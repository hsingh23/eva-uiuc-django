# ADR 002 — Flat project layout with one Django app

- Date: 2012-07-22
- Status: accepted (historical)
- Commits: `7bc463c`, `8035e16`, `6cc4ac4`

## Context

`django-admin.py startproject` in the Django 1.3/1.4 era produced a layout
with `manage.py` plus either a project package or (in the older flat style)
`settings.py`/`urls.py`/`wsgi.py` at the repository root. The developer
used the flat style. The domain was small and single-purpose: mirror the
catalog and serve searches.

## Decision

Keep the project configuration flat at the repo root (`settings.py`,
`urls.py`, `wsgi.py`, `manage.py`, `ROOT_URLCONF = 'urls'`) and put all
domain logic in exactly one app, `eva_uiuc_app`: models, admin, views,
templates, static files, and management commands all live in that package.

## Alternatives considered

- A project package (`eva/`) containing settings — partially attempted:
  `wsgi.py` defaults `DJANGO_SETTINGS_MODULE` to `eva.settings`, a leftover
  that never matched reality and breaks if `wsgi.py` is ever used directly.
- Multiple apps (`catalog`, `search`, `geo`) — overkill for seven models
  and five views.

## Consequences

- Positive: trivial mental model; everything findable in two directories;
  Heroku's `manage.py`/gunicorn integration worked with zero configuration.
- Negative: root-level clutter (`a`, `eva_db`, Sublime files sit next to
  `settings.py`); the name `eva_uiuc_app` is redundant; there is no
  separation between the scraping subsystem and the serving subsystem, so
  three scraper variants accumulated side by side in `management/commands/`.
- The committed SQLite database (`eva_db`) at the root was a dev-time
  convenience that would now be considered an anti-pattern.
