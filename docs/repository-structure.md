# Repository structure

The repository is deliberately small: one orchestration script, two operator-editable extension modules, a dependency manifest, and documentation. There are no packages, no tests, no CI configuration, and no build system.

## Source tree

```
mastodon-random-facts-bot/
├── .github/
│   └── FUNDING.yml                 # Funding platform configuration
├── docs/                           # This documentation set
│   ├── api-reference/              # Mastodon API usage reference
│   ├── behaviour/                  # User-facing behaviour documentation
│   ├── components/                 # Per-component deep dives
│   ├── flows/                      # End-to-end execution flows
│   └── *.md                        # Cross-cutting and operational documents
├── .gitignore                      # Ignores secrets, shells, caches, build output
├── ARCHITECTURE.md                 # Root architecture documentation
├── CODE_OF_CONDUCT.md              # Community conduct standards
├── CONTRIBUTING.md                 # Contribution workflow
├── LICENSE                         # GNU GPL v3.0 or later
├── PRIVACY.md                      # Privacy and data handling statement
├── README.md                       # Project front page
├── SECURITY.md                     # Vulnerability reporting and scope
├── dynamic_tags.py                 # Dynamic tag derivation extension point
├── mastodon-random-facts-bot.py    # Entry point and pipeline orchestration
├── requirements.txt                # Declared third-party dependencies
└── text_replacements.py            # Text transformation extension point
```

## Module organisation

| Path | Role | Imported by |
|------|------|-------------|
| `mastodon-random-facts-bot.py` | Entry point; owns all orchestration, network interaction, and pipeline stages | Not imported; executed directly |
| `text_replacements.py` | Operator-editable text transformation hook exposing `apply(text, language)` | `mastodon-random-facts-bot.py` |
| `dynamic_tags.py` | Operator-editable dynamic tag derivation hook exposing `get(text, language)` | `mastodon-random-facts-bot.py` |
| `requirements.txt` | Declared runtime dependencies | Consumed by `pip` |

## Ignored paths

The [../.gitignore](../.gitignore) file excludes runtime and tooling artefacts from version control. The rules material to architecture are:

- `*.secret` — excludes the bot-created `app_<instance>.secret` application credential file.
- `*.sh` — excludes operator-written launcher and scheduler helper scripts.
- `*.db`, `*.lst` — exclude optional local data files an operator may introduce.
- `docs/_build/` — excludes generated documentation build output.
- Standard Python exclusions (`__pycache__/`, `*.py[cod]`, `*.egg-info/`, `.pytest_cache/`, and similar).

## Absent directories

The following directories from the conventional documentation layout do not exist and are not required by the current architecture:

- `docs/api-reference/` exists but contains only the Mastodon API usage reference; there are no controllers because the bot exposes no HTTP API of its own.
- There is no `tests/` directory, no `ci/` directory, and no `.github/workflows/` directory.
- There is no `examples/` or `samples/` directory.

## Conventions

- File names are kebab-case for the entry point and snake_case for the importable Python modules.
- Documentation files are kebab-case Markdown.
- The entry point filename embeds the project name and the `.py` extension; it is executed with `python mastodon-random-facts-bot.py`.
