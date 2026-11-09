# Entry point and orchestration

This document deep-dives [mastodon-random-facts-bot.py](../../mastodon-random-facts-bot.py), the single executable component. It covers purpose, ownership, exact execution order, data transformations, state access, failure ownership, and modification impact. The root [ARCHITECTURE.md](../../ARCHITECTURE.md) defines the component's position in the wider system; this document explains its internals.

## Purpose and scope

The entry point owns the complete posting pipeline: argument interpretation, application secret bootstrap, Mastodon client construction, fact selection, media extraction and handling, text transformation delegation, tag assembly, and status publication. It is the only component that performs network I/O or file I/O.

It deliberately does not own:

- Text transformation rules (delegated to `text_replacements.apply`).
- Dynamic tag derivation (delegated to `dynamic_tags.get`).
- Scheduling (owned by the external scheduler).
- Fact content (owned by the operator's facts file).

## Location and invocation

- Path: `mastodon-random-facts-bot.py` (repository root).
- Invocation: `python mastodon-random-facts-bot.py <facts_file> <instance> <username> <access_token> <tags> <language>`.
- Entry mechanism: top-level script execution; there is no `if __name__ == '__main__':` guard, no `main()` function, and no argument parser. The entire script is the pipeline.

## Exact execution order

The script executes top to bottom with no functions and no branches other than the secret-file check and the media suffix filter. The ordered stages:

1. **Imports.** Standard library (`os.path`, `sys`, `re`, `base64`, `hashlib`, `random`), third-party (`mastodon.Mastodon`, `requests`, `fake_useragent.UserAgent`), and local modules (`text_replacements`, `dynamic_tags`). Note: `base64` and `hashlib` are imported but never used.
2. **Argument capture.** `sys.argv[1]` through `sys.argv[6]` are bound to `facts_file_path`, `mastodon_instance`, `mastodon_username`, `mastodon_access_token`, `tags_to_add`, and `language`. There is no validation; a missing argument raises `IndexError`.
3. **Secret bootstrap.** If `app_<instance>.secret` does not exist, `Mastodon.create_app(mastodon_username, api_base_url='https://<instance>', to_file='app_<instance>.secret')` is called. A falsy return prints `Failed to create the application on instance <instance>` and exits with code 1. A truthy return prints `Successfully created the application on instance <instance>`.
4. **Client construction.** `Mastodon(access_token=..., api_base_url='https://<instance>')` is constructed inside a `try`/`except Exception`. Failure prints `ERROR: Failed to log <username> into <instance>: <exception>` and exits with code 2.
5. **Facts read.** `open(facts_file_path, 'r').readlines()` inside a bare `except`. Failure prints `ERROR: Failed to read the file: <path>` and exits with code 1.
6. **Fact selection.** `random.choice(facts)` inside a `while random_fact is None` loop. Because `random.choice` never returns `None` for a non-empty list, the loop executes exactly once. An empty facts file raises `IndexError` (unhandled).
7. **Media URL extraction.** `re.finditer(r"https://[a-zA-Z0-9%\./_\-]*", random_fact)` scans the selected fact. Each match is retained only if it ends with `.gif`, `.jpg`, `.jpeg`, `.png`, or `.webp` (case-sensitive suffix check). Retained URLs are printed (`URL <url>`) and appended to `media_urls`.
8. **Media download and upload.** For each URL in `media_urls`: skip if the value is `None`, `'None'`, or `''`; remove the URL from `random_fact` via `str.replace`; print ` > Uploading media to Mastodon: <url>`; obtain a user agent from `UserAgent().firefox`; `requests.get(media_url, headers={'User-Agent': user_agent})`; `media.raise_for_status()`; `mastodon_api.media_post(media.content, mime_type=media.headers.get('content-type'))`; append `media_posted['id']` to `toot_media`; print `   > SUCCESS! <id>`. Any exception prints `   > FAILURE! <exception>` and is re-raised, terminating the process.
9. **Text transformation.** `random_fact` is stripped (`lstrip().rstrip()`), passed to `text_replacements.apply(random_fact, language)`, the literal sequence `\n` (backslash-n) is replaced with a real newline via `toot_body.replace(r'\n', '\n')`, and runs of spaces are collapsed via `re.sub(r'\ \ *', ' ', toot_body)`.
10. **Tag assembly.** `dynamic_tags.get(toot_body, language)` is called. `tags_to_add` and the dynamic result are concatenated into `all_tags_to_add` (each prefixed with a space when non-empty). If the concatenation is non-empty, it is split on spaces and filtered: tokens without `#` are kept verbatim; tokens with `#` are kept only when the lowercase tag followed by a space appears in neither the lowercase body plus a trailing space nor the accumulated filtered string plus a trailing space. The filtered string is stripped and appended to `toot_body` after `'\n\n'`.
11. **Publication.** The fact body is printed (` > Posting fact:\n<fact>`), then `mastodon_api.status_post(toot_body, in_reply_to_id=None, media_ids=toot_media, sensitive=False, visibility='public', spoiler_text=None)` is called. Exceptions are unhandled and produce a traceback.
12. **Exit.** The process ends with code 0 on success.

## Data transformations

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Fact selection | All fact lines | Uniform random choice | One fact string |
| Media extraction | Fact string | Regex URL scan plus suffix filter | List of media URLs |
| Media removal | Fact string plus URL list | `str.replace(url, '')` per URL | Fact string without media URLs |
| Text transformation | Stripped fact | `text_replacements.apply` | Transformed body |
| Escape conversion | Transformed body | `r'\n'` to newline | Body with real newlines |
| Whitespace collapse | Body with newlines | `re.sub(r'\ \ *', ' ')` | Body with single spaces |
| Tag filtering | Static tags, dynamic tags, body | Split, deduplicate against body and self | Filtered tag string |
| Body assembly | Body plus tags | Append `'\n\n' + tags` | Final toot body |

## State access

- **Reads:** the facts file (argument 1) and `app_<instance>.secret` (created in stage 3 if absent).
- **Writes:** `app_<instance>.secret` (first run only) and standard output.
- **Holds in memory:** the full facts list, the selected fact, downloaded media bytes, uploaded media IDs, and the final body. Nothing is persisted between stages except the secret file.

## Failure ownership

The entry point owns every failure path. There are exactly three termination behaviours:

| Trigger | Behaviour | Exit code |
|---------|-----------|-----------|
| `create_app` returns falsy | Print failure message, `sys.exit(1)` | 1 |
| Facts file unreadable | Print error, `sys.exit(1)` | 1 |
| `Mastodon(...)` constructor raises | Print error, `sys.exit(2)` | 2 |
| Media download or upload raises | Print `FAILURE!`, re-raise | Unhandled traceback (non-zero) |
| `status_post` raises | Unhandled | Unhandled traceback (non-zero) |
| Missing CLI argument | `IndexError` | Unhandled traceback (non-zero) |
| Empty facts file | `IndexError` from `random.choice` | Unhandled traceback (non-zero) |

See [Error handling](../error-handling.md) for the taxonomy and consequences.

## Dependants

Nothing depends on the entry point. It is the root of the dependency graph. The two helper modules are its dependants in the import sense but are consumed, not depended upon, by other code.

## Modification impact

- Changing the argument order or count breaks every existing scheduler invocation. Treat as incompatible; see [Compatibility contracts](../../ARCHITECTURE.md#-compatibility-contracts).
- Changing the media suffix list changes which fact URLs become attachments.
- Changing the tag filtering logic changes the published hashtag set.
- Changing the publication parameters (`visibility`, `sensitive`, `spoiler_text`) changes the published status semantics.
- Adding stages after media upload but before `status_post` affects the published body; adding stages after `status_post` has no effect on the post.
