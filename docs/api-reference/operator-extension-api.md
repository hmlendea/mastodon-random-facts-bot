# Operator extension API

This document defines the two internal APIs an operator may implement to customise bot behaviour without modifying the orchestration script. Both are imported directly by the entry point; there is no plugin discovery mechanism.

## `text_replacements.apply(text, language)`

### Contract

| Aspect | Specification |
|--------|---------------|
| Module | `text_replacements` |
| Function | `apply` |
| Parameters | `text` (`str`): the stripped fact text; `language` (`str`): the sixth CLI argument |
| Return | `str`: the transformed text |
| Called | Once per posting cycle, after stripping, before `\n` unescaping |
| Shipped behaviour | Identity (returns `text` unchanged) |

### Requirements

1. Preserve the function name `apply`.
2. Preserve the two-parameter signature `(text, language)`.
3. Return a string.
4. Import only the standard library.
5. Remain deterministic and side-effect-free.

### Example: locale-specific normalisation

```python
import re

def apply(text, language):
    if language == 'ro':
        text = re.sub('Rom[aâ]nia', '🇷🇴#Romania', text)
    return text
```

### Example: placeholder substitution

```python
def apply(text, language):
    return text.replace('{instance}', 'example.social')
```

## `dynamic_tags.get(text, language)`

### Contract

| Aspect | Specification |
|--------|---------------|
| Module | `dynamic_tags` |
| Function | `get` |
| Parameters | `text` (`str`): the transformed toot body; `language` (`str`): the sixth CLI argument |
| Return | `str` (space-separated tags, for example `' #Test #Example'`) or `None` when no tags apply |
| Called | Once per posting cycle, after text transformation, before static tag concatenation |
| Shipped behaviour | Always returns `None` |

### Requirements

1. Preserve the function name `get`.
2. Preserve the two-parameter signature `(text, language)`.
3. Return a string or `None`.
4. Import only the standard library.
5. Remain deterministic and side-effect-free.

### Example: content-derived tags

```python
import re

def get(text, language):
    tags = ''
    if re.search(r'\btest\b', text, re.IGNORECASE):
        tags = tags + ' #Test'
    if language == 'ro':
        tags = tags + ' #Romania'
    tags = re.sub('^\s*', '', tags)
    return tags if tags != '' else None
```

## Interaction with entry-point filtering

The tag string returned by `dynamic_tags.get` is concatenated with the static `tags_to_add` argument and then filtered by the entry point:

- Tokens without `#` are kept verbatim.
- Hashtags already present in the body are dropped.
- Duplicate hashtags within the combined set are dropped.
- Matching is case-insensitive; original casing is preserved.

Operators do not need to perform their own deduplication; the entry point handles it.

## Failure semantics

An exception raised by either hook propagates unhandled and terminates the process before publication. No status is published when a hook fails. This preserves the invariant that publication occurs only on complete pipeline success.

## Versioning

The hook signatures are part of the operator-facing contract. Changing a signature is a compatibility-breaking change for every operator who has customised these modules. See [Compatibility contracts](../../ARCHITECTURE.md#-compatibility-contracts) in the root architecture document.
