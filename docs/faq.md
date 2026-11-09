# FAQ

Frequently asked questions about the bot, its behaviour, and its operation.

## General

### What is this bot?

A Python script that posts a random fact to a Mastodon account on a schedule. It reads facts from a text file, optionally attaches media referenced in the fact, appends hashtags, and publishes a public status.

### Who maintains it?

The repository is maintained by hmlendea. Operators can customise text transformation and dynamic tags by editing two hook modules without touching the core script.

### What licence is it under?

GNU GPL v3.0 or later. See [LICENSE](../LICENSE).

## Operation

### How often does it post?

The bot itself has no schedule. The posting cadence is determined by the external scheduler. The documented `systemd` example runs approximately every 25 minutes.

### Can the same fact post twice?

Yes. The bot selects uniformly at random from all facts every run and retains no memory of previous selections. If you want no repeats, curate the facts file or implement deduplication in a wrapper.

### Can I post to multiple instances?

Yes, by running the bot multiple times with different `instance`, `username`, and `access_token` arguments. Each instance gets its own secret file (`app_<instance>.secret`).

### Can I post in multiple languages?

Yes, by running the bot multiple times with different facts files and `language` arguments. The `language` argument is passed to the operator hooks for locale-specific behaviour.

### Can I change the visibility from public?

Not without editing the entry point. The `status_post` call hardcodes `visibility='public'`. Changing it is a one-line edit but affects all posts.

### Can I add a content warning?

Not without editing the entry point. The `status_post` call hardcodes `spoiler_text=None`. Changing it is a one-line edit.

### Can I post replies or boosts?

No. The bot only creates original public statuses. `in_reply_to_id` is hardcoded to `None`.

## Media

### Which image formats are supported?

`.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`. The suffix check is case-sensitive; `.JPG` is not recognised.

### Why is my media URL not attached?

Check:
- The URL starts with `https://` (not `http://`).
- The URL ends with a supported suffix.
- The URL contains no query string (`?`) or fragment (`#`); the regex truncates at these characters.
- The URL contains only characters from `[a-zA-Z0-9%\./_\-]`.

### Why does my media URL appear in the published text?

The URL did not match the extraction regex or the suffix filter. Unsupported URLs remain in the text as plain links.

### Can I attach multiple images?

Yes, if the fact contains multiple supported media URLs. Each is downloaded, uploaded, and attached. The bot does not enforce Mastodon's media count limit; the instance rejects excess media.

### Can I attach video?

No. Only the five image suffixes are recognised. Video URLs remain in the text as plain links.

### Why does media upload fail?

Common causes:
- Media host unreachable or rate-limiting.
- Downloaded bytes are not a valid image (host served an error page).
- Access token lacks `write:media` scope.
- Media exceeds instance size limits.

See [Troubleshooting](./troubleshooting.md).

## Tags

### How do I add static tags?

Pass them as the fifth command-line argument, space-separated, quoted: `" #Fact #Random"`.

### How do I add dynamic tags?

Edit `dynamic_tags.py` to implement the `get(text, language)` function. Return a string of space-separated tags or `None`. See [Components: dynamic tags](./components/dynamic-tags.md).

### Why is my tag not appearing?

- The tag already appears in the fact body (deduplication drops it).
- The tag is a duplicate of another tag in the combined set.
- The tag token contains trailing punctuation (for example `#Fact,`).
- The `tags_to_add` argument was not quoted and the shell split it.

### Can I force a duplicate tag?

No. The filtering logic always deduplicates. This is intentional.

## Security

### Where is my access token stored?

Nowhere persistent. It is passed as a command-line argument and lives in process memory. It is visible in the process table and scheduler logs during execution. See [Security](./security.md).

### What is the secret file?

`app_<instance>.secret` contains the application credentials (client ID and secret) created on first run. It is not the access token. Protect it with filesystem permissions.

### Does the bot phone home?

No telemetry, no crash reports, no update checks. The only outbound connections are to the Mastodon instance, media hosts referenced in facts, and potentially the `fake_useragent` upstream.

## Development

### How do I customise text transformation?

Edit `text_replacements.py` and implement `apply(text, language)`. See [Components: text replacements](./components/text-replacements.md).

### How do I add a new media type?

Edit the suffix condition in the entry point. This is a compatibility-relevant change; see [Compatibility contracts](../ARCHITECTURE.md#-compatibility-contracts).

### How do I add a new configuration option?

Add a positional argument. This breaks all existing scheduler invocations. Consider a wrapper script instead.

### Are there tests?

No. See [Testing](./testing.md) for manual testing procedures.

### Can I contribute?

Yes. See [CONTRIBUTING.md](../CONTRIBUTING.md).