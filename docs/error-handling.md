# Error handling

This document catalogues every error path in the bot, its observable behaviour, and the operator's recovery options.

## Error taxonomy

| Category | Trigger | Detection | Behaviour | Exit code |
|----------|---------|-----------|-----------|-----------|
| **Argument error** | Missing CLI argument | `IndexError` from `sys.argv` | Unhandled traceback | Non-zero |
| **Registration failure** | `create_app` returns falsy | Explicit check | Print message, `sys.exit(1)` | 1 |
| **Client construction failure** | `Mastodon(...)` raises | `try`/`except Exception` | Print message, `sys.exit(2)` | 2 |
| **Facts file unreadable** | `open`/`readlines` raises | Bare `except` | Print message, `sys.exit(1)` | 1 |
| **Empty facts file** | `random.choice([])` | `IndexError` | Unhandled traceback | Non-zero |
| **Media download failure** | `requests.get` raises or `raise_for_status` | `try`/`except` in media loop | Print `FAILURE!`, re-raise | Non-zero (traceback) |
| **Media upload failure** | `media_post` raises | `try`/`except` in media loop | Print `FAILURE!`, re-raise | Non-zero (traceback) |
| **Publication failure** | `status_post` raises | Unhandled | Unhandled traceback | Non-zero |
| **Hook failure** | `text_replacements.apply` or `dynamic_tags.get` raises | Unhandled | Unhandled traceback | Non-zero |

## Failure invariants

1. **No partial publication.** A status is published only when the complete pipeline succeeds. Any failure before `status_post` prevents publication.
2. **No retry within a run.** The bot never retries a failed operation. The scheduler's next activation is the retry.
3. **No rollback of uploaded media.** If media upload succeeds for some URLs and then a later URL fails, the already-uploaded media remains on the Mastodon instance as orphaned media.
4. **No state corruption.** The bot writes only the secret file (once) and standard output. A failure leaves no partial local state.

## Observable signals

### Standard output (success path)

```
Successfully created the application on instance <instance>
URL <media_url>
 > Uploading media to Mastodon: <media_url>
   > SUCCESS! <media_id>
 > Posting fact:
<fact body>
```

### Standard error / traceback (failure path)

- Registration failure: `Failed to create the application on instance <instance>` followed by exit.
- Client construction: `ERROR: Failed to log <username> into <instance>: <exception>` followed by exit 2.
- Facts file: `ERROR: Failed to read the file: <path>` followed by exit 1.
- Media failure: `   > FAILURE! <exception>` followed by traceback.
- Publication failure: raw traceback.
- Hook failure: raw traceback.

## Recovery procedures

| Failure | Recovery |
|---------|----------|
| Missing argument | Fix the scheduler invocation. |
| Registration failure | Verify instance reachability, username validity, and network access. Delete the secret file and retry. |
| Client construction | Verify access token validity and instance URL. |
| Facts file unreadable | Verify file path, permissions, and existence. |
| Empty facts file | Add at least one line to the facts file. |
| Media download failure | Verify media URL reachability, host availability, and network access. The next scheduled run retries. |
| Media upload failure | Verify instance media endpoint, token write scope, and media size limits. The next scheduled run retries. |
| Publication failure | Verify token write scope, instance status endpoint, and body length limits. The next scheduled run retries. |
| Hook failure | Fix the operator's `text_replacements.py` or `dynamic_tags.py`. The next scheduled run retries. |

## What the bot does not handle

- **Rate limits.** A rate-limited API call raises an exception. No backoff, no retry-after parsing.
- **Network partitions.** Any connection error terminates the run.
- **Mastodon maintenance windows.** The bot does not check instance health before running.
- **Media host redirects, authentication, or cookies.** The download is a bare `GET` with a user agent.
- **Large media.** No size check before download or upload.
- **Invalid MIME types.** The download response `content-type` is forwarded verbatim.

## Design rationale

The error handling is deliberately minimal because:

- The bot is a scheduled batch job, not a service. Transient failures are resolved by the next schedule.
- Retrying within a run risks duplicate publication, which is worse than a missed cycle.
- The operator has full visibility through scheduler logs and standard output.
- Adding retry logic would require idempotency keys or deduplication state, which the bot deliberately avoids.

See [Concurrency and scheduling](./concurrency-and-scheduling.md) for the scheduling model and [Behaviour: fact selection and posting](./behaviour/fact-selection-and-posting.md) for the user-facing consequences.