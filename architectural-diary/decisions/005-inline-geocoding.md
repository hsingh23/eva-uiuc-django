# ADR 005 — Geocode building names inline instead of a worker thread

- Date: 2012-09-03
- Status: accepted (historical)
- Commits: `97bdda6`

## Context

`Section` meetings reference a `Location` (building name). To place
sections on a map, the project geocoded building names to lat/lng via the
Google Maps Geocoding HTTP API. The earlier scraper design gave geocoding
its own pipeline stage: a `GetLocation` thread draining a `geo_queue`
populated during section parsing — a third thread pool alongside fetchers
and parsers.

## Decision

Delete the geocoding thread and `geo_queue`. In
`get_create_section_info`, whenever a `Location` is newly created or found
without an address, call the Google Maps Geocode JSON endpoint inline
(`...?address=<BuildingName>,%20Urbana,%20Champaign,%20IL&sensor=false`),
store lat/lng on the row, and guard against empty `results` with an
IndexError fallback that leaves the address blank. All old geocoding code
was left in place as comments.

## Alternatives considered

- Keep the dedicated geocoding thread — rejected as extra moving parts:
  the queue rarely had parallelism worth exploiting because building names
  repeat heavily and `get_or_create` short-circuits after the first hit.
- Batch-geocode after the crawl — more code for no perceived benefit at
  2012 scale.
- Cache geocode results in a table keyed by name — effectively achieved
  for free by storing lat/lng on `Location` itself.

## Consequences

- Positive: one fewer thread class and queue; geocoding happens exactly
  once per unique building and never again on reruns; simpler mental
  model.
- Negative: a slow or rate-limited Google API now stalls the parser thread
  holding the DB transaction; the v2-style `sensor=false` endpoint is long
  dead, so this code is doubly historical.
- Demonstrates the project's pattern of refactoring by commenting code out
  rather than deleting it.
