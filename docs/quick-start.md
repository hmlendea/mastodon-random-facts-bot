# Quick start

This guide takes a new contributor from an empty checkout to one verified posting cycle. It covers only what is necessary to run the bot; architectural detail lives in [Architecture](./architecture.md) and the root [ARCHITECTURE.md](../ARCHITECTURE.md).

## Prerequisites

- Python 3
- The `pip` package manager
- A Mastodon account with an access token that has write scope
- A local facts file containing one fact per line

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

This installs the three declared packages from [requirements.txt](../requirements.txt): `fake_useragent`, `Mastodon.py`, and `regex`. Only `Mastodon.py` and `requests` (a transitive dependency of `Mastodon.py`) are actually imported by the source; see [Dependencies](./dependencies.md).

## Prepare the facts file

Create a text file with one fact per line. A fact may embed HTTPS image URLs; the bot recognises URLs ending in `.gif`, `.jpg`, `.jpeg`, `.png`, or `.webp`, downloads them, attaches them to the post, and removes the raw URL from the published text. The literal two-character sequence `\n` inside a fact is converted to a newline at publish time.

## Run one posting cycle

```bash
python mastodon-random-facts-bot.py <facts_file> <instance> <username> <access_token> "<tags>" <language>
```

The six positional arguments, in order:

| Position | Argument | Purpose |
|----------|----------|---------|
| 1 | `facts_file` | Path to the local facts file |
| 2 | `instance` | Mastodon instance host, for example `mastodon.social` |
| 3 | `username` | Application name used for first-run registration |
| 4 | `access_token` | Mastodon access token with write scope |
| 5 | `tags` | Static hashtags to append; pass an empty string to disable |
| 6 | `language` | Language code consumed by the text replacement and dynamic tag modules |

On the first run for a given instance, the bot registers an application and writes `app_<instance>.secret` into the working directory. Subsequent runs reuse that file. The file is ignored by Git through the `*.secret` rule in [../.gitignore](../.gitignore).

## Verify

Confirm that a public status containing the selected fact, any filtered tags, and any attached media appears on the target instance. Progress lines on standard output report application creation, each media URL, upload success with the returned media ID, and the final fact body.

## Schedule it

For periodic execution, use an external scheduler. The repository documents a `systemd` timer and service pair in [README.md](../README.md) (`OnUnitActiveSec=25min`, `RuntimeMaxSec=60`). Each invocation is independent and stateless apart from the secret file.

## Next steps

- Customise fact text and tags through [Components: text replacements](./components/text-replacements.md) and [Components: dynamic tags](./components/dynamic-tags.md).
- Understand failure behaviour through [Error handling](./error-handling.md).
- Understand the full pipeline through [Flows: startup and posting cycle](./flows/startup-and-posting-cycle.md).
