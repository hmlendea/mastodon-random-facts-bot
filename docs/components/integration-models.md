# Component: integration models

This document deep-dives the three integration models the entry point uses to interact with the outside world: the Mastodon API client, the media downloader, and the user agent supplier. It records the exact call shapes, the data that crosses each boundary, and the failure semantics.

## Mastodon API client (`Mastodon.py`)

### Model

The bot uses the `Mastodon` class from the `Mastodon.py` package as its sole Mastodon API client. The client is constructed once per run and used for three operations.

### Construction

```python
mastodon_api = Mastodon(
    access_token=mastodon_access_token,
    api_base_url='https://' + mastodon_instance
)
```

- The instance URL is assembled by string concatenation with a hardcoded `https://` scheme. There is no support for `http://`, custom ports, or path-prefixed instances.
- The access token is passed directly from the command line.
- Construction is wrapped in `try`/`except Exception`; failure exits with code 2.

### Application registration

```python
Mastodon.create_app(
    mastodon_username,
    api_base_url='https://' + mastodon_instance,
    to_file="app_" + mastodon_instance + '.secret'
)
```

- Called only when the secret file is absent.
- The `to_file` parameter persists the application credentials locally.
- A falsy return is treated as failure and exits with code 1.

### Media upload

```python
media_posted = mastodon_api.media_post(
    media.content,
    mime_type=media.headers.get('content-type')
)
```

- The bytes are the raw download response content.
- The MIME type is taken from the download response header, not inferred from the URL suffix.
- The returned dictionary's `id` field is collected into `toot_media`.

### Status publication

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

- The status is always public, never a reply, never marked sensitive, and has no content warning.
- `media_ids` is the list of uploaded media IDs; it is empty when the fact contains no recognised media URLs.

### Failure semantics

- Constructor failure: caught, logged, exit code 2.
- `create_app` falsy return: logged, exit code 1.
- `media_post` and `status_post` failures: unhandled tracebacks. There is no retry, no rate-limit handling, and no partial rollback of already-uploaded media.

## Media downloader (`requests`)

### Model

The bot uses the `requests` package to download media bytes from URLs embedded in fact text. Downloads are sequential, one per extracted URL.

### Call shape

```python
user_agent = UserAgent().firefox
headers = {'User-Agent': user_agent}
media = requests.get(media_url, headers=headers)
media.raise_for_status()
```

- A fresh `UserAgent` instance is created per media item (see the next section).
- `raise_for_status()` converts HTTP error codes (4xx, 5xx) into exceptions.
- The response content is passed directly to `media_post` without writing to disk.

### Data crossing the boundary

- Outbound: the media URL (from the fact file) and a Firefox user agent header.
- Inbound: the response body (bytes) and the `content-type` header (used as the Mastodon MIME type).

### Failure semantics

Any exception (connection error, timeout, HTTP error) is caught by the media loop's `try`/`except`, printed as `   > FAILURE! <exception>`, and re-raised. The process terminates before publication. Already-uploaded media from earlier iterations is not deleted.

## User agent supplier (`fake_useragent`)

### Model

The bot uses `fake_useragent.UserAgent` to obtain a rotating Firefox user agent string for media downloads. The purpose is to present a browser-like user agent to media hosts.

### Call shape

```python
user_agent = UserAgent().firefox
```

- A new `UserAgent` object is instantiated inside the media loop, once per media URL.
- The `.firefox` property yields a Firefox user agent string.

### Architectural consequence

`fake_useragent` may fetch its user agent data from a remote source on first use. This means a media download can fail not only because of the media host but also because the user agent supplier itself failed. Such a failure surfaces through the same `FAILURE!` path as a download failure and is indistinguishable in the logs.

## Boundary summary

| Integration | Direction | Protocol | Data out | Data in | Failure owner |
|-------------|-----------|----------|----------|---------|---------------|
| `Mastodon.create_app` | Outbound | HTTPS | Application name, instance URL | Secret file | Entry point (exit 1) |
| `Mastodon(...)` constructor | Outbound | HTTPS | Access token, instance URL | Client object | Entry point (exit 2) |
| `media_post` | Outbound | HTTPS | Media bytes, MIME type | Media ID | Entry point (re-raise) |
| `status_post` | Outbound | HTTPS | Body, media IDs, visibility | Status ID | Entry point (unhandled) |
| `requests.get` | Outbound | HTTPS | Media URL, user agent header | Bytes, content-type | Entry point (re-raise) |
| `UserAgent().firefox` | Outbound (potential) | HTTPS | None | User agent string | Entry point (re-raise) |

See [Integrations](../integrations.md) for the external-system perspective and [API usage examples](../api-usage-examples.md) for concrete call payloads.
