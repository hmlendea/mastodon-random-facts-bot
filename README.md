[![Donate](https://img.shields.io/badge/-%E2%99%A5%20Donate-%23ff69b4)](https://hmlendea.go.ro/funding)
[![Latest Release](https://img.shields.io/github/v/release/hmlendea/mastodon-random-facts-bot)](https://github.com/hmlendea/mastodon-random-facts-bot/releases/latest)
[![License](https://img.shields.io/github/license/hmlendea/mastodon-random-facts-bot)](https://github.com/hmlendea/mastodon-random-facts-bot/blob/master/LICENSE)

# Mastodon Random Facts Bot

A Python console pipeline that selects a random fact from an operator-maintained local file, transforms its text, downloads and uploads any embedded media, and publishes the result as a public Mastodon status.

## 📑 Table of Contents

- [Capabilities](#capabilities)
- [Use Cases](#use-cases)
- [Usage](#usage)
- [Known Limitations](#known-limitations)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Installation from Source](#installation-from-source)
- [Configuration](#configuration)
  - [Command-Line Options](#command-line-options)
- [Integrations](#integrations)
- [Authentication and Authorisation](#authentication-and-authorisation)
- [Privacy and Data](#privacy-and-data)
  - [Data Locations](#data-locations)
  - [Telemetry Controls](#telemetry-controls)
- [Development](#development)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Run](#run)
  - [Test](#test)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [Related Projects](#related-projects)
- [Security](#security)
- [Project Engagement](#project-engagement)
- [License](#license)

## ✨ Capabilities

- Random selection of one fact per invocation from a local file.
- Automatic media handling: URLs embedded in facts are downloaded, uploaded to Mastodon, attached to the status, and removed from the published text.
- Operator-customisable text transformation and dynamic tag derivation through two helper modules.
- Static tag injection through a command-line argument, with deduplication against the fact body.
- First-run application registration persisted in a local secret file.

## 🎯 Use Cases

- **Operators** running scheduled fact posting to a Mastodon instance via an external scheduler (for example, a `systemd` timer).
- **Contributors** extending text transformation or dynamic tag logic by editing the operator-editable hook modules without touching the orchestration code.

## 🚀 Usage

```bash
python mastodon-random-facts-bot.py <facts_file> <instance> <username> <access_token> "<tags>" <language>
```

The six positional arguments, in order:

| Position | Argument | Purpose |
|----------|----------|---------|
| 1 | `facts_file` | Path to the local facts file |
| 2 | `instance` | Mastodon instance host, for example `mastodon.social` |
| 3 | `username` | Application name used for first-run registration |
| 4 | `access_token` | Mastodon access token with write scope |
| 5 | `tags` | Static hashtags to append; pass an empty string to disable |
| 6 | `language` | Language code consumed by the text replacement and dynamic tag modules |

On the first run for a given instance, the bot registers an application and writes `app_<instance>.secret` into the working directory. Subsequent runs reuse that file.

## ⚠️ Known Limitations

- Media URL suffix matching is case-sensitive; `.JPG` is not recognised.
- The media extraction regex truncates URLs at `?` or `#`; query strings and fragments are lost.
- No retry or backoff for transient failures (network blips, rate limits, media host downtime); the next scheduled run retries.
- No fact deduplication across runs; the same fact may be selected on consecutive invocations.
- The access token is passed as a command-line argument and is visible in the process table and scheduler logs during execution.
- No rate limit handling; a rate-limited API call terminates the run.
- No timeout configured on media downloads; a slow host may hang until the scheduler's `RuntimeMaxSec` kills the process.
- Publication parameters are hardcoded: `visibility='public'`, `sensitive=False`, `spoiler_text=None`, `in_reply_to_id=None`.

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.6 | 3.11+ |
| pip | Any recent version | Latest |
| Mastodon account | Access token with `write:statuses` and `write:media` scopes | Dedicated bot account with minimal scopes |
| Facts file | Newline-delimited text file with at least one line | UTF-8 encoded, one fact per line |

## 📦 Installation

### Installation from Source

```bash
git clone https://github.com/hmlendea/mastodon-random-facts-bot.git
cd mastodon-random-facts-bot
python -m pip install -r requirements.txt
```

## ⚙️ Configuration

### Command-Line Options

| Option | Value | Default | Description |
|--------|-------|---------|-------------|
| `facts_file` | Path to facts file | — | Required. Newline-delimited facts. |
| `instance` | Instance domain | — | Required. For example `mastodon.social`. |
| `username` | Account username | — | Required. Also used as application name. |
| `access_token` | User access token | — | Required. Must have write scope. |
| `tags` | Space-separated tags | — | Required. Quote when containing spaces; empty string disables. |
| `language` | Language code | — | Required. Passed to operator hooks (for example `en`, `ro`). |

There are no configuration files, environment variables, or defaults. All configuration arrives as six positional command-line arguments.

## 🔌 Integrations

| Integration | Compatibility | Purpose | Required |
|-------------|---------------|---------|----------|
| Mastodon instance | HTTPS, Mastodon API v1/v2 | Application registration, media upload, status publication | Yes |
| Arbitrary media hosts | HTTPS, direct image URLs | Media byte download | No (only when facts contain media URLs) |
| `fake_useragent` upstream | HTTPS (potential) | User agent data refresh | No (implicit, on first use) |

## 🔐 Authentication and Authorisation

| Role or Scope | Access | Intended Audience |
|---------------|--------|-------------------|
| `write:statuses` | Create public statuses | Bot operator |
| `write:media` | Upload media attachments | Bot operator |
| Application registration | `POST /api/v1/apps` | Bot (first run only) |

The user access token is supplied via the command line. The application secret file (`app_<instance>.secret`) is created on first run and reused thereafter.

## 🛡️ Privacy and Data

Mastodon Random Facts Bot posts a random fact to a Mastodon instance from a predefined list of facts. It handles the Mastodon access token and application secret file locally, and transmits fact content, tags, and media to the configured Mastodon instance.

For the detailed description of how the application handles privacy and personal data, see the [Privacy Statement](./PRIVACY.md).

The application processes the following data categories:

| Data | Purpose | Storage | Retention | Optional |
|------|---------|---------|-----------|----------|
| Mastodon instance URL | API endpoint configuration | Command-line argument | Operator-controlled | No |
| Mastodon username | Application registration | Command-line argument | Operator-controlled | No |
| Mastodon access token | Authentication with the Mastodon API | Command-line argument | Operator-controlled | No |
| Tags to add | Hashtags appended to posts | Command-line argument | Operator-controlled | Yes |
| Language code | Text replacement selection | Command-line argument | Operator-controlled | Yes |
| Facts file | Source of facts to post | Local file | Operator-controlled | No |
| Application secret file | Mastodon application credentials | Local file (`app_<instance>.secret`) | Until manually deleted | No |
| Media URLs in facts | Media upload to Mastodon | Downloaded to memory during upload | Not persisted | Yes |

### Data Locations

| Platform or Scope | Location | Contents |
|-------------------|----------|----------|
| Local deployment | Working directory | Application secret file, facts file |
| Local deployment | Standard output | Operation logs, posted fact content |

### Telemetry Controls

The application does not send telemetry, crash reports, or update checks to the project maintainers or external services beyond the verified Mastodon API integration.

## 🛠️ Development

### Requirements

- Python 3.6+
- pip package manager

### Setup

```bash
git clone https://github.com/hmlendea/mastodon-random-facts-bot.git
cd mastodon-random-facts-bot
python -m pip install -r requirements.txt
```

### Run

```bash
python mastodon-random-facts-bot.py <facts_file> <instance> <username> <access_token> "<tags>" <language>
```

### Test

The repository contains no automated test suite. Manual testing on a throwaway Mastodon instance is the recommended verification approach:

```bash
python mastodon-random-facts-bot.py facts-test.txt test.instance.local testbot TEST_TOKEN " #Test" en
```

Verify the status appears on the test instance, media URLs are removed from the published text, tags are appended correctly, and no duplicate hashtags appear.

## 🗂️ Project Structure

```
mastodon-random-facts-bot/
├── .github/
│   └── FUNDING.yml                 # Funding platform configuration
├── docs/                           # Documentation set
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

## 🏗️ Architecture

Mastodon Random Facts Bot is a single-process, sequential console pipeline that selects a random fact from a local file, transforms its text, downloads and uploads embedded media, and publishes a public Mastodon status.

See the [Architecture Documentation](./ARCHITECTURE.md) for the system context, principal components, runtime flows, ownership boundaries, dependencies, constraints, and extension points.

## 🚢 Deployment

The bot is deployed as a scheduled one-shot process. The repository documents a `systemd` timer and service pair:

### Service unit

Create `/etc/systemd/system/mastodon-random-facts-bot.service`:

```ini
[Unit]
Description=Mastodon random facts bot

[Service]
Type=oneshot
WorkingDirectory=/opt/mastodon-random-facts-bot
ExecStart=/usr/bin/python3 mastodon-random-facts-bot.py facts.txt mastodon.social mybot TOKEN " #Fact #Random" en
RuntimeMaxSec=60
```

### Timer unit

Create `/etc/systemd/system/mastodon-random-facts-bot.timer`:

```ini
[Unit]
Description=Run Mastodon random facts bot every 25 minutes

[Timer]
OnBootSec=15min
OnUnitActiveSec=25min

[Install]
WantedBy=timers.target
```

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mastodon-random-facts-bot.timer
sudo systemctl status mastodon-random-facts-bot.timer
```

### View logs

```bash
journalctl -u mastodon-random-facts-bot.service -f
```

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| [Quick start](./docs/quick-start.md) | Install dependencies, configure arguments, and run one posting cycle. |
| [Repository overview](./docs/repository-overview.md) | Purpose, scope, entry points, and invocation model. |
| [Repository structure](./docs/repository-structure.md) | Source tree layout and module organisation. |
| [Architecture](./docs/architecture.md) | High-level architecture narrative. |
| [Components: entry point and orchestration](./docs/components/entry-point-and-orchestration.md) | Pipeline stages and failure ownership. |
| [Components: text replacements](./docs/components/text-replacements.md) | The `text_replacements.apply` extension contract. |
| [Components: dynamic tags](./docs/components/dynamic-tags.md) | The `dynamic_tags.get` extension contract. |
| [Components: integration models](./docs/components/integration-models.md) | Mastodon API, media download, and user agent models. |
| [Flows: startup and posting cycle](./docs/flows/startup-and-posting-cycle.md) | End-to-end execution from process launch to status publication. |
| [Flows: media handling](./docs/flows/media-handling.md) | URL extraction, download, upload, and body sanitisation. |
| [Flows: text transformation and tag assembly](./docs/flows/text-transformation-and-tag-assembly.md) | Replacement, escaping, whitespace normalisation, and tag filtering. |
| [Behaviour: fact selection and posting](./docs/behaviour/fact-selection-and-posting.md) | User-facing posting behaviour, visibility, and deduplication rules. |
| [Data model](./docs/data-model.md) | Facts file, secret file, in-memory payloads, and remote Mastodon objects. |
| [State and persistence](./docs/state-and-persistence.md) | What persists, where, and for how long. |
| [Dependencies](./docs/dependencies.md) | Declared and actual third-party dependencies. |
| [Integrations](./docs/integrations.md) | Mastodon API and external media hosts. |
| [Configuration](./docs/configuration.md) | The six command-line arguments, secret file contract, and precedence. |
| [Concurrency and scheduling](./docs/concurrency-and-scheduling.md) | Sequential execution model and scheduler interaction. |
| [Error handling](./docs/error-handling.md) | Failure taxonomy, exit codes, and recovery model. |
| [Logging](./docs/logging.md) | Standard output signals, their meaning, and diagnostic gaps. |
| [Security](./docs/security.md) | Trust boundaries, secret handling, and threat model. |
| [Build and deployment](./docs/build-and-deployment.md) | Dependency installation and `systemd` deployment model. |
| [Testing](./docs/testing.md) | Verification approach and coverage gaps. |
| [Troubleshooting](./docs/troubleshooting.md) | Common failures and their resolution. |
| [FAQ](./docs/faq.md) | Frequently asked questions. |
| [Change guide](./docs/change-guide.md) | How to modify common areas safely. |
| [Design decisions](./docs/design-decisions.md) | Consequential choices and their rationale. |
| [Invariants](./docs/invariants.md) | System-wide contracts that must remain true. |
| [API usage examples](./docs/api-usage-examples.md) | Concrete Mastodon API call shapes used by the bot. |
| [Ambiguities and open questions](./docs/ambiguities-and-open-questions.md) | Unresolved items and known gaps. |
| [Documentation maintenance](./docs/documentation-maintenance.md) | How to keep this documentation set current. |

## 🩺 Troubleshooting

See [Troubleshooting Guide](./docs/troubleshooting.md) for diagnostic procedures and resolutions to recurring problems.

## ❓ FAQ

See the [Frequently Asked Questions](./docs/faq.md) for responses to frequently raised inquiries.

## 🤝 Contributing

You are welcome to submit any suggestion, feedback, or modification to this project.

When doing so, please:
- Maintain cross-platform compatibility
- Preserve the existing public contract unless a breaking change is intentional
- Submit focused pull requests that conform to the existing code style
- Maintain your branch synchronised with `master`
- Revise the documentation when functionality changes
- Properly test all modifications, including edge cases and error conditions
- Include tests for additional or modified functionality
- Raise a new [issue](https://github.com/hmlendea/mastodon-random-facts-bot/issues) for problems or suggestions

See the [Contributing Guidelines](./CONTRIBUTING.md) for details on how to report issues, suggest enhancements, and submit changes.

## 📜 Code of Conduct

See the [Code of Conduct](./CODE_OF_CONDUCT.md) for the standards of conduct expected in all project spaces.

## 🔒 Security

Mastodon Random Facts Bot handles Mastodon access tokens and application secret files locally. It transmits fact content and media to the configured Mastodon instance.

For information on reporting security vulnerabilities, see the [Security Policy](./SECURITY.md).

## 🔗 Related Projects

- [Mastodon RSS Bot](https://github.com/hmlendea/mastodon-rss-bot): A Mastodon bot that posts the entries from any RSS feed.

## 💝 Project Engagement

Discovered a problem or have a suggestion? [Open an issue](https://github.com/hmlendea/mastodon-random-facts-bot/issues)!

If you find this project useful, consider [funding it](https://hmlendea.go.ro/funding) or starring ⭐️ it on GitHub!

[![Donate](https://raw.githubusercontent.com/hmlendea/readme-assets/master/donate_generic.png)](https://hmlendea.go.ro/funding)

## 📄 License

This project is being distributed under the `GNU General Public License v3.0 or later`.
See [LICENSE](./LICENSE) for additional information.
