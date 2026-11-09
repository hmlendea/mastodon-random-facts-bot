# Build and deployment

This document describes how to install, configure, and deploy the bot. It assumes a Linux host with Python 3 and `systemd`.

## Prerequisites

- Python 3 (3.6+ recommended; the code uses f-strings and `os.path.isfile`).
- `pip` for dependency installation.
- A Mastodon account on the target instance with an access token that has `write:statuses` and `write:media` scopes.
- A facts file (newline-delimited text).
- A scheduler (`systemd` timer, cron, or equivalent).

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:hmlendea/mastodon-random-facts-bot.git
cd mastodon-random-facts-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs `Mastodon.py`, `fake_useragent`, and `regex`. See [Dependencies](./dependencies.md) for the implicit `requests` dependency.

### 3. Prepare the facts file

Create a text file with one fact per line. Example `facts.txt`:

```
Honey never spoils. https://example.com/honey.jpg
Octopuses have three hearts.
Romania has the fastest internet in Europe.
```

Media URLs must be HTTPS, direct image links, and end with a supported suffix (`.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`).

### 4. Obtain an access token

On the target Mastodon instance:

1. Go to **Preferences → Development → New Application**.
2. Set a name, redirect URI (any valid URI), and scopes (`read`, `write`, `follow`).
3. Create the application and copy the access token.

Alternatively, the bot can register its own application on first run (see [Secret file bootstrap](#secret-file-bootstrap)), but the user access token must still be obtained manually.

### 5. Test the invocation

```bash
python mastodon-random-facts-bot.py facts.txt mastodon.social mybot TOKEN " #Fact #Random" en
```

Expected output on first run:

```
Successfully created the application on instance mastodon.social
 > Posting fact:
Honey never spoils.

 #Fact #Random
```

Verify the status appears on the instance timeline.

## Secret file bootstrap

On first run, the bot calls `Mastodon.create_app` and writes `app_<instance>.secret` to the current working directory. This file contains the application credentials. Subsequent runs reuse it.

- The file is plain JSON; protect it with filesystem permissions (`chmod 600`).
- Deleting the file forces re-registration on the next run.
- The file is ignored by `.gitignore` (`*.secret`).

## Deployment with systemd

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

## Deployment with cron

Add to the operator's crontab:

```cron
*/25 * * * * cd /opt/mastodon-random-facts-bot && /usr/bin/python3 mastodon-random-facts-bot.py facts.txt mastodon.social mybot TOKEN " #Fact #Random" en >> /var/log/mastodon-random-facts-bot.log 2>&1
```

## Deployment with Docker

The repository does not ship a Dockerfile. A minimal containerisation:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "mastodon-random-facts-bot.py", "facts.txt", "mastodon.social", "mybot", "TOKEN", " #Fact #Random", "en"]
```

Run with a scheduler outside the container (for example a Kubernetes CronJob or a host systemd timer).

## Access token security

The access token is passed as a command-line argument and is visible in:

- The process table (`ps aux`) during execution.
- Scheduler logs (systemd journal, cron logs).
- Shell history (if typed manually).

Mitigations:

- Use a dedicated bot account with minimal privileges.
- Restrict the token's scopes to `write:statuses` and `write:media`.
- Rotate the token if the host is compromised.
- Consider a wrapper script that reads the token from a protected file and passes it as an argument, keeping the token out of scheduler configuration.

## Rollback

The bot has no versioned deployment artefacts. Rollback is a `git checkout` of the repository:

```bash
cd /opt/mastodon-random-facts-bot
git checkout v1.4.1
```

The secret file is not affected by checkout (it is gitignored).

## Health checks

The bot provides no health endpoint. Health is inferred from:

- Scheduler logs showing successful exits (exit code 0).
- The Mastodon timeline showing new posts at the expected cadence.
- Absence of `FAILURE!` lines in the journal.

See [Troubleshooting](./troubleshooting.md) for failure diagnosis.