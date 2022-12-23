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
