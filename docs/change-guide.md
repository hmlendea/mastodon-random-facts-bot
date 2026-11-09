# Change guide

This document describes how to make common changes to the bot safely. It maps each change type to the files affected, the invariants at risk, and the verification steps.

## Change types

### Add a supported media suffix

**Files:** `mastodon-random-facts-bot.py` (suffix condition in the media loop).

**Invariants at risk:** I3 (no media URLs in published body) — a new suffix must be added to both the extraction filter and the removal logic (they share the same condition).

**Steps:**
1. Add the suffix to the `endswith` condition.
2. Test with a fact containing a URL with the new suffix.
3. Verify the URL is extracted, downloaded, uploaded, and removed from the published text.

**Verification:** Integration run on a test instance; check the published status has the attachment and no URL in the text.

### Add a new operator hook

**Files:** New module (for example `media_filters.py`), entry point import and call.

**Invariants at risk:** I6 (hook signatures stable) — the new hook must have a documented signature; I2 (publication only on complete success) — the hook must not swallow exceptions.

**Steps:**
1. Create the module with a single public function.
2. Import it in the entry point.
3. Call it at the appropriate pipeline stage.
4. Document the contract in [Operator extension API](./api-reference/operator-extension-api.md).

**Verification:** Unit test of the hook; integration run verifying the hook's effect on the published status.

### Change the tag filtering logic

**Files:** `mastodon-random-facts-bot.py` (filtering block).

**Invariants at risk:** I4 (no duplicate hashtags), I10 (tag block separator).

**Steps:**
1. Modify the filtering block.
2. Write unit tests covering: tag in body, duplicate tags, prefix collisions (`#art` vs `#artificial`), case variants, non-hashtag tokens.
3. Run the integration test.

**Verification:** Unit tests plus integration run; inspect the published status for correct tags.

### Change the publication parameters

**Files:** `mastodon-random-facts-bot.py` (`status_post` call).

**Invariants at risk:** I1 (at most one status per invocation) — do not add a second `status_post` call.

**Steps:**
1. Modify the `status_post` parameters (for example, `visibility`, `sensitive`, `spoiler_text`).
2. Document the change in [Behaviour: fact selection and posting](./behaviour/fact-selection-and-posting.md).
3. Run the integration test.

**Verification:** Integration run; inspect the published status attributes on the instance.

### Add a CLI argument

**Files:** `mastodon-random-facts-bot.py` (`sys.argv` binding), all scheduler invocations.

**Invariants at risk:** Compatibility contract (argument order and count). This is a **breaking change**.

**Steps:**
1. Add the argument binding.
2. Update every scheduler invocation (service unit, cron, wrapper scripts).
3. Update [Command-line interface](./api-reference/command-line-interface.md).
4. Update [Configuration](./configuration.md).
5. Bump the major version or document the migration.

**Verification:** Manual run with the new argument; verify scheduler logs show the updated invocation.

### Update a dependency

**Files:** `requirements.txt`.

**Invariants at risk:** Compatibility contracts documented in [Dependencies](./dependencies.md).

**Steps:**
1. Update the version constraint in `requirements.txt`.
2. Review the dependency's changelog for breaking changes.
3. Run the integration test on a test instance.
4. Update [Dependencies](./dependencies.md) if the API shape changed.

**Verification:** Integration run; verify registration, media upload, and publication all succeed.

### Modify an operator hook

**Files:** `text_replacements.py` or `dynamic_tags.py`.

**Invariants at risk:** I6 (hook signatures stable) — preserve the function name, parameters, and return type.

**Steps:**
1. Edit the hook implementation.
2. Keep standard-library-only imports.
3. Keep the function deterministic and side-effect-free.
4. Test with sample inputs.

**Verification:** Unit test of the hook; integration run verifying the effect.

### Change the facts file format

**Files:** Entry point (read and selection logic), operator documentation.

**Invariants at risk:** I7 (no local state between runs) — a richer format may tempt persistent state; resist unless justified.

**Steps:**
1. Define the new format (for example, JSON with metadata).
2. Update the read and selection logic.
3. Update [Data model](./data-model.md).
4. Provide a migration path for existing facts files.

**Verification:** Integration run with a facts file in the new format.

## General verification checklist

For any change:

- [ ] Read the affected files before editing.
- [ ] Identify the invariants at risk (see [Invariants](./invariants.md)).
- [ ] Make the smallest change that achieves the goal.
- [ ] Run the integration test on a test instance.
- [ ] Verify the published status matches expectations.
- [ ] Update affected documentation.
- [ ] Check the README sections that reference changed behaviour.

## What not to change without discussion

- The six-argument CLI contract (breaking for all operators).
- The hook signatures (breaking for all operator customisations).
- The stateless batch model (fundamental architectural decision).
- The no-retry policy (fundamental error-handling decision).
- The public visibility default (changes the bot's social contract).

Changes to these require a clear rationale, a migration plan, and a version bump. Open an issue to discuss before implementing.