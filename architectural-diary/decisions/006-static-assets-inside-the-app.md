# ADR 006 — Keep static assets and templates inside `eva_uiuc_app`

- Date: 2012-07-22
- Status: accepted (historical)
- Commits: `c51ab2f`, `8035e16`, `6cc4ac4`

## Context

Frontend assets (Bootstrap 2, jQuery, glyphicons, help-page JS) and
templates (`base.html`, `find.html`, 404/500) were first added at the repo
root — the instinct of someone used to plain PHP/static hosting. Django
1.4's `django.contrib.staticfiles` `AppDirectoriesFinder` and the
`app_directories` template loader, however, automatically discover
`<app>/static/` and `<app>/templates/` with zero settings, which matters
on Heroku where `collectstatic` runs during slug compilation.

## Decision

Duplicate every asset and template into `eva_uiuc_app/static/` and
`eva_uiuc_app/templates/` (`8035e16`), then delete the root-level
`static/` and `templates/` directories in the immediately following commit
(`6cc4ac4`). `STATIC_ROOT`/`STATIC_URL` settings and the app finders do
the rest; `TEMPLATE_DIRS` was also pointed at the app templates directory
explicitly.

## Alternatives considered

- Keep root-level assets and configure `STATICFILES_DIRS` — equally valid;
  would have avoided committing 27 files twice for a few minutes.
- A top-level `assets/` or `frontend/` package — nonstandard for the era.

## Consequences

- Positive: zero-config discovery by both the dev server and Heroku's
  collectstatic; assets version with the app.
- Negative: a full duplicate of the asset tree existed in history between
  `8035e16` and `6cc4ac4` (irrelevant now, confusing then); because the
  real frontend lived on another domain, most of these assets (help-page
  JS, fancybox, quickselect) were trimmed in `10bc1f3` as dead weight.
- The final `find.html` still references CSS/JS from
  `st3.herokuapp.com`, confirming the local assets were mostly unused.
