# Concurrency and scheduling

This document describes the concurrency model, scheduling assumptions, and the consequences of running multiple bot instances.

## Concurrency model

The bot is **single-threaded, single-process, and non-reentrant**. It performs no internal concurrency:

- No threads, no asyncio, no multiprocessing.
- Media downloads and uploads are strictly sequential.
- The entire pipeline executes in one call stack.

The process holds no locks, creates no lock files, and performs no coordination with other processes.

## Scheduling

Scheduling is entirely external. The bot has no timer, no daemon mode, and no concept of intervals. The documented deployment uses a `systemd` timer:

```ini
[Timer]
OnBootSec=15min
OnUnitActiveSec=25min
```

This launches the bot approximately every 25 minutes after an initial 15-minute boot delay. The `RuntimeMaxSec=60` bound ensures a stuck run cannot block the next activation.

## Multiple instances

Running multiple bot processes concurrently is **not prevented and not coordinated**:

- Each process reads the same facts file independently.
- Each process may select the same fact.
- Each process uploads its own media and publishes its own status.
- The secret file is read-only after creation; concurrent reads are safe.
- Concurrent writes to the secret file (first run on a new instance) are a race condition: `Mastodon.create_app` may be called multiple times, creating multiple applications on the instance.

The operator must ensure the scheduler does not launch overlapping runs if deduplication or ordering matters. The `systemd` example uses `RuntimeMaxSec` and the default `AccuracySec=1min` to minimise overlap, but it does not guarantee serialisation.

## No in-process state

Because the bot retains no state between runs:

- There is no in-memory cache to invalidate.
- There is no connection pool to share.
- There is no rate-limit bucket to coordinate.

Each run is a clean slate. This makes horizontal scaling (multiple schedulers, multiple hosts) trivial from the bot's perspective, but it also means the operator must handle deduplication at the scheduler or content level if desired.

## Media host concurrency

Media downloads are sequential within a run. Across concurrent runs, multiple processes may download from the same media host simultaneously. The bot sets a Firefox user agent but does not implement politeness delays, rate limiting, or retry-after handling. A media host that rate-limits will cause failures in the affected runs.

## Mastodon instance concurrency

Multiple concurrent runs publish statuses independently. The Mastodon instance's own rate limits apply per access token. If the operator runs multiple bots with the same token, they share the instance's rate-limit bucket. The bot does not inspect rate-limit headers or back off.

## Failure isolation

A failure in one run (media download error, publication error, exception) has no effect on other runs. The process terminates; the scheduler launches the next run independently. There is no cascade failure mode.

## Modification impact

- Adding internal concurrency (thread pool for media downloads) would introduce shared state (the `toot_media` list) and require synchronisation.
- Adding a lock file would introduce a filesystem dependency and a failure mode (stale lock).
- Adding a daemon mode would invert the scheduling model and require process supervision.

The current model is deliberately minimal. Concurrency is the scheduler's problem.