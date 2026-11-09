# State and persistence

This document describes what state the bot creates, reads, and retains across invocations.

## Persistent state

The bot creates exactly one persistent artefact:

| Artefact | Location | Created | Read | Written | Deleted |
|----------|----------|---------|------|---------|---------|
| `app_<instance>.secret` | Current working directory | First run (when absent) | Every run | First run only | Never by the bot |

The secret file contains the application credentials (client ID and client secret) returned by `Mastodon.create_app`. It is a plain JSON file.

### Secret file lifecycle

1. **First run on an instance.** `os.path.isfile` returns false. `Mastodon.create_app` registers an application on the instance and writes credentials to the file. The bot prints a success message.
2. **Subsequent runs.** `os.path.isfile` returns true. Registration is skipped. The file is read by `Mastodon.py` during client construction.
3. **Manual deletion.** If the operator deletes the file, the next run re-registers a new application. The old application remains registered on the instance until revoked.
4. **Corruption.** If the file exists but is invalid, `Mastodon.py` raises during client construction. The bot exits with code 2.

## Transient state

All other state is in-memory and dies with the process:

- The full facts list.
- The selected fact.
- Extracted media URLs.
- Downloaded media bytes.
- Uploaded media IDs.
- The final toot body.

## State the bot does not retain

- **Posting history.** The bot does not remember which facts were posted. Deduplication is impossible without external state.
- **Published status IDs.** The return value of `status_post` is discarded.
- **Media IDs after publication.** The `toot_media` list is discarded when the process exits.
- **Rate limit state.** The bot does not read rate-limit headers.
- **Configuration.** All configuration arrives as CLI arguments; nothing is cached.

## External state

The bot creates state on external systems:

| System | State created | Owned by |
|--------|---------------|----------|
| Mastodon instance | Registered application | Instance |
| Mastodon instance | Uploaded media attachments | Instance |
| Mastodon instance | Published statuses | Instance |

The bot has no mechanism to query, list, or delete this external state. Orphaned media (from failed runs after upload but before publication) accumulates on the instance until manually removed.

## Scheduler state

The scheduler (for example `systemd`) retains its own state: last activation time, failure count, journal logs. This state is outside the bot's control and outside this document's scope.

## Consequences of the stateless design

- **Idempotent invocations.** Each run is independent; there is no state to corrupt.
- **Trivial rollback.** Deleting the secret file and facts file returns the system to its initial state (modulo external Mastodon state).
- **No migration path.** Because there is no schema, there are no migrations.
- **No backup requirement.** The only local file worth backing up is the secret file; the facts file is operator-owned.

## Modification impact

- Adding persistent state (for example, a posting history for deduplication) introduces a new file, a new failure mode, and a new migration concern.
- Adding a cache (for example, downloaded media) introduces disk I/O and cleanup logic.
- The current design deliberately excludes both. See [Architecture](./architecture.md) for the rationale.