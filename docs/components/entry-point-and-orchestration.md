# Entry point and orchestration

This document deep-dives [mastodon-random-facts-bot.py](../../mastodon-random-facts-bot.py), the single executable component. It covers purpose, ownership, execution order, data transformations, state access, failure ownership, and modification impact. The root [ARCHITECTURE.md](../../ARCHITECTURE.md) defines the component's position in the wider system; this document explains its internals.

## Purpose and scope

The entry point owns the complete posting pipeline: argument interpretation, application secret bootstrap, Mastodon client construction, fact selection, media extraction and handling, text transformation delegation, tag assembly, and status publication. It is the only component that performs network I/O or file I/O.

It deliberately does not own:

- Text transformation rules (delegated to `text_replacements.apply`).
- Dynamic tag derivation (delegated to `dynamic_tags.get`).
- Configuration constants (owned by `config.py`).
- Scheduling (owned by the external scheduler).
- Fact content (owned by the operator's facts file).

## Location and invocation

- Path: `mastodon-random-facts-bot.py` (repository root).
- Invocation: `python mastodon-random-facts-bot.py <facts_file> <instance> <username> <access_token> <tags> <language>`.
- Entry mechanism: the script defines focused functions and a `main()` orchestrator, invoked through the `if __name__ == '__main__':` guard at the end of the file. There is no argument parser.

## Function decomposition

The pipeline is expressed as small single-responsibility functions assembled by `main()`:

| Function | Responsibility |
|----------|----------------|
| `read_arguments` | Binds the six positional arguments and returns them as a tuple |
| `ensure_application_registration` | Creates the application secret file when absent |
| `create_mastodon_client` | Constructs the Mastodon client, exiting with code 2 on failure |
| `read_facts` | Reads the facts file into a list of lines, exiting with code 1 on failure |
| `select_random_fact` | Selects one fact uniformly at random |
| `extract_media_urls` | Scans the fact for supported media URLs |
| `download_and_upload_media_item` | Downloads and uploads a single media item, returning its ID |
| `download_and_upload_media` | Iterates the media URLs, removing each from the fact and collecting IDs |
| `transform_fact_body` | Applies operator replacements, escape conversion, and whitespace collapse |
| `filter_tags` | Splits, deduplicates, and reassembles the tag string |
| `build_tag_block` | Concatenates static and dynamic tags into a filtered block, or `None` when empty |
| `publish_status` | Prints the fact and posts the status |

## Execution order

`main()` runs the stages in the following fixed order. Branches are limited to the secret-file check, the media suffix filter, and the tag-presence checks.

1. **Imports.** Standard library (`os.path`, `random`, `re`, `sys`, `typing`), third-party (`mastodon.Mastodon`, `requests`, `fake_useragent.UserAgent`), local modules (`text_replacements`, `dynamic_tags`), and configuration constants from `config.py`.
2. **Argument capture.** `read_arguments` binds `sys.argv[1]` through `sys.argv[6]`, using the named index constants from `config.py`, to `facts_file_path`, `mastodon_instance`, `mastodon_username`, `mastodon_access_token`, `tags_to_add`, and `language`. There is no validation; a missing argument raises `IndexError`.
3. **Secret bootstrap.** `ensure_application_registration` returns immediately if `app_<instance>.secret` exists. Otherwise it calls `Mastodon.create_app(mastodon_username, api_base_url='https://<instance>', to_file='app_<instance>.secret')`. A falsy return prints `Failed to create the application on instance <instance>` and exits with code 1. A truthy return prints `Successfully created the application on instance <instance>`.
4. **Client construction.** `create_mastodon_client` constructs `Mastodon(access_token=..., api_base_url='https://<instance>')` inside a `try`/`except Exception`. Failure prints `ERROR: Failed to log <username> into <instance>: <exception>` and exits with code 2.
5. **Facts read.** `read_facts` calls `open(facts_file_path, 'r').readlines()` inside a `try`/`except Exception`. Failure prints `ERROR: Failed to read the file: <path>` and exits with code 1.
6. **Fact selection.** `select_random_fact` returns `random.choice(facts)`. An empty facts file raises `IndexError` (unhandled).
7. **Media URL extraction.** `extract_media_urls` scans the selected fact with `re.finditer(MEDIA_URL_PATTERN, fact)`. Each match is retained only if it ends with one of the extensions in `SUPPORTED_MEDIA_FILE_EXTENSIONS` (case-sensitive suffix check). Retained URLs are printed (`URL <url>`) and appended to the returned list.
8. **Media download and upload.** `download_and_upload_media` iterates the URL list: skip if the value is `None`, `'None'`, or `''`; remove the URL from the fact via `str.replace`; print ` > Uploading media to Mastodon: <url>`; delegate each item to `download_and_upload_media_item`, which obtains a user agent from `UserAgent().firefox`, issues `requests.get(media_url, headers={'User-Agent': user_agent})`, calls `raise_for_status()`, and passes the bytes and `content-type` header to `media_post`, returning `media_posted['id']`; append the ID and print `   > SUCCESS! <id>`. Any exception prints `   > FAILURE! <exception>` and is re-raised, terminating the process.
9. **Text transformation.** `main` strips the fact once (`fact_text.strip()`), then `transform_fact_body` passes it to `text_replacements.apply`, replaces the literal sequence `\n` (backslash-n) with a real newline, and collapses runs of spaces via `re.sub(SPACE_RUN_PATTERN, SINGLE_SPACE, ...)`.
10. **Tag assembly.** `build_tag_block` calls `dynamic_tags.get(body, language)`; `tags_to_add` and the dynamic result are concatenated (each prefixed with a space when non-empty). When the concatenation is empty, `None` is returned and no tag block is appended. Otherwise it is split on spaces and filtered by `filter_tags`: tokens without `#` are kept verbatim; tokens with `#` are kept only when the lowercase tag followed by a space appears in neither the lowercase body plus a trailing space nor the accumulated filtered string plus a trailing space. The filtered string is stripped and appended to the body after `'\n\n'` when it is not `None`.
11. **Publication.** `publish_status` prints ` > Posting fact:\n<stripped fact>`, then calls `mastodon_client.status_post(toot_body, in_reply_to_id=None, media_ids=media_ids, sensitive=STATUS_IS_SENSITIVE, visibility=STATUS_VISIBILITY, spoiler_text=None)`. Exceptions are unhandled and produce a traceback.
12. **Exit.** The process ends with code 0 on success.

## Data transformations

| Stage | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Fact selection | All fact lines | Uniform random choice | One fact string |
| Media extraction | Fact string | Regex URL scan plus suffix filter | List of media URLs |
| Media removal | Fact string plus URL list | `str.replace(url, '')` per URL | Fact string without media URLs |
| Stripping | Fact text | `str.strip()` | Stripped fact |
| Text transformation | Stripped fact | `text_replacements.apply` | Transformed body |
| Escape conversion | Transformed body | `r'\n'` to newline | Body with real newlines |
| Whitespace collapse | Body with newlines | `re.sub(SPACE_RUN_PATTERN, SINGLE_SPACE)` | Body with single spaces |
| Tag filtering | Static tags, dynamic tags, body | Split, deduplicate against body and self | Filtered tag string |
| Body assembly | Body plus tags | Append `'\n\n' + tags` when tags exist | Final toot body |

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

Nothing depends on the entry point. It is the root of the dependency graph. The `config` module and the two helper modules are its dependants in the import sense but are consumed, not depended upon, by other code.

## Modification impact

- Changing the argument order or count breaks every existing scheduler invocation. Treat as incompatible; see [Compatibility contracts](../../ARCHITECTURE.md#-compatibility-contracts).
- Changing the media suffix list (`SUPPORTED_MEDIA_FILE_EXTENSIONS` in `config.py`) changes which fact URLs become attachments.
- Changing the tag filtering logic changes the published hashtag set.
- Changing the publication parameters (`STATUS_VISIBILITY`, `STATUS_IS_SENSITIVE`, `spoiler_text`) changes the published status semantics.
- Adding stages after media upload but before `status_post` affects the published body; adding stages after `status_post` has no effect on the post.
