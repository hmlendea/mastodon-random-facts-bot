# Invariants

This document lists the properties the bot guarantees (or deliberately does not guarantee) across all executions. These are the contracts that future modifications must preserve.

## Guaranteed invariants

### I1: At most one status per invocation
The bot calls `status_post` at most once. The code path contains exactly one call to `status_post`, and it is reached only when all preceding stages succeed.

### I2: Publication only on complete success
A status is published if and only if every stage from argument parsing through media upload succeeds. Any exception before `status_post` prevents publication. There is no partial post, no post without media, and no post with a stale fact.

### I3: No media URLs in published body
Every supported media URL (matching the suffix list) is removed from the fact text via `str.replace` before publication. The published body never contains a URL that was uploaded as an attachment.

### I4: No duplicate hashtags in published body
The tag filtering logic ensures that:
- A hashtag already present in the fact body is not re-appended.
- A hashtag appearing multiple times in the combined tag set appears only once in the output.
- Matching is case-insensitive; original casing is preserved.

### I5: Secret file created at most once per instance
`Mastodon.create_app` is called only when `app_<instance>.secret` does not exist. The file is written once and never modified by the bot thereafter.

### I6: Hook signatures are stable
The entry point calls `text_replacements.apply(text, language)` and `dynamic_tags.get(text, language)` with exactly these signatures. The return types are `str` and `str | None` respectively. Changing these signatures breaks operator customisations.

### I7: No local state between runs
The bot writes only the secret file (once) and stdout. It reads the facts file and the secret file. No other files are created, read, or modified. The process retains no memory across invocations.

### I8: Access token never persisted
The access token arrives as a command-line argument, lives in process memory, is transmitted to the Mastodon instance over HTTPS, and is never written to disk by the bot.

### I9: Media bytes never written to disk
Downloaded media bytes are held in memory (`media.content`) and passed directly to `media_post`. No temporary files are created.

### I10: Tag block separated by exactly one blank line
When tags are present, the final body is `body + '\n\n' + tags`. When no tags are present, no trailing blank line is added.

## Deliberately not guaranteed

### N1: Fact uniqueness across runs
The bot does not track posted facts. The same fact may be selected on consecutive runs.

### N2: Posting cadence
The bot has no scheduler. The cadence is entirely determined by the external scheduler. A failed run produces no post; the next run may produce a post.

### N3: Media upload success
Media uploads can fail (network, rate limit, instance error). A failure aborts the run; no status is published. Already-uploaded media from earlier iterations in the same run is not deleted.

### N4: Media host availability
The bot does not validate media URLs before downloading. A dead media host causes a failed run.

### N5: Rate limit handling
The bot does not inspect rate-limit headers, does not back off, and does not retry. A rate-limited call fails the run.

### N6: Instance health
The bot does not check instance availability before running. An unreachable instance causes a failed run.

### N7: Fact file validity
The bot assumes the facts file is non-empty, readable, and UTF-8. An empty file raises `IndexError`; an unreadable file exits with code 1.

### N8: Hook behaviour
The operator hooks are operator code. The bot makes no guarantees about their correctness, performance, or side effects. An exception in a hook fails the run.

### N9: Argument validation
The bot does not validate argument formats (instance domain, token format, language code). Invalid values cause downstream failures.

### N10: Media URL correctness
The regex and suffix filter are heuristics. A URL that passes the filter may not be a valid image; a URL that fails the filter may be a valid image with an unsupported extension.

## Invariant enforcement

The invariants are enforced by the code structure, not by assertions or tests. The single linear pipeline in `mastodon-random-facts-bot.py` makes I1–I5 and I7–I10 structurally inevitable. I6 is a convention documented in [Operator extension API](./api-reference/operator-extension-api.md).

## Modification checklist

When changing the bot, verify:

- [ ] I1: Still exactly one `status_post` call?
- [ ] I2: Can any new stage fail after media upload but before publication?
- [ ] I3: Does the new stage re-insert media URLs?
- [ ] I4: Does the new tag logic preserve deduplication?
- [ ] I5: Is the secret file still written only on absence?
- [ ] I6: Are hook signatures unchanged?
- [ ] I7: Is any new persistent state introduced?
- [ ] I8: Is the access token still never written to disk?
- [ ] I9: Are media bytes still only in memory?
- [ ] I10: Is the tag separator still exactly `'\n\n'`?

If any check fails, the change breaks an invariant and must be justified in the PR description.