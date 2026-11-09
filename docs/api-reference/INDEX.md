# API reference

This directory documents the external APIs the bot consumes and the internal APIs it exposes to operators.

## Contents

- [Mastodon API usage](./mastodon-api-usage.md) — the exact `Mastodon.py` calls, parameters, and return values used by the bot.
- [Operator extension API](./operator-extension-api.md) — the `text_replacements.apply` and `dynamic_tags.get` contracts.
- [Command-line interface](./command-line-interface.md) — the six positional arguments and their semantics.

## External API surface

| API | Package | Operations used |
|-----|---------|-----------------|
| Mastodon REST API | `Mastodon.py` | `create_app`, `Mastodon(...)`, `media_post`, `status_post` |
| Arbitrary media hosts | `requests` | `get` |
| User agent data | `fake_useragent` | `UserAgent().firefox` |

## Internal API surface

| Module | Symbol | Signature | Return |
|--------|--------|-----------|--------|
| `text_replacements` | `apply` | `(text, language)` | `str` |
| `dynamic_tags` | `get` | `(text, language)` | `str` or `None` |

The entry point `mastodon-random-facts-bot.py` exposes no importable API; it is a script.

## Versioning

The bot does not pin dependency versions. `requirements.txt` declares `Mastodon.py`, `fake_useragent`, and `regex` without version constraints. The API shapes documented here reflect the versions current at the time of writing; see [Dependencies](../dependencies.md) for the compatibility posture.
