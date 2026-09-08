# ADR 001 — Scrape the UIUC CISAPI XML with queued thread pools

- Date: 2012-07-22 → 2012-09-07
- Status: accepted (historical)
- Commits: `7bc463c`, `10bc1f3`, `97bdda6`, `3665f82`

## Context

The University of Illinois published its course catalog through the CISAPI
XML explorer at `courses.illinois.edu/cisapp/explorer/schedule.xml`, a tree
of calendar years → terms → subjects → cascading courses → detailed
sections (`?mode=cascade`). There was no bulk download and no JSON API; the
data could only be obtained by crawling many small XML documents (one per
subject per term). The catalog needed to be mirrored into our own database
so search endpoints could answer quickly.

## Decision

Use BeautifulSoup ("xml" mode via lxml) over `urllib.FancyURLopener` with a
rotating list of browser user agents, driven by a two-stage threaded
pipeline:

1. Discover all subject cascade URLs by walking the year/term/subject tree
   (`get_all_cascade_urls`).
2. Feed those URLs into a `Queue.Queue` consumed by ~30 fetcher threads
   (`ThreadUrl`) that push raw XML chunks onto an output queue consumed by
   ~40 parser threads (`DatamineThread`) that write rows with
   `get_or_create` (keyed on natural keys: sid/label/number/term/section
   number) so reruns are idempotent.

Errors are handled opportunistically: retry once after a random 1–3 s
sleep; university-side "no courses found" pages are detected by the absence
of an `id` on the root element and skipped; database exceptions are logged
and the thread moves on.

## Alternatives considered

- **Single-threaded crawl** — rejected: with thousands of XML documents and
  2012 network latency, a serial crawl would take hours.
- **Official API / data dump** — none existed at the time.
- **`scraper.py` (earlier design in `7bc463c`)**: 100 worker threads each
  doing fetch *and* parse inline. Superseded by the two-queue design in
  `better_threading_example.py`, which decouples I/O from parsing and
  survives university-side error pages better.
- **`update.py` (`10bc1f3`)**: an attempted function-per-entity refactor
  with logging; abandoned mid-write (empty function body = SyntaxError).

## Consequences

- Positive: the crawl is fast, reruns are safe (get_or_create), and flaky
  pages don't kill the run.
- Negative: 70 daemon threads against Django 1.4's MySQL driver caused the
  intermittent "database freaks out and dies" IntegrityErrors the comments
  complain about; connection pooling was never addressed.
- The command name `better_threading_example` betrays its origin as a
  copied tutorial file (`try.py`, the original threading playground, is
  still tracked).
- Hardcoded `DEBUG = True` in the module means a fresh clone only scrapes
  one CS Fall 2011 URL unless edited.
