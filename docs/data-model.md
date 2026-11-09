# Data model

This document describes the data the bot processes, its shape, and its lifecycle. The bot has no database; the facts file is the data store.

## Entities

### Fact

A fact is a single line in the facts file. Its shape:

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| Text | `str` | Facts file line | May contain embedded media URLs and literal `\n` escape sequences |
| Media URLs | `list[str]` | Extracted via regex | Only HTTPS URLs with supported image suffixes |

A fact has no identifier, no timestamp, no author, and no state. It is a plain string.

### Media URL

A media URL is a substring of a fact matching `https://[a-zA-Z0-9%\./_\-]*` and ending with `.gif`, `.jpg`, `.jpeg`, `.png`, or `.webp` (case-sensitive).

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| URL | `str` | Regex match | Full matched string |
| Suffix | `str` | Suffix check | One of the five supported extensions |
| Bytes | `bytes` | Download response | Held in memory only |
| MIME type | `str` or `None` | Download response header | Forwarded to Mastodon |
| Media ID | `str` | Mastodon API response | Used in `status_post` |

### Tag

A tag is a space-separated token in the combined tag string.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| Token | `str` | Split of combined tag string | May or may not start with `#` |
| Is hashtag | `bool` | `'#' in token` | Determines filtering behaviour |
| Kept | `bool` | Filter result | Non-hashtags always kept; hashtags kept when not duplicated |

### Toot body

The final published body is assembled as:

```
<transformed fact text without media URLs>

<filtered tags>
```

The tag block is present only when at least one tag survives filtering.

## Data lifecycle

```
Facts file (persistent, operator-owned)
  -> readlines() -> list of fact strings (in-memory)
  -> random.choice() -> one fact string (in-memory)
  -> regex extraction -> list of media URLs (in-memory)
  -> str.replace() -> fact text without URLs (in-memory)
  -> requests.get() -> media bytes (in-memory, transient)
  -> media_post() -> media IDs (in-memory)
  -> text_replacements.apply() -> transformed body (in-memory)
  -> dynamic_tags.get() -> tag string or None (in-memory)
  -> filtering -> filtered tag string (in-memory)
  -> concatenation -> final toot body (in-memory)
  -> status_post() -> published status (owned by Mastodon instance)
```

No data is persisted by the bot except the application secret file. The published status becomes state owned by the Mastodon instance; the bot retains no record of it.

## Data ownership

| Data | Owner | Bot's role |
|------|-------|------------|
| Facts file | Operator | Read-only consumer |
| Secret file | Bot (creator), operator (owner) | Writes once, reads thereafter |
| Access token | Operator | Transient holder, never persists |
| Media bytes | Media host | Transient downloader, never persists |
| Published status | Mastodon instance | Creator, no local record |
| Media attachments | Mastodon instance | Uploader, no local record |

## Data quality assumptions

The bot assumes:

- The facts file is UTF-8 encoded text (Python 3 default).
- Each line is a complete fact.
- Media URLs are well-formed HTTPS URLs.
- The facts file is non-empty.
- The facts file is readable by the bot process.

Violations of these assumptions produce the error behaviours documented in [Error handling](./error-handling.md).

## Modification impact

- Changing the facts file format (for example, to JSON) requires changing the read and selection logic.
- Adding fact metadata (for example, per-fact tags) requires a richer data model and a parser.
- Adding deduplication requires persistent state, which the current model deliberately excludes.
