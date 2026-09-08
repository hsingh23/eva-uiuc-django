# One-shot recreation prompt — eva-uiuc-django

Use this prompt to recreate this project from scratch (modernized where the
original is unreproducible, e.g. dead Google Maps v2 endpoint). Everything
needed is specified below.

---

**Goal:** Build "EVA UIUC", the backend for a course-schedule explorer for
the University of Illinois at Urbana-Champaign: a Django web service that
(1) scrapes the public UIUC course catalog (CISAPI XML explorer at
`courses.illinois.edu/cisapp/explorer/schedule.xml`) into a relational
database and (2) serves JSON/JSONP search endpoints used by a separately
hosted JavaScript frontend for autocomplete and section display.

**Stack (as built in 2012):** Python 2.7, Django 1.4, MySQL
(`MySQL-python`), BeautifulSoup 4 + lxml (XML mode), Google Maps Geocoding
HTTP API, gunicorn on Heroku (`Procfile`:
`web: gunicorn_django -b 0.0.0.0:$PORT -w 8`),
`wadofstuff-django-serializers` for nested-relation JSON, DatabaseCache
locally / memcacheify in production. (A modern recreation should use
Python 3, a current Django LTS, and `requests` — the design below stands.)

## Phase 1 — Project skeleton

1. Flat Django project at the repo root: `manage.py`, `settings.py`,
   `urls.py` (`ROOT_URLCONF = 'urls'`), `wsgi.py`; `DEBUG = True`; timezone
   `America/Chicago`; admin enabled.
2. One app, `eva_uiuc_app`, containing models, admin, views, templates,
   static, and management commands (decision: single-app flat layout).
3. `requirements.txt` with pinned dependencies; `Procfile` for Heroku.
4. Environment switching by a single boolean env var `PRODUCTION`
   (checked in `settings.py`): when true, `DEBUG=False`, external
   `STATIC_URL`, memcached cache, production database. **Read DB
   credentials and `SECRET_KEY` from environment variables — never
   hardcode them** (the original hardcoded them; treat that as the
   anti-requirement).

## Phase 2 — Data model (`eva_uiuc_app/models.py`)

camelCase field names mirroring the upstream XML tags. All relationships
below; every model registered in `admin.py`:

- `Subject`: `sid` (unique, indexed), `label`, `collegeCode`,
  `departmentCode`, `unitName`, `contactName`, `contactTitle`,
  `addressLine1/2`, `phoneNumber`, `webSiteURL`,
  `collegeDepartmentDescription`.
- `Course`: FK `subject`, `label` (indexed), `description`, `creditHours`
  (int), `votes` (int, default 0), `number` (int, indexed),
  `courseSectionInformation`, `sectionDegreeAttributes`,
  `classScheduleInformation`.
- `Section`: FK `course` (nullable), M2M `instructor` (Instructor,
  nullable), M2M `gened` (GenEdCategory, nullable), FK `location`
  (Location, nullable), `sectionNumber` (indexed), `statusCode`,
  `partOfTerm`, `term` (indexed, e.g. "Fall 2012"), `sectionStatusCode`,
  `enrollmentStatus`, `startDate`, `endDate` (datetimes, nullable),
  `calendarYear` (int, indexed), `code`, `section_type`, `roomNumber`,
  `daysOfTheWeek`.
- `Instructor`: `firstName`, `lastName`, `rating` (int, default 0),
  `course` (label of the course taught — denormalized on purpose).
- `Location`: `buildingName` (unique), `address`, `lat`/`lng` (decimal
  10,7, nullable, indexed).
- `GenEdCategory`: `category`, `description`, M2M `genEdAttribute`.
- `GenEdAttribute`: `ns2code` (unique), `ns2desc`.

Rebuild script `remake_db.sh`: pipe `drop database; create database;`
through `manage.py dbshell`, then `manage.py syncdb` (modern: `migrate`).
Create the cache table: `manage.py createcachetable jsonp_cache`.

## Phase 3 — Scraper management command

Command `better_threading_example` (keep the historical name or use
`scrape_catalog`):

1. Walk the explorer tree: `schedule.xml` → `calendarYear` (id ≥
   `least_year`) → `term` → `subject` → collect `<subject href +
   "?mode=cascade">` URLs (`get_all_cascade_urls`).
2. Two-stage thread pools: ~30 fetcher threads (`ThreadUrl`) pull URLs
   from an input `Queue` and push raw XML onto an output queue; ~40 parser
   threads (`DatamineThread`) parse and write. All threads daemonized;
   `queue.join()` at the end.
3. Fetch via `FancyURLopener` subclass with a rotating list of browser
   user agents; on IOError retry once after a random 1–3 s sleep.
