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
