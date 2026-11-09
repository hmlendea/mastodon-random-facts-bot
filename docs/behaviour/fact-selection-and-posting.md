# Behaviour: fact selection and posting

This document describes the user-facing behaviour of the bot as it is implemented: how a fact is chosen, what the published status looks like, and what an operator can expect to observe on the Mastodon timeline.

## Selection behaviour

- Exactly one fact is selected per invocation, uniformly at random, from the lines of the operator-provided facts file.
- Selection is stateless: the bot does not remember which facts were previously posted. The same fact may be selected on consecutive invocations.
- An empty facts file causes an unhandled `IndexError` from `random.choice`; no status is published.
- The selection is not influenced by the language argument, the tags, or any external state.

## Published status shape

A successfully published status has the following structure:

```
<transformed fact text>

<filtered tags>
```

- The fact text is the selected line with media URLs removed, leading and trailing whitespace stripped, operator replacements applied, literal `\n` sequences converted to newlines, and runs of spaces collapsed.
- The tag block is present only when at least one tag survives filtering. It is separated from the body by a blank line.
- The status is always public (`visibility='public'`), never marked sensitive (`sensitive=False`), never a reply (`in_reply_to_id=None`), and never has a content warning (`spoiler_text=None`).

## Media behaviour

- Supported image URLs (`.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`, case-sensitive) embedded in the fact are downloaded, uploaded to Mastodon, attached to the status, and removed from the published text.
- Unsupported URLs remain in the published text as plain text.
- Up to one media item per extracted URL is attached; there is no limit enforcement in the bot itself, but Mastodon's own media count limits apply.
- A fact with no supported URLs publishes as a text-only status.

## Tag behaviour

- Static tags from the command line and dynamic tags from the `dynamic_tags.get` hook are combined.
- Hashtags already present in the fact body are not duplicated.
- Duplicate hashtags within the combined tag set are not duplicated.
- Non-hashtag tokens from the static argument are preserved verbatim.
- Tag matching is case-insensitive; original casing is preserved in the output.

## Observable operator signals

On standard output, a successful run prints:

1. `Successfully created the application on instance <instance>` (first run only).
2. `URL <media_url>` for each recognised media URL.
3. ` > Uploading media to Mastodon: <media_url>` before each upload.
4. `   > SUCCESS! <media_id>` after each successful upload.
5. ` > Posting fact:` followed by the fact body.

The operator can correlate these lines with the published status on the instance.

## Periodicity behaviour

The bot itself has no schedule. The observed posting cadence is entirely determined by the external scheduler. The repository documents a `systemd` example with `OnBootSec=15min` and `OnUnitActiveSec=25min`, which yields a post roughly every 25 minutes once the timer is active. Each invocation is independent; a failed run has no effect on the next run other than the absence of a post.

## What the bot does not do

- It does not deduplicate facts across runs.
- It does not verify that the access token has write scope before attempting publication.
- It does not check whether the instance is reachable before reading the facts file.
- It does not validate the facts file format beyond reading its lines.
- It does not persist any record of what was published.
- It does not send telemetry, crash reports, or update checks.
