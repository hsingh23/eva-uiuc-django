# Changelog

All notable changes to the eva-uiuc-django project.

> Note: hashes below reference the current (message-rewritten) history. In
> September 2026 the original one-word commit messages ("changes", "balls",
> "heroku", etc.) were rewritten into conventional-commit form; tree contents
> and authorship are unchanged.

## 2012-09-07 · b8645a8 · chore(settings): point default and prod databases at remote MySQL

- Replaced the local MySQL `DATABASES` config (kept as a comment) with the remote shared-hosting MySQL database in `settings.py`.
- Set the production settings block's `HOST` to the server IP instead of the hosting hostname.
- Both default and production configurations now target the same remote database.

## 2012-09-07 · 8834a86 · chore(settings): use Namecheap hostname for MySQL host

- Pointed the MySQL `HOST` setting at the hosting provider's canonical database server hostname instead of the raw IP address.
- No other files touched.

## 2012-09-07 · 9c5bc76 · chore(settings): use IP address for MySQL host

- Replaced the shared-hosting hostname with the server's raw IP address as the MySQL `HOST` in the production settings block.
- Part of a same-day hostname/IP flip-flop while diagnosing database connectivity.

## 2012-09-07 · 3665f82 · fix(scraper): process instructors per section, point app at MySQL

- Fixed an indentation bug in `better_threading_example.py` so instructors are associated with every section of a course rather than only the last one.
- Skipped redundant saves for already-existing subjects/courses.
- Rewrote the `test_a` view around a new `get_everything_interesting` helper that tolerates missing instructor/location data and returns up to 10 Fall 2012 sections.
- Replaced `dj_database_url`/Postgres in settings with a remote MySQL config (credentials hardcoded) and dropped `least_year` to 2012.

## 2012-09-03 · 97bdda6 · refactor(scraper): geocode locations inline during section scraping

- Removed the dedicated `GetLocation` worker thread and `geo_queue` from the scraper.
- Geocoding via the Google Maps API now happens inline in `get_create_section_info` whenever a `Location` is created or lacks an address, with a guard against empty geocode results.
- Bumped `least_year` to 2013 and removed a leftover debug print.

## 2012-09-03 · 79b87f9 · chore(scripts): simplify remake_db.sh to dbshell plus syncdb

- Replaced the interactive mysql password prompt in `remake_db.sh` with a pipe of DROP/CREATE DATABASE statements through `manage.py dbshell`.
- Runs `manage.py syncdb` afterwards to rebuild the schema.

## 2012-09-03 · 0677d7a · fix(scraper): skip missing genEdCategories in threading example

- Guarded the `genEdCategories` lookup so courses without gen-ed data no longer raise `AttributeError`.
- Removed leftover "done getting/doing section/instructor" debug prints from the parse loop in `better_threading_example.py`.

## 2012-09-03 · 10bc1f3 · feat(api): add JSON/JSONP course search API and update scraper

- Implemented `course_info`, `course_title`, and `course_code` views with JSONP callback validation and wired them into `urls.py` (`/course-info/`, `/course-title/`, `/course-code/`, plus `/test/` and `/test-a/`).
- Added the `find.html` template and the `wadofstuff-django-serializers` dependency (`SERIALIZATION_MODULES` setting) for nested-relation JSON.
- Added a refactored `update.py` scraper management command (function-based, with logging) alongside the original `scraper.py`.
- Relaxed `Instructor`/`Course` model fields, trimmed unused static assets (fancybox, quickselect, help-page JS), and added DB-rebuild scratch scripts (`a`, `remake_db.sh`, `a.xml`).

## 2012-07-22 · 6cc4ac4 · chore(assets): drop root-level static/templates for app copies

- Removed the duplicate root-level `static/` and `templates/` directories (27 files) now that everything lives under `eva_uiuc_app/static/` and `eva_uiuc_app/templates/`.
- Static files and templates are resolved solely via Django's app-level finders/loaders.

## 2012-07-22 · 8035e16 · chore(assets): copy static assets and templates into eva_uiuc_app

- Duplicated the Bootstrap/jQuery assets, images, and base/404/500 templates from the repo root into `eva_uiuc_app/static/` and `eva_uiuc_app/templates/`.
- App-level copies resolve via Django's app static finders and template loaders; root-level copies were still left in place at this commit.

## 2012-07-22 · c51ab2f · feat(assets): add Bootstrap/jQuery assets, base templates, help JS

- Added the frontend foundation: Twitter Bootstrap CSS/JS (responsive and minified variants), jQuery with fancybox and mousewheel plugins, quickselect CSS, glyphicons, favicon, and UIUC logo.
- Introduced `base.html` plus 404 and 500 error page templates.
- Added `help_page`/`help_maker` JS carried over from a prior project, and `MySQL-python`/`pytz` to requirements.

## 2012-07-22 · 7bc463c · feat(app): bootstrap Django project with UIUC catalog scraper

- Initial import: Django project skeleton (`settings.py`, `urls.py`, `wsgi.py`, `manage.py`, Heroku `Procfile`, `requirements.txt`).
- Created `eva_uiuc_app` with models for `Subject`, `Course`, `Section`, `Instructor`, `Location`, `GenEdCategory`, and `GenEdAttribute`.
- Added a threaded scraper management command that walks the courses.illinois.edu CISAPI XML explorer and populates the database via `get_or_create`.
- Also committed Sublime editor files, a SQLite dev database (`eva_db`), and scratch threading/example scripts.
