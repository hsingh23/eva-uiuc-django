# AGENTS.md — working guide for coding agents

This is an **archived Python 2 / Django 1.4 (2012)** project. It cannot run
on a modern Python without a compatibility layer. Treat it as read-mostly:
the realistic tasks are documentation, archaeology, and (if ever revived) a
full framework migration.

## Commands (as the project was designed)

```bash
pip install -r requirements.txt        # Python 2.7 virtualenv only
python manage.py syncdb                # create schema (Django 1.4, pre-migrations)
python manage.py createcachetable jsonp_cache   # required by CACHES DatabaseCache
python manage.py runserver             # dev server
python manage.py dbshell               # mysql shell
./remake_db.sh                         # drop/create DB + syncdb
python manage.py better_threading_example   # the only runnable scraper command
python manage.py test                  # runs the stub test in eva_uiuc_app/tests.py
```

Deployment: Heroku with `Procfile` (`web: gunicorn_django -b 0.0.0.0:$PORT -w 8`),
`PRODUCTION=True` env var for production settings.

## Architecture map

```
UIUC CISAPI (courses.illinois.edu XML explorer)
        │  threaded scrape (fetch queue → parse queue)
        ▼
management/commands/better_threading_example.py
        │  get_or_create rows
        ▼
MySQL ── models: Subject → Course → Section ─┬─ Instructor (M2M)
                                              ├─ GenEdCategory (M2M) → GenEdAttribute
                                              └─ Location (geocoded inline)
        ▼
views.py: course_info / course_title / course_code (+ test, test_a)
        │  json.dumps, optional JSONP ?callback=
        ▼
Remote frontend (2012: st3.herokuapp.com / scheedule.com)
```

- Project config lives at the repo root (`settings.py`, `urls.py`,
  `wsgi.py`, `manage.py`) — not in a package. `ROOT_URLCONF = 'urls'`.
- Everything functional lives in the single app `eva_uiuc_app`.
- `settings.py` has a `PRODUCTION == 'True'` block that flips DEBUG off,
  swaps the cache to `memcacheify`, and points at the remote MySQL host.

## Conventions (2012 codebase)

- Python 2: print statements, `unicode`/`unichr`, `Queue` module,
  `urllib.FancyURLopener` with rotating user-agent strings.
- camelCase field names on models (e.g. `sectionNumber`, `daysOfTheWeek`),
  mirroring the upstream XML tag names.
- Scraper idempotency via `Model.objects.get_or_create(...)` keyed on
  natural keys, `defaults={...}` for the remaining attributes.
- Views return raw `HttpResponse(json.dumps(...), content_type='application/json')`;
  no Django REST framework, no class-based views, no forms.

## Gotchas

1. **Two of the three scraper commands are broken.**
   `scraper.py` imports `from evauiuc.models import *` (wrong module path —
   should be `eva_uiuc_app.models`) and `update.py` has a function
   `def get_create_gened_category(gc):` with an empty body (SyntaxError).
   Only `better_threading_example` actually runs.
2. **JSONP paths reference an undefined `callback`.** In `views.py`, the
   `if ("callback" in request.GET)` branches call
   `is_valid_jsonp_callback_value(callback)` but `callback` is never
   assigned → NameError whenever a `?callback=` param is supplied.
3. **`wsgi.py` sets `DJANGO_SETTINGS_MODULE` to `eva.settings`**, which does
   not exist (settings live at repo root). Heroku's `gunicorn_django`
   didn't use this file, so it was never noticed.
4. **Secrets are committed.** `settings.py` contains hardcoded MySQL
   credentials and `SECRET_KEY` (2012-era, defunct). Never copy these into
   new files or docs; names only.
5. **`POSTGRES` flag in `views.py`** (module-level `False`) gates a
   `.distinct('label')` query that only works on Postgres; MySQL runs the
   plain path. The `PRODUCTION` flag read in `views.py` is unused.
6. **Caching requires a DB table.** `CACHES` uses `DatabaseCache` at
   location `jsonp_cache`; without `createcachetable` every cache op fails.
7. **Scraper "DEBUG" mode.** `better_threading_example` has a module-level
   `DEBUG = True`; the command scrapes a single hard-coded CS Fall 2011 URL
   unless you flip it to run the full crawl (30 fetch threads + 40 parse
   threads).
8. **Scratch files are tracked**: `a` (SQL drop script), `eva_db` (SQLite
   binary), `a.xml`/`subject.xml` (fixtures), `try.py` (threading playground),
   `eva.sublime-*` (editor files). Do not treat them as load-bearing.
9. **Gen-ed scraping is commented out** in the scraper; the `GenEd*` models
   exist and are admin-registered but were never populated.
10. **`Section` uses `to_field='id'` FKs** and there is an instructor-loop
    indentation fix history — older scraper variants attached instructors
    only to the last section of each course.

## Verifying changes

- There is no CI. The only test is a stub (`tests.py` asserts 1+1 == 2).
- For docs-only changes: verify claims against
  `git show <sha>` and the files themselves; check that no secret *values*
  appear (`grep -riE '(password|secret|token|key)\s*[:=]' *.md`).
- For (hypothetical) code changes: `python manage.py test` under Python 2.7,
  then `python manage.py runserver` and hit `/course-code/?q=CS`,
  `/course-title/?q=programming`, `/course-info/?q=CS`.

## Pointers

- Per-commit history: `CHANGELOG.md`.
- Design decisions and their context: `architectural-diary/`
  (start at `architectural-diary/main.md`).
- One-shot recreation spec: `prompt.md`.
