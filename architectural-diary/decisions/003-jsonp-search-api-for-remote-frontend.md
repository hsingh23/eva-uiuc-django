# ADR 003 — Serve a remote frontend via JSON/JSONP search endpoints

- Date: 2012-09-03
- Status: accepted (historical)
- Commits: `10bc1f3`, `3665f82`

## Context

The user-facing product was a JavaScript single-page app hosted on a
different domain (st3.herokuapp.com / scheedule.com). In 2012, browsers
blocked cross-origin `XMLHttpRequest` without CORS headers (CORS support
was still patchy), but `?callback=`-style JSONP worked everywhere. The
frontend needed autocomplete-style queries: as the user types, fetch
matching course codes, titles, and instructors.

## Decision

Expose simple GET endpoints returning `application/json`, with optional
JSONP wrapping when a `callback` parameter is present:

- `/course-info/?q=...` — combined payload: up to 5 course-code matches,
  10 course-title matches, 10 instructor (lastName) matches. Powers the
  main autocomplete.
- `/course-code/?q=...` — subject-code (single token) or
  `subject number` (two token) matches via `course_code_helper`.
- `/course-title/?q=...` — course labels by substring.
- `/test/`, `/test-a/` — development endpoints (Django-serializer dump;
  `get_everything_interesting` JSON for Fall 2012 sections).

Quotes are stripped from the query as a crude injection guard; POSTGRES
flag gates a `.distinct('label')` variant; responses are cached (DatabaseCache
table `jsonp_cache`, 2-day timeout) because catalog data changes rarely.
Callback names are validated by a full ECMAScript identifier validator
(`is_valid_javascript_identifier` / `is_valid_jsonp_callback_value`) to
prevent JSONP hijacking/reflection attacks.

## Alternatives considered

- Serve the frontend and API from the same origin — rejected: the frontend
  team deployed independently on Heroku free tier.
- Enable early CORS headers — impractical in 2012 browser landscape.
- Django REST framework / tastypie — both were young; raw `json.dumps` +
  `wadofstuff-django-serializers` (for nested relations) was the familiar
  path.

## Consequences

- Positive: worked cross-origin with zero frontend changes; the strict
  callback validation was ahead of its time; caching kept the tiny
  shared-hosting MySQL load low.
- Negative: the JSONP branches reference an undefined `callback` variable
  (NameError whenever `?callback=` is actually passed) — shipped broken and
  never noticed because the frontend apparently used plain JSON.
- The `find.html` template in this repo points at the *other* domain for
  its CSS/JS — evidence the Django templates were largely vestigial.
