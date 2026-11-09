# Repository overview

## Purpose

Mastodon Random Facts Bot posts a random fact to a Mastodon instance from a predefined, operator-maintained list of facts. It is designed to keep Mastodon users informed and entertained by publishing a new fact on a regular basis.

## Scope

The repository owns:

- The Python entry point that orchestrates the complete posting pipeline.
- Two operator-editable helper modules that define text replacement and dynamic tag behaviour.
- The declared dependency manifest.
- Repository documentation and policy files.

The repository does not own:

- The facts file content, which the operator supplies at runtime.
- The Mastodon instance, its API, or the published statuses.
- The scheduler that invokes the bot; the repository documents a `systemd` example but does not ship it.
- The application secret file, which the bot creates at runtime in the working directory.

## Entry points

There is exactly one executable entry point: [mastodon-random-facts-bot.py](../mastodon-random-facts-bot.py). It is a console script, not an importable library. The two helper modules, [text_replacements.py](../text_replacements.py) and [dynamic_tags.py](../dynamic_tags.py), are imported by the entry point and are not independently executable.

## Invocation model

The bot is a one-shot batch process. Each invocation:

1. Reads six positional command-line arguments.
2. Bootstraps or reuses the local application secret file.
3. Constructs a Mastodon API client.
4. Reads the facts file and selects one fact at random.
5. Extracts, downloads, and uploads embedded media.
6. Transforms the fact text and assembles tags.
7. Publishes one public status.
8. Exits.

There is no daemon mode, no internal scheduler, no queue, and no retry loop. Periodicity is the responsibility of the external scheduler. See [Concurrency and scheduling](./concurrency-and-scheduling.md).

## Principal capabilities

- Random selection of one fact per invocation from a local file.
- Automatic media handling: URLs embedded in facts are downloaded, uploaded to Mastodon, attached to the status, and removed from the published text.
- Operator-customisable text transformation and dynamic tag derivation through the two helper modules.
- Static tag injection through a command-line argument, with deduplication against the fact body.
- First-run application registration persisted in a local secret file.

## Repository identity

- Remote: `git@github.com:hmlendea/mastodon-random-facts-bot.git`
- Default branch: `master`
- Licence: GNU General Public License v3.0 or later ([LICENSE](../LICENSE))
- Released tags: `v1.0.0` through `v1.4.1`
