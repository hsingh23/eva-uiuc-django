# Architectural diary — eva-uiuc-django

A narrative history of how this codebase came to look the way it does,
reconstructed in September 2026 from the twelve original commits (whose
messages were, at the time, mostly the word "changes"). Commit hashes
reference the current (message-rewritten) history.

## The project in one paragraph

In summer 2012, Harsh Singh (UIUC student) was building "EVA UIUC", a
course-schedule explorer for the University of Illinois. The visible product
was a JavaScript frontend hosted separately (st3.herokuapp.com /
scheedule.com); this repository is the backend half — a Django 1.4 service
that scrapes the university's public CISAPI XML catalog into MySQL and
exposes JSON/JSONP autocomplete endpoints for the frontend.

## Timeline

### Phase 1 — skeleton and scraper (2012-07-22, `7bc463c`)

The very first commit landed an entire working project: Django settings,
URLs, WSGI, a Heroku `Procfile`, and `eva_uiuc_app` with a full seven-model
schema (`Subject`, `Course`, `Section`, `Instructor`, `Location`,
`GenEdCategory`, `GenEdAttribute`). It also shipped a threaded scraper
management command walking years → terms → subjects on
`courses.illinois.edu/cisapp/explorer/schedule.xml`, plus dev detritus
(Sublime files, a SQLite `eva_db`, scratch scripts). The original message
was "stuff is looking good boys and girls".

### Phase 2 — frontend assets arrive, then find their home (2012-07-22, `c51ab2f` → `8035e16` → `6cc4ac4`)

A second commit ("balls") added Bootstrap 2, jQuery, fancybox, glyphicons,
base/404/500 templates, and help-page JS at the repo root. Within minutes
(the same day) the assets were duplicated *into* `eva_uiuc_app/static/` and
`eva_uiuc_app/templates/` so Django's app finders would resolve them, and
the root-level copies were then deleted ("heroku"). Net effect: static and
templates live inside the app package.

### Phase 3 — the API becomes the product (2012-09-03, `10bc1f3`)

After a six-week gap, work shifted to what actually mattered: JSON endpoints
(`/course-info/`, `/course-title/`, `/course-code/`, `/test/`, `/test-a/`)
with JSONP callback validation (a carefully lifted `is_valid_javascript_identifier`
implementation), a `find.html` page, and `wadofstuff-django-serializers` for
nested-relation JSON. A refactored scraper (`update.py`, function-per-entity)
was started but left syntactically broken (empty
`get_create_gened_category` body).

### Phase 4 — scraper hardening (2012-09-03, `0677d7a`, `79b87f9`, `97bdda6`)

Rapid iteration on the real scraper (`better_threading_example.py`): guard
missing `genEdCategories`, a one-line `remake_db.sh`, and a notable refactor
that deleted the dedicated geocoding thread in favor of inline Google Maps
geocoding when a `Location` is created.

### Phase 5 — MySQL churn and the end (2012-09-07, `3665f82` → `b8645a8`)

A mixed commit fixed a real scraper bug (instructors were only attached to
the *last* section of each course due to indentation), rewrote `test_a` with
the `get_everything_interesting` helper, and switched production from
Heroku Postgres to remote MySQL on shared hosting. The remaining three
commits are hostname↔IP flip-flops for the MySQL host while diagnosing
connectivity — then development stopped. The repo sat dormant for 14 years
until this documentation pass.

## Decision index

| # | Decision | Commits |
|---|----------|---------|
| [001](decisions/001-scrape-cisapi-xml-with-thread-pools.md) | Scrape the UIUC CISAPI XML with queued thread pools | `7bc463c`, `10bc1f3`, `97bdda6`, `3665f82` |
| [002](decisions/002-single-app-flat-project-layout.md) | Flat project layout with one Django app | `7bc463c`, `8035e16`, `6cc4ac4` |
| [003](decisions/003-jsonp-search-api-for-remote-frontend.md) | Serve a remote frontend via JSON/JSONP endpoints | `10bc1f3`, `3665f82` |
| [004](decisions/004-heroku-web-with-remote-mysql.md) | Heroku/gunicorn web tier with remote shared-hosting MySQL | `7bc463c`, `3665f82`, `9c5bc76`, `8834a86`, `b8645a8` |
| [005](decisions/005-inline-geocoding.md) | Geocode building names inline instead of a worker thread | `97bdda6` |
| [006](decisions/006-static-assets-inside-the-app.md) | Keep static/templates inside `eva_uiuc_app` | `c51ab2f`, `8035e16`, `6cc4ac4` |

## What we'd do differently (hindsight)

- Never commit credentials (`settings.py` hardcoded MySQL creds and
  `SECRET_KEY`) — use env vars (the `PRODUCTION` toggle was already halfway
  there).
- Migrations instead of `syncdb` + shell-script DB drops.
- One scraper command instead of three divergent copies, two of which are
  broken.
- Real tests; the only test asserts `1 + 1 == 2`.
