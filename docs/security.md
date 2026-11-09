# Security

This document describes the bot's security posture, threat model, and the security-relevant decisions in the codebase. It complements the root [SECURITY.md](../SECURITY.md).

## Threat model

### Assets

- **User access token** (command-line argument): grants write access to the Mastodon account.
- **Application secret file** (`app_<instance>.secret`): grants the ability to register new applications on the instance.
- **Published statuses**: public by design; no confidentiality requirement.
- **Facts file**: operator-controlled input; integrity matters for correct posting.

### Trust boundaries

| Boundary | Trusted | Untrusted |
|----------|---------|-----------|
| Operator host | Yes (runs the bot, holds credentials) | — |
| Facts file | Yes (operator-authored) | — |
| Secret file | Yes (created by bot, readable by operator) | — |
| Mastodon instance | No (external service) | API responses, rate limits, availability |
| Media hosts | No (external services) | Media bytes, headers, availability |
| `fake_useragent` upstream | No (external service) | User agent data freshness |

### Attack surface

1. **Command-line arguments.** The access token is visible in the process table (`ps aux`) and scheduler logs. This is a known limitation of the positional-argument model.
2. **Secret file.** Plain JSON on disk. Filesystem permissions are the only protection.
3. **Media downloads.** The bot downloads arbitrary bytes from URLs in the facts file and forwards them to Mastodon. A compromised media host could serve malicious content, but the bot does not execute or interpret the bytes.
4. **User agent fetching.** `fake_useragent` may fetch data from its upstream on first use. This is an outbound network call not directly controlled by the operator.
5. **Mastodon API calls.** All calls are authenticated with the access token over HTTPS.

## Security-relevant code properties

- **No secrets in logs.** The access token is never printed. The secret file is never printed.
- **No input validation on media URLs.** The regex and suffix filter are extraction heuristics, not security controls. A fact file containing a malicious URL will cause the bot to download from it.
- **No content validation on media.** The downloaded bytes are forwarded to Mastodon based on the response `content-type` header. The bot does not verify magic bytes, dimensions, or file structure.
- **No TLS verification disable.** `requests.get` uses the system trust store; `Mastodon.py` uses the system trust store. There is no `verify=False`.
- **No dynamic code execution.** The operator hooks (`text_replacements.apply`, `dynamic_tags.get`) are imported as modules, not `eval`ed. They run with the bot's privileges.
- **No subprocess calls.** The bot does not invoke shells or external commands.

## Credential handling

| Credential | Source | Storage | Transmission |
|------------|--------|---------|--------------|
| Access token | CLI argument | Process memory only | HTTPS to Mastodon instance |
| Application secret | `create_app` | `app_<instance>.secret` (JSON) | HTTPS to Mastodon instance (registration only) |
| Client ID/secret | Secret file | `app_<instance>.secret` | HTTPS to Mastodon instance (client construction) |

The access token is never persisted by the bot. The operator must inject it at each invocation (for example via a `systemd` `EnvironmentFile` with restricted permissions).

## Hardening recommendations

1. **Restrict secret file permissions.** `chmod 600 app_<instance>.secret`.
2. **Use a dedicated access token.** Create a token with only `write:statuses` and `write:media` scopes.
3. **Protect the scheduler environment.** If using `systemd`, store the token in an `EnvironmentFile` with `chmod 600` and `EnvironmentFile=-/path/to/token.env`.
4. **Audit the facts file.** Treat it as code: review changes, restrict write access.
5. **Monitor published statuses.** Verify that the timeline matches expectations.

## Vulnerability reporting

See [SECURITY.md](../SECURITY.md) for the project's vulnerability disclosure policy.

## Compliance

The bot processes no personal data beyond the access token (which is a credential, not personal data). See [PRIVACY.md](../PRIVACY.md) for the data-handling statement.