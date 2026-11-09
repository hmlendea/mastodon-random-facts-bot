# Mastodon API usage

This document records every Mastodon API interaction the bot performs, through the `Mastodon.py` client. It is the authoritative reference for what the bot requires from a Mastodon instance.

## Authentication model

The bot uses application-only credentials persisted in `app_<instance>.secret` plus a user access token supplied on the command line. The application is registered once per instance; subsequent runs reuse the persisted secret.

## Operations

### 1. Application registration

```python
Mastodon.create_app(
    mastodon_username,
    api_base_url='https://' + mastodon_instance,
    to_file="app_" + mastodon_instance + '.secret'
)
```

| Aspect | Detail |
|--------|--------|
| Endpoint | `POST /api/v1/apps` (via `Mastodon.py`) |
| Called when | `app_<instance>.secret` does not exist |
| Parameters | Application name (the username argument), instance base URL, output file path |
| Return | Truthy on success; falsy on failure |
| Side effect | Writes application credentials to `app_<instance>.secret` |
| Failure handling | Falsy return prints a message and exits with code 1 |

### 2. Client construction

```python
Mastodon(
    access_token=mastodon_access_token,
    api_base_url='https://' + mastodon_instance
)
```

| Aspect | Detail |
|--------|--------|
| Endpoint | None (local construction) |
| Parameters | User access token, instance base URL |
| Return | `Mastodon` client instance |
| Failure handling | Constructor exception prints an error and exits with code 2 |

Note: construction does not validate the token. Authentication failures surface at the first authenticated API call.

### 3. Media upload

```python
media_posted = mastodon_api.media_post(
    media.content,
    mime_type=media.headers.get('content-type')
)
```

| Aspect | Detail |
|--------|--------|
| Endpoint | `POST /api/v2/media` (or `/api/v1/media`, depending on `Mastodon.py` version) |
| Parameters | Raw media bytes, MIME type taken from the download response header |
| Return | Dictionary containing at least the `id` key |
| Used value | `media_posted['id']`, appended to `toot_media` |
| Failure handling | Exception propagates through the media loop's re-raise; process terminates |

### 4. Status publication

```python
mastodon_api.status_post(
    toot_body,
    in_reply_to_id=None,
    media_ids=toot_media,
    sensitive=False,
    visibility='public',
    spoiler_text=None
)
```

| Aspect | Detail |
|--------|--------|
| Endpoint | `POST /api/v1/statuses` (via `Mastodon.py`) |
| Parameters | Body text, no reply, media ID list, not sensitive, public visibility, no content warning |
| Return | Status object (unused by the bot) |
| Failure handling | Unhandled exception; traceback |

## Instance requirements

The bot requires a Mastodon instance that:

- Accepts application registration via `/api/v1/apps`.
- Accepts media uploads via the media endpoint.
- Accepts status creation via `/api/v1/statuses` with the parameters listed above.
- Serves media bytes over HTTPS when the fact file references media URLs.

The bot does not use streaming, websockets, pagination, or any read endpoints. It never fetches its own statuses, timelines, or account information.

## Rate limits

The bot performs no rate-limit introspection. A rate-limited `media_post` or `status_post` raises an exception that terminates the run. The scheduler's next activation is the implicit retry. See [Error handling](../error-handling.md).

## Data sent to the instance

| Call | Data |
|------|------|
| `create_app` | Application name (the username argument), instance URL |
| `media_post` | Downloaded media bytes, MIME type |
| `status_post` | Final toot body, media IDs, visibility |

The access token is transmitted to the instance as part of every authenticated request. See [PRIVACY.md](../../PRIVACY.md) for the data-handling statement.
