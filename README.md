# eva-uiuc-django

**Status: archived / legacy.** This is a 2012-era project kept for historical
interest. It targets Python 2 and Django 1.4 and will not run unmodified on a
modern toolchain. Do not deploy it as-is (see "Security warning" below).

## What it is

EVA UIUC ("Explore. Venture. Adventure." / "time well spent") is the backend
half of a course-schedule explorer for the University of Illinois at
Urbana-Champaign. It is a Django application that:

1. **Scrapes** the public UIUC course catalog (the `courses.illinois.edu`
   CISAPI XML explorer) with a multithreaded management command, resolving
   years → terms → subjects → cascading courses → detailed sections.
2. **Stores** subjects, courses, sections, instructors, meeting locations
   (with Google Maps geocoding), and gen-ed categories in a MySQL database.
3. **Serves** JSON/JSONP search endpoints consumed by a separately hosted
   frontend (at the time: `st3.herokuapp.com` / scheedule.com), including
   autocomplete-style queries by course code, course title, and instructor
   name.

## Features

- Threaded scraper (`better_threading_example` management command): fetch
  queue + parse queue with worker pools, rotating user agents, retry with
  backoff, and inline geocoding of building names.
- Read-only search API with JSONP support and strict callback-name
  validation (`is_valid_jsonp_callback_value`).
- Django admin registered for all seven models.
- Heroku deployment via `Procfile` (gunicorn) with a `PRODUCTION` env toggle
  that switches settings (debug off, memcached via `memcacheify`, remote
  MySQL).
- Bootstrap 2 static assets and base/404/500 templates for the (mostly
  vestigial) server-rendered pages.

## Stack

| Layer     | Technology |
|-----------|------------|
| Language  | Python 2.7 (print statements, `Queue`, `urllib.FancyURLopener`) |
| Framework | Django 1.4 |
| Database  | MySQL (`MySQL-python`), SQLite dev DB committed as `eva_db` |
| Parsing   | beautifulsoup4 + lxml ("xml" mode) |
| Geocoding | Google Maps Geocoding API v2-style HTTP endpoint |
| Serving   | gunicorn (`gunicorn_django`), Heroku `Procfile` |
| Caching   | Django `DatabaseCache` (`jsonp_cache` table) locally; memcached (via `memcacheify`) in production |
| Serializers | `wadofstuff-django-serializers` for nested-relation JSON |

## Quickstart (as designed in 2012)

```bash
pip install -r requirements.txt          # Python 2.7 environment required
# configure MySQL credentials in settings.py (see warning below)
python manage.py syncdb                  # create schema
python manage.py createcachetable jsonp_cache
python manage.py runserver               # dev server on :8000
python manage.py better_threading_example  # DEBUG mode scrapes one subject (CS Fall 2011)
```

Rebuild the database from scratch: `./remake_db.sh`
(drops/creates the DB via `manage.py dbshell`, then `syncdb`).

Deploy (2012-style Heroku): `git push heroku master` with the `Procfile`
(`web: gunicorn_django -b 0.0.0.0:$PORT -w 8`) and `PRODUCTION=True` set.

### Environment variable names

- `PRODUCTION` — set to `True` to enable production settings (disables
  DEBUG, switches cache to memcacheify, uses remote MySQL).
- `PORT` — bind port for gunicorn on Heroku.
- `DJANGO_SETTINGS_MODULE` — defaults to `settings` (repo root) via
  `manage.py`; note `wsgi.py` incorrectly defaults to `eva.settings`.

No secret values are documented here; see the security warning.

## Security warning

`settings.py` in this archived repo contains **hardcoded database
credentials and a Django `SECRET_KEY` committed to git history** from the
original 2012 development. These are long-defunct, but the pattern is the
reason this repo should never be revived without first moving all secrets to
environment variables. GitHub's Dependabot also reports dozens of known
vulnerabilities in the pinned 2012 dependencies.

## Repository structure

```
.
├── manage.py, settings.py, urls.py, wsgi.py   # Django project (repo root)
├── Procfile, requirements.txt, remake_db.sh   # deploy + deps + DB rebuild
├── eva_db                                     # committed SQLite dev database
├── a                                          # scratch SQL drop-tables script
├── eva_uiuc_app/
│   ├── models.py                              # Subject, Course, Section, Instructor,
│   │                                          # Location, GenEdCategory, GenEdAttribute
│   ├── views.py                               # JSON/JSONP search endpoints
│   ├── admin.py, tests.py                     # admin for all models; stub tests
│   ├── static/                                # Bootstrap 2, glyphicons
│   ├── templates/                             # base.html, find.html, 404, 500
│   └── management/commands/
│       ├── better_threading_example.py        # the working threaded scraper
│       ├── scraper.py                         # earlier scraper (broken import)
│       ├── update.py                          # refactor attempt (syntax error)
│       └── try.py, a.xml, subject.xml         # scratch/fixture files
└── architectural-diary/, AGENTS.md, CHANGELOG.md, prompt.md   # added 2026 docs
```

## Further reading

- `CHANGELOG.md` — every commit, newest first.
- `AGENTS.md` — commands, architecture map, and gotchas for agents.
- `architectural-diary/` — decision records and history narrative.
- `prompt.md` — one-shot prompt to recreate this project from scratch.
