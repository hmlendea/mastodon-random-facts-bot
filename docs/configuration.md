# Configuration

This document describes how the bot is configured, where configuration lives, and the consequences of changing it.

## Configuration model

The bot has no configuration file. All configuration arrives as six positional command-line arguments:

1. `facts_file` — path to the facts file
2. `instance` — Mastodon instance domain
3. `username` — account username (also application name)
4. `access_token` — user access token with write scope
5. `tags` — space-separated static tags
6. `language` — language code for extension hooks

There are no environment variables, no defaults, and no configuration discovery.

## Secret file

The only persistent local configuration is `app_<instance>.secret`, created automatically on first run by `Mastodon.create_app`. It contains the application credentials (client ID and secret) for the registered application. The file is:

- Created in the current working directory.
- Named after the instance argument.
- Reused on subsequent runs without validation.
- Not encrypted; it is a plain JSON file.

The operator must ensure the working directory is writable and that the secret file is protected by filesystem permissions.

## Scheduler configuration

The posting cadence is configured in the external scheduler. The repository documents a `systemd` timer unit with:

```ini
OnBootSec=15min
OnUnitActiveSec=25min
RuntimeMaxSec=60
```

These values are not part of the bot; they are operator choices. The bot itself has no concept of time, intervals, or scheduling.

## Consequences of the model

- **Self-describing invocations.** The scheduler log shows exactly which instance, account, and facts file were used.
- **No configuration drift.** There is no second file to fall out of sync with the scheduler.
- **Breaking changes are visible.** Adding, removing, or reordering arguments breaks every existing scheduler invocation immediately and visibly.
- **No secrets in configuration.** The access token is passed as an argument, not stored in a file. The secret file contains only application credentials, not the user token.

## Modification impact

- Adding a seventh argument breaks all existing invocations. Treat as incompatible; see [Compatibility contracts](../ARCHITECTURE.md#-compatibility-contracts).
- Changing the argument order breaks all existing invocations.
- Introducing a configuration file would be a new dependency and a new failure mode (missing file, parse error, validation error).
- Introducing environment variable fallbacks would create ambiguity about which value takes precedence.

## Recommendation

Keep the six-argument model. If additional configuration is needed, consider:

1. A subcommand structure (for example `post`, `register`, `test`) that preserves the existing positional arguments for the `post` subcommand.
2. A separate configuration file read by a wrapper script that then invokes the bot with the six arguments.

Either approach preserves the bot's current contract while allowing richer configuration.