4. Parsing helpers, one per entity: `get_create_subject_info(soup)`,
   `get_create_course_info(c, subject_id)`,
   `get_create_section_info(s, course_id)`,
   `get_create_teacher_info(i, course_label)`. All writes use
   `get_or_create` keyed on natural keys so reruns are idempotent.
5. Skip university-side "no courses found" pages by checking for an `id`
   attribute on the root element; log and continue on DB errors.
6. **Geocode inline** (no dedicated thread): when a `Location` is created
   or lacks an address, call the Google Maps Geocoding JSON endpoint with
   `<buildingName>, Urbana, Champaign, IL`, store first-result lat/lng,
   fall back to blank on empty results.
7. Attach instructors **inside the section loop** (a historical bug
   attached them only to the last section of each course — do not repeat
   it). Guard courses with no `genEdCategories`. Module-level `DEBUG`
   flag: when true, scrape a single hard-coded CS Fall 2011 URL instead of
   the whole tree.

## Phase 4 — Search API (`eva_uiuc_app/views.py`, `urls.py`)

All endpoints GET, return `application/json`, strip quotes from `q`, 400
when `q` missing/empty; optional `?callback=` wraps the payload as JSONP
after validating the callback with a full ECMAScript identifier validator
(`is_valid_javascript_identifier` → `is_valid_jsonp_callback_value`):
reject reserved words, non-identifier characters, bad `\u` escapes, and
anything but dotted member access with `[n]` indexing. **Define the
`callback` variable from `request.GET` before using it** (the original
shipped a NameError in these branches).

- `/course-info/?q=` — combined autocomplete payload with keys
  `course_codes` (via `course_code_helper(q, 5)`), `course_titles` (10
  `Course.label` icontains matches), `teachers` (10
  `Instructor.lastName` icontains matches, objects `{name, course}`,
  ordered by lastName).
- `/course-code/?q=` — `course_code_helper(q)` (default limit 15): single
  token → `Subject.sid` icontains matches as `{code, name}`; two tokens
  `"SUBJ 2xx"` → `Course` matches on `subject__sid` + `number` contains,
  as `{code: "SID 123", name: label}`.
- `/course-title/?q=` — list of matching `Course.label` values.
- `/test/`, `/test-a/` — dev endpoints: Django-serializer JSON of the
  first matching section; and `get_everything_interesting(section)` JSON
  for up to 10 "Fall 2012" sections, with dict keys `section`,
  `instructor`, `location`, `subject`, `course`, each a list of fields,
  tolerating missing instructor/location (`["Unknown"]`).

Cache responses (2-day timeout) — catalog data changes rarely. A
module-level `POSTGRES` flag gates a `.distinct('label')` variant of the
titles query (Postgres-only).

## Phase 5 — Templates and static

- `base.html` (block structure: title, css, body_id, content_title,
  content, js), `404.html`, `500.html`, and a `find.html` search page.
- Bootstrap 2 + jQuery assets served from `eva_uiuc_app/static/`
  (app-level discovery via `AppDirectoriesFinder`; no root-level copies).

## Acceptance criteria

1. `manage.py migrate && manage.py createcachetable jsonp_cache` then
   `manage.py runserver` starts cleanly.
2. Running the scraper twice populates identical row counts (idempotent
   `get_or_create`; spot-check Subject/Course/Section counts > 0 and
   instructors attached to *every* section).
3. `GET /course-code/?q=CS` returns JSON subject matches; `?q=CS 2`
   returns `{code, name}` course matches.
4. `GET /course-info/?q=prog` returns `course_codes`, `course_titles`,
   `teachers` keys, each ≤ their limits.
5. `GET /course-title/?q=intro` returns a JSON array of labels.
6. Missing `q` returns HTTP 400 on all three endpoints.
7. `?callback=validName` returns `validName({...});` with
   `application/json`; `?callback=alert;evil` is rejected by the
   validator.
8. Every unique building in sections has exactly one `Location` row with
   lat/lng after the first geocode-enabled run, and no additional geocode
   calls on rerun.
9. No credential values anywhere in the repo — only env var names
   (`PRODUCTION`, `PORT`, `DJANGO_SETTINGS_MODULE`, plus DB/secret vars).
10. Django admin at `/admin/` lists all seven models.

## Known pitfalls to avoid (from the original's history)

- Broken duplicate commands: the original's `scraper.py` imported from a
  nonexistent `evauiuc.models` module and `update.py` had an empty
  function body (SyntaxError). Ship exactly one working command.
- The JSONP NameError described in Phase 4.
- Silencing settings errors with `try/except: pass`.
- Committing dev databases, editor workspaces, and scratch files.
