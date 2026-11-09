# Documentation maintenance

This document describes how the documentation set is organised, how to keep it synchronised with the code, and the conventions for editing it.

## Documentation inventory

| Document | Purpose | Update trigger |
|----------|---------|----------------|
| [INDEX.md](./INDEX.md) | Documentation entry point and reading guide | Add or remove a document |
| [quick-start.md](./quick-start.md) | First-run guide | CLI change, dependency change, deployment change |
| [repository-overview.md](./repository-overview.md) | Project purpose and scope | Feature change affecting purpose |
| [repository-structure.md](./repository-structure.md) | File tree and roles | Add, remove, or rename a file |
| [architecture.md](./architecture.md) | Architectural rationale | Architectural decision change |
| [components/entry-point-and-orchestration.md](./components/entry-point-and-orchestration.md) | Entry point internals | Pipeline stage change |
| [components/text-replacements.md](./components/text-replacements.md) | Text hook contract | Hook signature or behaviour change |
| [components/dynamic-tags.md](./components/dynamic-tags.md) | Tag hook contract | Hook signature or behaviour change |
| [components/integration-models.md](./components/integration-models.md) | External API call shapes | Dependency or API change |
| [flows/startup-and-posting-cycle.md](./flows/startup-and-posting-cycle.md) | End-to-end execution | Pipeline order change |
| [flows/media-handling.md](./flows/media-handling.md) | Media sub-flow | Media logic change |
| [flows/text-transformation-and-tag-assembly.md](./flows/text-transformation-and-tag-assembly.md) | Text and tag sub-flow | Transformation or tag logic change |
| [behaviour/fact-selection-and-posting.md](./behaviour/fact-selection-and-posting.md) | User-facing behaviour | Published status shape change |
| [api-reference/INDEX.md](./api-reference/INDEX.md) | API reference index | Add or remove an API document |
| [api-reference/mastodon-api-usage.md](./api-reference/mastodon-api-usage.md) | Mastodon API calls | API call change |
| [api-reference/operator-extension-api.md](./api-reference/operator-extension-api.md) | Hook contracts | Hook change |
| [api-reference/command-line-interface.md](./api-reference/command-line-interface.md) | CLI definition | Argument change |
| [configuration.md](./configuration.md) | Configuration model | Configuration mechanism change |
| [concurrency-and-scheduling.md](./concurrency-and-scheduling.md) | Concurrency model | Concurrency or scheduling change |
| [error-handling.md](./error-handling.md) | Error taxonomy | Error path change |
| [logging.md](./logging.md) | Logging model | Output change |
| [security.md](./security.md) | Security posture | Security-relevant change |
| [data-model.md](./data-model.md) | Data entities and lifecycle | Data shape change |
| [state-and-persistence.md](./state-and-persistence.md) | Persistent state | State mechanism change |
| [dependencies.md](./dependencies.md) | Dependency inventory | Dependency change |
| [integrations.md](./integrations.md) | External integrations | Integration change |
| [design-decisions.md](./design-decisions.md) | Decision log | New or revised decision |
| [invariants.md](./invariants.md) | Guaranteed properties | Invariant change |
| [api-usage-examples.md](./api-usage-examples.md) | Concrete API examples | API call change |
| [build-and-deployment.md](./build-and-deployment.md) | Deployment guide | Deployment mechanism change |
| [testing.md](./testing.md) | Testing posture | Test infrastructure change |
| [troubleshooting.md](./troubleshooting.md) | Failure diagnosis | Failure mode change |
| [faq.md](./faq.md) | Frequently asked questions | Common question emerges |
| [change-guide.md](./change-guide.md) | How to make changes | Change process change |
| [ambiguities-and-open-questions.md](./ambiguities-and-open-questions.md) | Known ambiguities | New ambiguity discovered or resolved |

## Synchronisation rules

1. **Code change first, documentation second.** Make the code change, verify it, then update every document whose update trigger matches.
2. **One source of truth.** Each fact is documented in exactly one place. Other documents link to it; they do not repeat it.
3. **Root documents are authoritative for structure.** [ARCHITECTURE.md](../ARCHITECTURE.md) defines the canonical component catalogue and diagrams. `docs/architecture.md` adds rationale only.
4. **README sections mirror policy documents.** When a policy document changes, update the corresponding README section to match the template.
5. **Cross-references use relative paths.** Links between documents use relative paths (for example, `./error-handling.md`, `../ARCHITECTURE.md`). Verify links before committing.

## Conventions

- **File naming:** kebab-case (for example, `error-handling.md`).
- **Headings:** `#` for the document title, `##` for sections, `###` for subsections.
- **Code blocks:** fenced with the language identifier (```python, ```bash, ```ini, ```mermaid).
- **Tables:** GitHub-flavoured Markdown pipe tables.
- **British spelling:** colour, behaviour, normalisation, licence (noun).
- **Emoji in headings:** only where the root template documents require them (policy documents). `docs/` documents use plain headings.
- **No HTML comments:** remove template comments before publishing.
- **No placeholders:** replace all template placeholders with concrete content.

## Review checklist

Before committing a documentation change:

- [ ] The document's update trigger matches the code change.
- [ ] No other document now contradicts this one.
- [ ] All relative links resolve.
- [ ] Code examples match the current code.
- [ ] Tables are well-formed.
- [ ] British spelling is used.
- [ ] No template placeholders remain.
- [ ] No HTML comments remain.

## Adding a new document

1. Create the file in the appropriate directory (`docs/`, `docs/components/`, `docs/flows/`, `docs/behaviour/`, `docs/api-reference/`).
2. Use kebab-case naming.
3. Start with a `#` title and a one-paragraph purpose statement.
4. Add the document to [INDEX.md](./INDEX.md) and to the inventory table above.
5. Link to it from related documents.

## Removing a document

1. Verify no other document links to it (search the `docs/` tree).
2. Remove the file.
3. Remove it from [INDEX.md](./INDEX.md) and from the inventory table above.
4. Remove or update links in related documents.

## Documentation debt

When documentation falls out of sync with the code:

1. Open an issue describing the discrepancy.
2. Link the issue from the affected document (for example, in a note at the top).
3. Fix the documentation in the same change that fixes the code, or in a follow-up change linked to the issue.

See [Ambiguities and open questions](./ambiguities-and-open-questions.md) for the current documentation debt register.