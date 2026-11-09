# Logging

This document describes the bot's logging and observability model.

## Output streams

The bot writes exclusively to **standard output**. It does not use the `logging` module, does not write to standard error (except for unhandled tracebacks), and does not write to files other than the secret file.

## Log format

There is no structured log format. Output consists of free-form human-readable lines:

```
Successfully created the application on instance mastodon.social
URL https://example.com/image.png
 > Uploading media to Mastodon: https://example.com/image.png
   > SUCCESS! 1234567890
 > Posting fact:
This is the fact text.

 #Fact #Random
```

## Log levels

The bot has no log levels. Every line is informational. Failures produce tracebacks on standard error (unhandled exceptions) or explicit messages followed by `sys.exit` (registration, client construction, facts file).

## What is logged

| Event | Line |
|-------|------|
| Application registration (first run) | `Successfully created the application on instance <instance>` |
| Media URL recognised | `URL <url>` |
| Media upload start | ` > Uploading media to Mastodon: <url>` |
| Media upload success | `   > SUCCESS! <media_id>` |
| Media upload failure | `   > FAILURE! <exception>` |
| Fact publication | ` > Posting fact:` followed by the body |

## What is not logged

- The access token (never printed).
- The secret file contents.
- The full facts file.
- Timestamps (the scheduler provides them).
- Structured fields (JSON, key-value pairs).
- Debug or trace information.

## Correlation

The operator correlates runs using the scheduler's timestamp and the printed instance name. The fact body printed at the end of a successful run matches the published status on the instance.

## Modification impact

- Adding the `logging` module would introduce a dependency and a configuration surface (level, format, handlers).
- Adding timestamps would duplicate the scheduler's timestamps.
- Adding structured logging would require a schema and a consumer.
- The current model is intentionally minimal: the scheduler captures stdout, and the operator reads it.

## Recommendation

Keep stdout-only logging. If structured observability is needed, wrap the bot in a script that emits JSON envelopes around each invocation's stdout/stderr and exit code.