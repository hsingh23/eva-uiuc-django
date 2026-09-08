# ADR 004 — Heroku/gunicorn web tier with remote shared-hosting MySQL

- Date: 2012-07-22 → 2012-09-07
- Status: accepted (historical), reversed twice, ultimately superseded by abandonment
- Commits: `7bc463c`, `3665f82`, `9c5bc76`, `8834a86`, `b8645a8`

## Context

The app needed free hosting in 2012. Heroku's free dyno was the natural web
tier (`Procfile`: `web: gunicorn_django -b 0.0.0.0:$PORT -w 8`). Heroku
Postgres existed (and `dj-database-url` was even pinned in
requirements.txt), but the developer also had cheap shared hosting
(Namecheap-style) with MySQL included, and MySQL was the familiar stack
(`MySQL-python` pinned from the first commit).

## Decision

- Web tier: Heroku + gunicorn (`gunicorn_django`, 8 workers).
- Data tier: MySQL on remote shared hosting, credentials hardcoded in
  `settings.py` (defunct; values are not reproduced in this diary).
- Environment switching via a single `PRODUCTION` env var checked inside
  `settings.py`: flips `DEBUG` off, points `STATIC_URL` at an external
  static host, swaps the cache from DatabaseCache to memcached
  (`memcacheify`), and selects the production `DATABASES` block.
- The dev default `DATABASES` also pointed at the remote MySQL by the final
  commit, making local dev dependent on the remote box.

The last three commits (`9c5bc76`, `8834a86`, `b8645a8`) are a single-day
hostname↔IP flip-flop for the MySQL `HOST` while diagnosing connectivity
from Heroku (DNS resolution on shared hosting was flaky).

## Alternatives considered

- **Heroku Postgres** — genuinely attempted: `dj-database-url` +
  `psycopg2` were pinned and a commented `dj_database_url.config()` block
  survives in settings; abandoned in `3665f82` in favor of MySQL.
- **SQLite everywhere** — fine for dev (`eva_db`) but not for a shared
  Heroku dyno filesystem.

## Consequences

- Positive: free deployment end-to-end; memcacheify made the production
  cache a one-liner.
- Negative: hardcoded credentials in git (defunct but a permanent record);
  cross-datacenter latency between Heroku (AWS us-east) and shared-hosting
  MySQL made queries slow and connections flaky — the likely root cause of
  the host flip-flopping; `views.py` kept an unused `POSTGRES` flag
  commemorating the abandoned Postgres path.
- The production settings block sits inside a bare `try/except: pass`,
  so *any* settings error silently falls back to dev defaults.
