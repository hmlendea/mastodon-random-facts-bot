# Architecture

This document complements the root [ARCHITECTURE.md](../ARCHITECTURE.md). It does not repeat the system context, component catalogue, or runtime process defined there. Instead, it elaborates the architectural reasoning that a future agent needs in order to modify the pipeline safely: why the decomposition is shaped the way it is, where the real boundaries lie, and which properties the design deliberately preserves.

## Architectural narrative

The bot is a scheduled batch pipeline, not a service. That single fact explains most of its shape. There is no long-lived process, so there is no in-process state to protect, no connection pool to manage, and no graceful shutdown path. Each invocation is a complete, independent transaction: read configuration, select one fact, enrich it, publish it, exit. The scheduler owns periodicity; the bot owns exactly one posting cycle.

The pipeline is strictly sequential. Media downloads and uploads happen one at a time inside a loop. This is a deliberate simplicity trade-off: the bot posts at most one status per invocation, the media set per fact is small, and the documented `systemd` unit bounds each run to 60 seconds. Parallelism would add failure modes (partial upload sets, ordering hazards) without materially improving throughput at this scale.

## Why the decomposition is entry point plus two hooks

The repository separates three concerns that change for different reasons:

1. **Orchestration and integration** (`mastodon-random-facts-bot.py`) changes when the Mastodon API, the media handling strategy, or the pipeline order changes. It is maintained by the project.
2. **Text transformation** (`text_replacements.py`) changes when the operator wants locale-specific rewrites. It is maintained by the operator.
3. **Dynamic tag derivation** (`dynamic_tags.py`) changes when the operator wants content-derived hashtags. It is maintained by the operator.

The two hook modules are the operator-facing extension surface. They are imported directly by the entry point; there is no plugin registry, no discovery mechanism, and no configuration file. The contract is the function signature and return type, documented in [Components: text replacements](./components/text-replacements.md) and [Components: dynamic tags](./components/dynamic-tags.md).

This decomposition means an operator can customise posting behaviour without touching orchestration code, and the project can evolve orchestration without breaking operator customisations, provided the hook signatures remain stable.

## Real boundaries

- **Process boundary.** The bot is one operating-system process launched by a scheduler. Everything inside is sequential; everything outside (scheduler, Mastodon instance, media hosts) is asynchronous relative to it.
- **Trust boundary.** The operator's host and credentials are trusted. Fact file content is trusted operator input. Media URLs embedded in facts are trusted by construction: their bytes are downloaded into memory and forwarded to Mastodon without content validation beyond the response `content-type` header. The Mastodon instance and media hosts are untrusted network peers whose failures terminate the run.
- **State boundary.** The only persistent local state is the application secret file. The facts file is operator-owned and read-only to the bot. Published statuses and uploaded media become state owned by the Mastodon instance; the bot retains no local record of what it published.
- **Module boundary.** The helper modules depend only on the Python standard library. They perform no I/O, hold no state, and import nothing from the entry point. This keeps them safe to edit in place and trivial to reason about.

## Causal model of a posting cycle

The pipeline preserves one invariant: **a status is published only when the complete pipeline succeeds**. The causal chain is:

```
arguments parsed
  -> secret file present? (create app if absent)
  -> Mastodon client constructed
  -> facts file read
  -> one fact chosen
  -> media URLs extracted
  -> each URL downloaded then uploaded (any failure aborts)
  -> text transformed
  -> tags assembled and filtered
  -> status posted
```

Each arrow is a hard dependency. A failure at any stage prevents publication. There is no partial post, no post without media, and no post with a stale fact. The consequence is that transient failures (network blip, Mastodon rate limit, media host downtime) simply defer posting to the next scheduled invocation. The bot never retries within a run and never publishes a degraded fact.

## What the design deliberately excludes

- **No database.** The facts file is the database. This keeps the operator's mental model flat and the deployment trivial.
- **No configuration file.** All configuration arrives as command-line arguments. This makes the invocation self-describing in scheduler logs and avoids a second file to manage.
- **No daemon.** Scheduling is externalised. This avoids process supervision concerns inside the bot.
- **No retry or backoff.** Retrying a status post risks duplicate publication, which is worse than a missed cycle. The scheduler's next activation is the retry.
- **No deduplication of facts.** `random.choice` may select the same fact on consecutive runs. The bot does not track posting history because it retains no state between runs.

## Consequences for modification

- Adding a new pipeline stage means editing the entry point and deciding where in the causal chain it belongs; stages after media upload but before `status_post` affect the published body.
- Adding a new media type means editing the suffix condition in the entry point; see [Compatibility contracts](../ARCHITECTURE.md#-compatibility-contracts).
- Adding a new configuration input means adding a positional argument, which is a compatibility-breaking change for every existing scheduler invocation; see [Configuration](./configuration.md).
- Adding a new external integration means adding a new outbound boundary in the entry point; helper modules must remain I/O-free.

## Relationship to root documentation

The root [ARCHITECTURE.md](../ARCHITECTURE.md) defines the canonical component catalogue, diagrams, data architecture, interfaces, dependency direction, deployment, compatibility contracts, testing, constraints, extension points, and source map. This document adds the reasoning layer: why the boundaries are where they are and what invariants they protect. Where the two documents overlap, the root document is authoritative for structure and this document is authoritative for rationale.
