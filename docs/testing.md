# Testing

This document describes the testing posture of the repository: what exists, what does not, and how to test changes safely.

## Current state

The repository contains **no tests**:

- No test files (`test_*.py`, `*_test.py`, `tests/` directory).
- No test runner configuration (`pytest.ini`, `tox.ini`, `setup.cfg`).
- No CI pipeline (`.github/workflows/` contains only `FUNDING.yml`).
- No test dependencies in `requirements.txt`.

## Why no tests

The design decisions document records the rationale:

- The bot is a simple linear script with two operator hooks.
- The core logic is the pipeline order, which is visible by reading the entry point.
- Testing would require mocking Mastodon, media hosts, and the scheduler.
- The operator tests by running the bot manually or observing the timeline.

## How to test changes safely

### 1. Dry run with a test instance

Use a throwaway Mastodon account on a test instance (for example, a local instance or a sandbox):

```bash
python mastodon-random-facts-bot.py facts-test.txt test.instance.local testbot TEST_TOKEN " #Test" en
```

Verify:
- The status appears on the test instance.
- Media URLs are removed from the published text.
- Tags are appended correctly.
- No duplicate hashtags.

### 2. Unit test the operator hooks

The hooks are pure functions and can be tested without network access:

```python
# test_text_replacements.py
import text_replacements

def test_identity():
    assert text_replacements.apply('hello', 'en') == 'hello'

def test_language_branch():
    # Add operator-specific assertions here
    pass
```

```python
# test_dynamic_tags.py
import dynamic_tags

def test_returns_none():
    assert dynamic_tags.get('hello', 'en') is None
```

Run with `pytest` (not a declared dependency; install separately).

### 3. Test the regex extraction

```python
import re

def test_media_url_extraction():
    fact = 'See https://example.com/img.png and https://example.com/doc.pdf'
    urls = [m.group(0) for m in re.finditer(r"https://[a-zA-Z0-9%\./_\-]*", fact)]
    media = [u for u in urls if u.endswith(('.gif', '.jpg', '.jpeg', '.png', '.webp'))]
    assert media == ['https://example.com/img.png']
```

### 4. Test the tag filtering

```python
def test_tag_filtering():
    toot_body = 'Fact about art\n\n'
    all_tags = ' #art #Art #design'
    filtered = ''
    for tag in all_tags.split(' '):
        if '#' not in tag:
            filtered += ' ' + tag
            continue
        if (tag.lower() + ' ' not in toot_body.lower() + ' ' and
            tag.lower() + ' ' not in filtered.lower() + ' '):
            filtered += ' ' + tag
    assert filtered.strip() == '#design'
```

### 5. Integration test with a real instance

For changes to the entry point, run the full pipeline against a real instance with a dedicated test account:

1. Prepare a facts file with one known fact and one media URL.
2. Run the bot.
3. Verify the published status: body text, media attachment, tags.
4. Verify the secret file was created (first run) or reused (subsequent runs).

## What to test before merging

| Change type | Minimum test |
|-------------|--------------|
| Entry point pipeline order | Full integration run on test instance |
| Media suffix list | Regex extraction test with new suffix |
| Tag filtering logic | Unit test with edge cases (prefix tags, case variants) |
| `text_replacements.py` | Unit test of `apply` with sample inputs |
| `dynamic_tags.py` | Unit test of `get` with sample inputs |
| Dependency update | Full integration run on test instance |
| CLI argument change | Verify all scheduler invocations updated |

## Limitations

- No automated regression detection.
- No coverage measurement.
- No property-based testing.
- No fuzzing of the regex or tag filtering.
- No mocking framework in use.

## Recommendation

If the project grows (more pipeline stages, more hooks, more operators), consider:

1. Extracting the pipeline into testable functions.
2. Adding `pytest` and a `tests/` directory.
3. Adding a CI workflow that runs unit tests on push.
4. Adding integration tests against a test instance with a dedicated token.

Until then, manual testing on a test instance is the pragmatic approach.