# Ambiguities and open questions

This document records known ambiguities in the codebase, undocumented behaviours, and open questions for future maintainers. Each entry states the observation, the likely intent, and the risk if left unresolved.

## Ambiguities

### A1: `while random_fact is None` loop

**Observation:** The entry point wraps `random.choice(facts)` in `while random_fact is None:`. `random.choice` never returns `None` for a non-empty list, so the loop executes exactly once.

**Likely intent:** Defensive programming against a hypothetical `None` return, or leftover from an earlier implementation.

**Risk:** Low. The loop is harmless but misleading. A reader may assume `random.choice` can return `None`.

**Resolution options:** Remove the loop; document why it exists; add a comment.

### A2: `base64` and `hashlib` imports

**Observation:** The entry point imports `base64` and `hashlib` but never uses them.

**Likely intent:** Placeholders for future features (media hashing, deduplication, content addressing).

**Risk:** Low. Dead imports confuse readers and trigger linter warnings.

**Resolution options:** Remove the imports; implement the intended feature; document the intent.

### A3: `regex` dependency unused

**Observation:** `requirements.txt` declares `regex`, but no source file imports it. The code uses the standard `re` module.

**Likely intent:** Leftover from an earlier implementation that used the `regex` package for advanced pattern matching.

**Risk:** Low. An unnecessary dependency increases install time and attack surface.

**Resolution options:** Remove from `requirements.txt`; switch to `regex` for the URL extraction; document the intent.

### A4: Media URL regex character class

**Observation:** The regex `https://[a-zA-Z0-9%\./_\-]*` excludes `?`, `&`, `=`, `#`, `:`, `@`, and other URL characters. URLs with query strings are truncated at `?`.

**Likely intent:** Conservative matching to avoid capturing trailing punctuation in fact text.

**Risk:** Medium. Facts with query-string URLs (common on CDN links) fail to download, causing run failures.

**Resolution options:** Extend the character class; use a URL-parsing library; document the limitation in the facts file format guide.

### A5: Case-sensitive suffix check

**Observation:** The suffix filter checks `.gif`, `.jpg`, `.jpeg`, `.png`, `.webp` in lowercase only. `.JPG` and `.PNG` are not recognised.

**Likely intent:** Simplicity.

**Risk:** Medium. Facts with uppercase extensions publish the URL as text instead of attaching media.

**Resolution options:** Lowercase the URL before the suffix check; document the limitation.

### A6: `UserAgent()` instantiated per media item

**Observation:** `UserAgent()` is created inside the media loop, once per URL. `fake_useragent` may fetch its data source on each instantiation.

**Likely intent:** Unintentional; the author may have assumed a singleton.

**Risk:** Medium. Multiple network calls to the user agent upstream per run; potential failure point indistinguishable from media download failure.

**Resolution options:** Hoist `UserAgent()` outside the loop; cache the user agent string; document the behaviour.

### A7: `media.headers.get('content-type')` forwarded as MIME type

**Observation:** The download response's `content-type` header is passed directly to `media_post` as the MIME type. No validation or normalisation occurs.

**Likely intent:** Trust the media host's content type.

**Risk:** Medium. A host serving `text/html` for an image URL causes Mastodon to reject the upload. A host serving a generic type (`application/octet-stream`) may cause Mastodon to misclassify the media.

**Resolution options:** Infer MIME type from the URL suffix; validate against an allowlist; document the behaviour.

### A8: `tags_to_add` concatenation with leading space

**Observation:** Static and dynamic tags are concatenated with a leading space (`' ' + tags_to_add`). The filtering block splits on spaces, producing an empty first token when the string starts with a space.

**Likely intent:** Ensure separation when appended to the body.

**Risk:** Low. The empty token is filtered out (no `#`, kept verbatim as empty string, then stripped). Behaviour is correct but the mechanism is non-obvious.

**Resolution options:** Use `str.split()` without argument to split on any whitespace and drop empties; document the mechanism.

### A9: `filtered_tags_to_add` initial value

**Observation:** `filtered_tags_to_add` is initialised to `''` (empty string) but the filtering loop appends `' ' + tag`, producing a leading space. The final `.strip()` removes it.

**Likely intent:** Accumulate tags with space separators.

**Risk:** Low. Correct after stripping, but the intermediate state is awkward.

**Resolution options:** Initialise to a list and join; document the accumulation pattern.

### A10: Secret file format undocumented

**Observation:** `Mastodon.create_app(..., to_file=...)` writes a JSON file, but the bot never reads it directly; `Mastodon.py` reads it during client construction. The format is an implementation detail of `Mastodon.py`.

**Likely intent:** Delegate credential persistence to the library.

**Risk:** Low. A `Mastodon.py` version change could alter the file format, breaking reuse.

**Resolution options:** Document the file as opaque; pin the `Mastodon.py` version; add a version check.

## Open questions

### Q1: Should the bot deduplicate facts?

**Context:** `random.choice` may select the same fact on consecutive runs. The bot retains no history.

**Considerations:**
- Deduplication requires persistent state (a file, a database, or instance-side tracking).
- Persistent state contradicts the stateless batch model.
- The operator can curate the facts file to reduce repeats.
- A wrapper script could track posted fact hashes externally.

**Status:** Open. No consensus documented.

### Q2: Should the bot retry transient failures?

**Context:** Any failure terminates the run. The next scheduled run is the retry.

**Considerations:**
- Retrying `status_post` risks duplicate publication.
- Retrying `media_post` is safe (media upload is idempotent from the bot's perspective; orphaned media accumulates).
- A bounded retry with backoff for media only would reduce missed posts.

**Status:** Open. The no-retry policy is a deliberate design decision; changing it requires justification.

### Q3: Should the bot validate media before upload?

**Context:** Downloaded bytes are forwarded to Mastodon without content validation.

**Considerations:**
- Validation (magic bytes, dimensions, size) adds complexity and dependencies.
- Mastodon performs its own validation and rejects invalid media.
- The failure mode (run terminates, no post) is acceptable.

**Status:** Open. Current behaviour is acceptable for operator-authored facts.

### Q4: Should the bot support multiple facts per run?

**Context:** The bot posts exactly one fact per invocation.

**Considerations:**
- Multiple facts per run would require multiple `status_post` calls, violating I1.
- The scheduler controls cadence; multiple facts per run reduces scheduler flexibility.
- The current model is simple and predictable.

**Status:** Open. No requirement documented.

### Q5: Should the bot expose a health endpoint?

**Context:** The bot is a batch job with no daemon. Health is inferred from scheduler logs and timeline activity.

**Considerations:**
- A health endpoint requires a daemon, contradicting the batch model.
- External monitoring (for example, uptime checks on the timeline) is the operator's responsibility.
- The scheduler's `RuntimeMaxSec` provides a liveness signal.

**Status:** Open. Not applicable under the current architecture.

### Q6: Should the repository add CI?

**Context:** No CI pipeline exists. No tests exist.

**Considerations:**
- CI without tests provides no value.
- Adding tests requires extracting testable functions from the linear script.
- The project is small and operator-maintained.

**Status:** Open. See [Testing](./testing.md) for the recommendation.

## How to resolve an entry

1. Open an issue on the repository describing the ambiguity or question.
2. Link the issue from the relevant entry (replace this text with the issue number).
3. When resolved, remove the entry and update affected documentation.
