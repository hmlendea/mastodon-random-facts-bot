# Documentation Index

Last reviewed: 2026-11-09. Owner: repository maintainer (hmlendea). Coverage status: complete for the current single-file pipeline architecture; no test suite or CI workflow exists to document.

## Repository summary

Mastodon Random Facts Bot is a Python console pipeline that selects one fact from an operator-maintained local file, transforms its text, downloads and uploads any embedded media, and publishes the result as a public Mastodon status. It is invoked periodically by an external scheduler such as a `systemd` timer. This documentation set complements the root `ARCHITECTURE.md` and provides component deep dives, execution flows, contracts, and operational guidance.

## Root document map

The following documents reside at the repository root and are not duplicated under `docs/`:

- [ARCHITECTURE.md](../ARCHITECTURE.md) — system context, architectural style, runtime process, components, data architecture, interfaces, dependency direction, deployment, compatibility contracts, testing, constraints, extension points, and source map.
- [SECURITY.md](../SECURITY.md) — supported versions, vulnerability reporting route, and security scope.
- [PRIVACY.md](../PRIVACY.md) — data categories, processing, storage, retention, external processing, and contact.
- ROADMAP.md — planning document when present at the repository root.
- [LICENSE](../LICENSE) — GNU General Public License v3.0 or later.
- [README.md](../README.md) — capabilities, usage, deployment example, contributing, privacy, security, code of conduct, and architecture summary.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — contribution workflow, prerequisites, and pull request guidelines.
- [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) — conduct standards for project spaces.

## Documentation catalogue

### Orientation

- [Quick start](./quick-start.md) — install dependencies, configure arguments, and run one posting cycle.
- [Repository overview](./repository-overview.md) — purpose, scope, entry points, and invocation model.
- [Repository structure](./repository-structure.md) — source tree layout and module organisation.

### Architecture and components

- [Architecture](./architecture.md) — high-level architecture narrative that complements the root `ARCHITECTURE.md`.
- [Components: entry point and orchestration](./components/entry-point-and-orchestration.md) — `mastodon-random-facts-bot.py` responsibilities, pipeline stages, and failure ownership.
- [Components: text replacements](./components/text-replacements.md) — the `text_replacements.apply` extension contract.
- [Components: dynamic tags](./components/dynamic-tags.md) — the `dynamic_tags.get` extension contract.
- [Components: integration models](./components/integration-models.md) — Mastodon API, media download, and user agent models.

### Flows and behaviour

- [Flows: startup and posting cycle](./flows/startup-and-posting-cycle.md) — end-to-end execution from process launch to status publication.
- [Flows: media handling](./flows/media-handling.md) — URL extraction, download, upload, and body sanitisation.
- [Flows: text transformation and tag assembly](./flows/text-transformation-and-tag-assembly.md) — replacement, escaping, whitespace normalisation, and tag filtering.
- [Behaviour: fact selection and posting](./behaviour/fact-selection-and-posting.md) — user-facing posting behaviour, visibility, and deduplication rules.

### Data, state, and dependencies

- [Data model](./data-model.md) — facts file, secret file, in-memory payloads, and remote Mastodon objects.
- [State and persistence](./state-and-persistence.md) — what persists, where, and for how long.
- [Dependencies](./dependencies.md) — declared and actual third-party dependencies and their integration boundaries.
- [Integrations](./integrations.md) — Mastodon API and external media hosts.

### Cross-cutting concerns

- [Configuration](./configuration.md) — the six command-line arguments, secret file contract, and precedence.
- [Concurrency and scheduling](./concurrency-and-scheduling.md) — sequential execution model and scheduler interaction.
- [Error handling](./error-handling.md) — failure taxonomy, exit codes, and recovery model.
- [Logging](./logging.md) — standard output signals, their meaning, and diagnostic gaps.
- [Security](./security.md) — trust boundaries, secret handling, and threat model; complements root `SECURITY.md`.

### Design knowledge

- [Design decisions](./design-decisions.md) — consequential choices and their rationale.
- [Invariants](./invariants.md) — system-wide contracts that must remain true.
- [API usage examples](./api-usage-examples.md) — concrete Mastodon API call shapes used by the bot.

### Operations

- [Build and deployment](./build-and-deployment.md) — dependency installation and `systemd` deployment model.
- [Testing](./testing.md) — verification approach and coverage gaps.
- [Troubleshooting](./troubleshooting.md) — common failures and their resolution.
- [FAQ](./faq.md) — frequently asked questions.

### Maintenance

- [Change guide](./change-guide.md) — how to modify common areas safely.
- [Ambiguities and open questions](./ambiguities-and-open-questions.md) — unresolved items and known gaps.
- [Documentation maintenance](./documentation-maintenance.md) — how to keep this documentation set current.

## Navigation aids

- **Start here:** read [Quick start](./quick-start.md), then [Repository overview](./repository-overview.md), then [Architecture](./architecture.md).
- **Deep dive (component owners):** [Components: entry point and orchestration](./components/entry-point-and-orchestration.md), [Components: text replacements](./components/text-replacements.md), [Components: dynamic tags](./components/dynamic-tags.md), [Components: integration models](./components/integration-models.md).
- **Flows (debuggers):** [Startup and posting cycle](./flows/startup-and-posting-cycle.md), [Media handling](./flows/media-handling.md), [Text transformation and tag assembly](./flows/text-transformation-and-tag-assembly.md).
- **Contracts:** [Invariants](./invariants.md), [Configuration](./configuration.md), [Error handling](./error-handling.md).
