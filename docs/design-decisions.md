# Design decisions

This document records the significant design decisions that shape the bot, their rationale, and their consequences. It is intended for future maintainers who need to understand why the code is the way it is.

## 1. Scheduled batch over daemon

**Decision:** The bot is a one-shot process launched by an external scheduler (systemd timer), not a long-running daemon.

**Rationale:**
- Eliminates process supervision concerns (crash recovery, log rotation, signal handling).
- Makes each invocation a clean slate; no in-process state to corrupt.
- Aligns with the "post one fact, exit" mental model.
- The operator already has a scheduler (systemd); no need to reimplement scheduling.

**Consequences:**
- No in-memory caching, connection pooling, or rate-limit tracking across runs.
- Transient failures defer to the next schedule; no retry logic needed.
- The access token is passed at each invocation, never cached.

## 2. Six positional arguments, no configuration file

**Decision:** All configuration arrives as six positional CLI arguments. No config file, no environment variables, no defaults.

**Rationale:**
- Self-describing scheduler logs: the invocation line shows exactly what ran.
- No configuration drift between scheduler and bot.
- Breaking changes are immediately visible (missing argument = traceback).
- Secrets (access token) are not persisted by the bot.

**Consequences:**
- Adding configuration is a breaking change for every scheduler invocation.
- The operator must manage argument quoting (especially for tags).
- No help text, no validation, no discoverability.

## 3. Two operator hooks, no plugin system

**Decision:** Customisation points are `text_replacements.apply` and `dynamic_tags.get`, imported directly as modules. No plugin discovery, no configuration-driven hooks.

**Rationale:**
- Zero infrastructure: the hooks are just Python functions in files the operator edits.
- Clear contract: function name, signature, return type.
- No version skew between core and plugins; they are the same deployment.
- The operator has full control; the project has zero control over hook behaviour.

**Consequences:**
- Hooks must be edited in place; no separate plugin directory.
- Changing a hook signature breaks all operator customisations.
- Hooks cannot have their own dependencies (standard library only).

## 4. Sequential media handling, no parallelism

**Decision:** Media downloads and uploads happen one at a time in a loop.

**Rationale:**
- The bot posts at most one status per run; the media set is small (typically 0-1 items).
- The documented `RuntimeMaxSec=60` bounds the run; parallelism would not materially improve throughput.
- Sequential code is simpler to reason about and debug.

**Consequences:**
- A slow media host blocks the entire run.
- No retry or timeout; a slow host causes a failed run.
- The operator must choose reliable media hosts.

## 5. No deduplication of facts

**Decision:** `random.choice` selects uniformly from all facts every run. No history, no tracking.

**Rationale:**
- Deduplication requires persistent state, which contradicts the stateless batch model.
- The facts file is the operator's responsibility; if they want no repeats, they curate the file.
- Simplicity: no database, no migration, no backup.

**Consequences:**
- The same fact may post on consecutive runs.
- The operator observes this in the timeline and adjusts the facts file if undesired.

## 6. Media URL extraction by regex and suffix

**Decision:** URLs are extracted with a regex and filtered by a hardcoded suffix list (`.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`).

**Rationale:**
- No HTML parsing, no content-type sniffing, no HEAD requests.
- The facts file is operator-authored; the operator controls what URLs appear.
- Simplicity: a few lines of code, no dependencies.

**Consequences:**
- URLs with query strings are truncated at `?` (regex character class excludes `?`).
- Case-sensitive suffix check: `.JPG` is not recognised.
- Unsupported URLs remain in the published text.
- The operator must use clean, direct image URLs.

## 7. Tag filtering against body and self

**Decision:** Hashtags already present in the fact body are not re-appended. Duplicate hashtags in the combined tag set are collapsed.

**Rationale:**
- Prevents visual clutter in the published status.
- The operator can include hashtags in the fact text or in the tags argument; both work.
- Case-insensitive matching with trailing-space trick handles prefix collisions (`#art` vs `#artificial`).

**Consequences:**
- The operator cannot force a duplicate hashtag.
- Non-hashtag tokens in the tags argument are preserved verbatim (allows arbitrary text append).

## 8. No retry, no backoff, no idempotency

**Decision:** Any failure terminates the run. The next scheduled run is the retry.

**Rationale:**
- Retrying a status post risks duplicate publication, which is worse than a missed cycle.
- Idempotency keys would require persistent state.
- The scheduler already provides periodic retry.

**Consequences:**
- Transient network blips cause a missed post.
- Rate limits cause a missed post.
- The operator sees gaps in the timeline and knows the scheduler will retry.

## 9. Secret file created automatically, never rotated

**Decision:** `Mastodon.create_app` runs on first run; the secret file is reused forever.

**Rationale:**
- Zero operator setup: the first scheduled run bootstraps the application.
- Application credentials are long-lived; rotation is not required by Mastodon.
- The operator can delete the file to force re-registration.

**Consequences:**
- Multiple applications may accumulate on the instance if the file is deleted repeatedly.
- The secret file is plain JSON; filesystem permissions are the only protection.

## 10. Standard output only, no logging framework

**Decision:** The bot prints human-readable lines to stdout. No `logging` module, no levels, no structure.

**Rationale:**
- The scheduler captures stdout; the operator reads the journal.
- No configuration, no handlers, no formatters.
- The output is already correlated with the scheduler's timestamps.

**Consequences:**
- No structured log parsing.
- No debug/trace levels.
- Adding observability requires a wrapper script.

## 11. Unused imports and dependencies retained

**Decision:** `base64`, `hashlib`, and `regex` remain in the codebase despite being unused.

**Rationale:**
- They are harmless (no runtime cost beyond import).
- Removing them is a cosmetic change with no behavioural impact.
- They may be placeholders for future features (e.g., media hashing, advanced regex).

**Consequences:**
- Static analysis tools flag them.
- They add noise to the dependency graph.
- A cleanup PR would be accepted but is not a priority.

## 12. No tests in the repository

**Decision:** The repository contains no test files, no test runner configuration, and no CI pipeline.

**Rationale:**
- The bot is a simple script with two operator hooks; the core logic is the pipeline order.
- The operator tests by running the bot manually or observing the timeline.
- Adding tests would require mocking Mastodon, media hosts, and the scheduler.

**Consequences:**
- No regression detection for refactoring.
- No confidence for dependency updates.
- The operator bears the testing burden.

---

Each decision is a trade-off. The current design optimises for **simplicity of deployment and operation** at the cost of **observability, configurability, and resilience**. Future maintainers should evaluate whether the trade-offs still hold before changing them.