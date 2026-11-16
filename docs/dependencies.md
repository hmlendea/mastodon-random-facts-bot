# Dependencies

This document catalogues the bot's dependencies, their roles, and the compatibility posture.

## Runtime dependencies

Declared in [requirements.txt](../requirements.txt):

| Package | Role | Used in | Notes |
|---------|------|---------|-------|
| `Mastodon.py` | Mastodon API client | Entry point | `create_app`, `Mastodon(...)`, `media_post`, `status_post` |
| `fake_useragent` | User agent strings | Entry point | `UserAgent().firefox` per media download |
| `requests` | Media downloads | Entry point | `requests.get` for media bytes |

## Transitive dependencies

- `requests` is used directly by the entry point for media downloads and is declared explicitly in `requirements.txt`. It is also a transitive dependency of `Mastodon.py`.
- `fake_useragent` may fetch user agent data from a remote source on first use. This is an undeclared network dependency.

## Standard library usage

| Module | Used in | Purpose |
|--------|---------|---------|
| `os.path` | Entry point | `isfile` check for secret file |
| `sys` | Entry point | `argv` access, `exit` |
| `re` | Entry point, `text_replacements`, `dynamic_tags` | URL extraction, whitespace collapse, operator hooks |
| `random` | Entry point | `random.choice` for fact selection |
| `typing` | Entry point | Type hints for function signatures |

## Dependency direction

```
mastodon-random-facts-bot.py
  -> config (local constants)
  -> Mastodon.py (third-party)
  -> requests (third-party)
  -> fake_useragent (third-party)
  -> text_replacements (local, standard library only)
  -> dynamic_tags (local, standard library only)
```

The local `config` module exposes constants only. The helper modules depend only on the standard library. Neither the helper modules nor `config` depend on each other or on the entry point.

## Version pinning

`requirements.txt` declares no version constraints:

```
fake_useragent
Mastodon.py
requests
```

Consequences:

- `pip install -r requirements.txt` installs the latest compatible versions.
- Builds are not reproducible across time.
- Breaking changes in `Mastodon.py` (for example, API signature changes) surface at runtime, not at install time.

## Compatibility contracts

The bot relies on the following API shapes:

| Dependency | Contract | Risk |
|------------|----------|------|
| `Mastodon.py` | `Mastodon.create_app(name, api_base_url, to_file)` returns truthy/falsy | Medium — signature stable across major versions |
| `Mastodon.py` | `Mastodon(access_token, api_base_url)` constructor | Low |
| `Mastodon.py` | `media_post(data, mime_type)` returns dict with `id` | Medium — return shape may vary by version |
| `Mastodon.py` | `status_post(status, in_reply_to_id, media_ids, sensitive, visibility, spoiler_text)` | Medium — parameter names may change |
| `requests` | `get(url, headers)` returns response with `.content`, `.headers`, `.raise_for_status()` | Low |
| `fake_useragent` | `UserAgent().firefox` returns a string | Medium — upstream data source may change |

## Modification impact

- Adding a dependency requires updating `requirements.txt` and the dependency direction diagram.
- Pinning versions improves reproducibility but requires manual updates.
- Adding or removing a configuration constant requires editing `config.py`, which the entry point imports explicitly by name.

## Security posture

Dependencies are fetched from PyPI over HTTPS. The bot does not verify package integrity beyond pip's default behaviour. There is no lock file, no hash pinning, and no vendoring. See [Security](./security.md).