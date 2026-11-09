[![Donate](https://img.shields.io/badge/-%E2%99%A5%20Donate-%23ff69b4)](https://hmlendea.go.ro/fund.html)

# About

This is Python bot that posts a random fact to Mastodon from a predefined list of facts.

The facts are stored in a file and the bot selects a one to post.

It's designed to keep Mastodon users informed and entertained by posting a new fact on a regular basis.

# Usage

## Running in the background

### Using `systemd`

`/usr/lib/systemd/system/mastodon-random-facts-bot.timer`:
```gitconfig
[Unit]
Description=Periodically activates the random facts bot for Mastodon

[Timer]
OnBootSec=15min
OnUnitActiveSec=25min

[Install]
WantedBy=timers.target
```

`/usr/lib/systemd/system/mastodon-random-facts-bot.service`:
```gitconfig
[Unit]
Description=RSS bot for Mastodon
After=network.target

[Service]
WorkingDirectory=/home/horatiu/bots/mastodon-rss-bot
ExecStart=/bin/bash /home/horatiu/bots/mastodon-rss-bot/run.sh
User=horatiu
RuntimeMaxSec=60

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

You are welcome to submit any suggestion, feedback, or modification to this project.

When doing so, please:
- Maintain cross-platform compatibility
- Submit focused pull requests that conform to the existing code style
- Maintain your branch synchronised with `master`
- Revise the documentation when functionality changes
- Raise a new [issue](https://github.com/hmlendea/mastodon-random-facts-bot/issues) for problems or suggestions

See the [Contributing Guidelines](./CONTRIBUTING.md) for details on how to report issues, suggest enhancements, and submit changes.

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

## 🔒 Security

Mastodon Random Facts Bot handles Mastodon access tokens and application secret files locally. It transmits fact content and media to the configured Mastodon instance.

For information on reporting security vulnerabilities, see the [Security Policy](./SECURITY.md).

## 📜 Code of Conduct

See the [Code of Conduct](./CODE_OF_CONDUCT.md) for the standards of conduct expected in all project spaces.

## 🏗️ Architecture

Mastodon Random Facts Bot is a single-process, sequential console pipeline that selects a random fact from a local file, transforms its text, downloads and uploads embedded media, and publishes a public Mastodon status.

See the [Architecture Documentation](./ARCHITECTURE.md) for the system context, principal components, runtime flows, ownership boundaries, dependencies, constraints, and extension points.
