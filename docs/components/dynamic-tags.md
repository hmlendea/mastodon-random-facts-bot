# Component: dynamic tags

This document deep-dives [dynamic_tags.py](../../dynamic_tags.py), the operator-editable dynamic tag derivation extension point.

## Purpose

The module exists so that an operator can derive hashtags from the content of the transformed fact body without touching the orchestration script. Typical uses include tagging posts that mention specific topics, places, or events.

## Location and contract

- Path: `dynamic_tags.py` (repository root).
- Public symbol: `get(text, language)`.
- Input: `text` (the transformed toot body, after `text_replacements.apply` and the entry point's escape and whitespace processing), `language` (the sixth command-line argument).
- Output: a string of space-separated tags (for example `' #Test #Example'`), or `None` when no tags apply.
- Called from: `mastodon-random-facts-bot.py`, after text transformation and before static tag concatenation.

## Current implementation

```python
import re

def get(text, language):
    tags = ''

    # Build your own custom dynamic tags. For example:
    # if ('test TeSt TEST' in text):
    #     tags = tags + ' #Test'

    tags = re.sub('^\s*', '', tags)

    if tags != '':
        return tags
    else:
        return None
```

The shipped implementation always returns `None`: `tags` is initialised to the empty string, the commented example is inactive, and the `re.sub` call strips leading whitespace from an empty string. The `if tags != ''` branch therefore never fires.

## Behavioural consequences

Because the shipped implementation returns `None`:

- The entry point's `if dynamic_tags_to_add:` check is false, so no dynamic tags are appended.
- The published hashtag set consists solely of the static `tags_to_add` command-line argument, filtered against the body.
- The `language` argument has no effect on tags until the operator adds language-conditional logic.

## Dependencies

The module imports only `re` from the standard library. It must not import `mastodon`, `requests`, `fake_useragent`, the entry point, or `text_replacements`. This keeps it I/O-free and safe to edit in place.

## Lifetime and ownership

The module has no independent lifetime. It is imported once at entry-point startup and its `get` function is called once per posting cycle. It is owned by the repository but intended to be edited by the operator.

## Extension contract

An operator revising this module must preserve:

1. The function name `get`.
2. The two-parameter signature `(text, language)`.
3. A return value of either a tag string or `None`.
4. Standard-library-only imports.
5. Deterministic, side-effect-free behaviour.

The `None`-for-empty contract is load-bearing: the entry point uses `if dynamic_tags_to_add:` to decide whether to concatenate. Returning an empty string instead of `None` is also falsy and therefore safe, but returning `None` matches the shipped template and is the documented convention.

## Interaction with tag filtering

The returned tag string is concatenated with the static `tags_to_add` argument into `all_tags_to_add`. The entry point then splits the concatenation on spaces and filters each token:

- Tokens without `#` are kept verbatim.
- Tokens with `#` are kept only when the lowercase tag followed by a space appears in neither the lowercase body plus a trailing space nor the accumulated filtered string plus a trailing space.

Consequently, a dynamic tag already present in the fact body is not duplicated. A dynamic tag identical to a static tag is also not duplicated. The filtering is case-insensitive but preserves the original casing in the output.

## Failure semantics

An exception raised inside `get` propagates unhandled to the entry point and terminates the process before publication. The invariant that a status is published only when the complete pipeline succeeds is preserved.

## Modification impact

- Changing the signature breaks the entry point call site.
- Returning a non-string, non-`None` value breaks the concatenation logic.
- Introducing I/O violates the module boundary rule documented in [Architecture](../architecture.md) and the root [ARCHITECTURE.md](../../ARCHITECTURE.md).
