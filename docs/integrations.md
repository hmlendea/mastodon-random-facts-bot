# Integrations

This document describes the external systems the bot integrates with, the nature of each integration, and the failure modes.

## Integration inventory

| System | Protocol | Direction | Purpose | Authentication |
|--------|----------|-----------|---------|----------------|
| Mastodon instance | HTTPS | Outbound | Application registration, media upload, status publication | Access token (user), application secret (app) |
| Arbitrary media hosts | HTTPS | Outbound | Media byte download | None (public URLs) |
| `fake_useragent` upstream | HTTPS | Outbound (potential) | User agent data refresh | None |

## Mastodon instance

### Nature

The bot integrates with a single Mastodon instance specified by the `instance` argument. The instance URL is assembled as `https://<instance>`; there is no support for custom schemes, ports, or paths.

### Operations

1. **Application registration** (`POST /api/v1/apps` via `Mastodon.create_app`). Once per instance, persisted to the secret file.
2. **Media upload** (`POST /api/v2/media` or `/api/v1/media` via `media_post`). Once per media URL per run.
3. **Status publication** (`POST /api/v1/statuses` via `status_post`). Once per run.

### Data exchanged

- **To instance:** application name, instance URL (registration); media bytes and MIME type (upload); body, media IDs, visibility (publication); access token (all authenticated calls).
- **From instance:** application credentials (registration); media ID (upload); status object (publication, discarded).

### Failure modes

- Instance unreachable: registration or API call raises; run terminates.
- Rate limited: API call raises; run terminates.
- Token invalid: API call raises; run terminates.
- Instance version incompatibility: API call may raise or return unexpected shapes.

### Operator responsibilities

- Ensure the instance allows application registration.
- Ensure the access token has `write:statuses` and `write:media` scopes.
- Monitor instance rate limits and availability.

## Arbitrary media hosts

### Nature

The bot downloads media bytes from any HTTPS URL embedded in fact text that matches the supported suffix list. The media host is not known in advance; it is whatever the operator puts in the facts file.

### Operations

1. **HTTP GET** (`requests.get` with a Firefox user agent header). Once per media URL per run.

### Data exchanged

- **To host:** URL, Firefox user agent header.
- **From host:** response bytes, `content-type` header.

### Failure modes

- Host unreachable: `requests.get` raises; run terminates.
- HTTP error (4xx, 5xx): `raise_for_status()` raises; run terminates.
- Redirect loops or excessive redirects: `requests` raises; run terminates.
- Slow response: no timeout configured; the run may hang until the scheduler's `RuntimeMaxSec` kills it.
- Non-image content served with an image URL: bytes are forwarded to Mastodon; Mastodon may reject the upload.

### Operator responsibilities

- Use reliable media hosts in fact files.
- Prefer URLs without query strings (the regex truncates at `?`).
- Ensure media hosts allow the bot's user agent.

## `fake_useragent` upstream

### Nature

`fake_useragent` may fetch its user agent database from a remote source on first use. This is an implicit, undeclared network dependency.

### Operations

1. **Data fetch** (internal to `fake_useragent`). Once per `UserAgent()` instantiation, which is once per media URL per run.

### Failure modes

- Upstream unreachable: `UserAgent().firefox` may raise or return a fallback; behaviour varies by version.
- Stale data: user agent strings may become outdated.

### Operator responsibilities

- None directly. The integration is a side effect of the media download user agent strategy.

## Integration boundaries

The bot does not integrate with:

- Databases or object storage.
- Message queues or event buses.
- Monitoring or alerting systems.
- CI/CD systems.
- Package registries at runtime (only at install time).

## Modification impact

- Adding a new external integration (for example, a URL shortener) adds a new outbound boundary, a new failure mode, and a new dependency.
- Changing the Mastodon API client library changes the integration contract.
- Adding media host authentication changes the facts file format (credentials must be stored somewhere).

See [Components: integration models](./components/integration-models.md) for the code-level call shapes.