# Component: text replacements

This document deep-dives [text_replacements.py](../../text_replacements.py), the operator-editable text transformation extension point.

## Purpose

The module exists so that an operator can customise how fact text is rewritten before publication without touching the orchestration script. Typical uses include locale-specific normalisation, inserting hashtags into the body, or rewriting placeholders.

## Location and contract

- Path: `text_replacements.py` (repository root).
- Public symbol: `apply(text, language)`.
- Input: `text` (the stripped fact string), `language` (the sixth command-line argument).
- Output: the transformed text string.
- Called from: `mastodon-random-facts-bot.py`, immediately after stripping and before the `\n` escape conversion.

## Current implementation

```python
import re

def apply(text, language):
    # Apply your custom text replacements. For example:
    # text = text.replace('Oradea', 'Oradea')
    # text = re.sub('Rom[aâ]nia', '🇷🇴#Romania', text)
    return text
```

The shipped implementation is an identity function: it returns the input unchanged. The two commented lines are illustrative examples supplied by the template, not active behaviour. The `re` import is present to support regex-based replacements in operator customisations.

## Behavioural consequences

Because the shipped implementation is the identity function:

- The fact body published to Mastodon is byte-identical to the selected fact line, minus extracted media URLs, modulo the entry point's own `\n` conversion and space collapsing.
- The `language` argument has no effect on the published text until the operator adds language-conditional logic.
- No transformation, sanitisation, or validation occurs at this boundary.

## Dependencies

The module imports only `re` from the standard library. It must not import `mastodon`, `requests`, `fake_useragent`, the entry point, or `dynamic_tags`. This keeps it I/O-free and safe to edit in place.

## Lifetime and ownership

The module has no independent lifetime. It is imported once at entry-point startup and its `apply` function is called once per posting cycle. It is owned by the repository but intended to be edited by the operator.

## Extension contract

An operator revising this module must preserve:

1. The function name `apply`.
2. The two-parameter signature `(text, language)`.
3. A string return value.
4. Standard-library-only imports.
5. Deterministic, side-effect-free behaviour (the entry point calls it once and does not retry).

The `language` parameter is the designated mechanism for locale-specific behaviour. A correct multi-language implementation branches on `language` and returns the appropriately transformed text.

## Failure semantics

An exception raised inside `apply` propagates unhandled to the entry point and terminates the process before publication. Because the entry point wraps only the client constructor and the facts read in `try`/`except`, a transformation error produces a traceback, not a friendly message. The invariant that a status is published only when the complete pipeline succeeds is preserved.

## Modification impact

- Changing the signature breaks the entry point call site.
- Introducing I/O (network or file) violates the module boundary rule documented in [Architecture](../architecture.md) and the root [ARCHITECTURE.md](../../ARCHITECTURE.md).
- Introducing non-determinism (for example, time- or randomness-based replacement) makes the published body unpredictable across runs.
