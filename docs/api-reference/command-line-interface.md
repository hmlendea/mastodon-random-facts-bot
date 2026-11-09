# Command-line interface

This document defines the bot's command-line interface: six positional arguments, no options, no flags, and no help text.

## Synopsis

```bash
python mastodon-random-facts-bot.py <facts_file> <instance> <username> <access_token> <tags> <language>
```

## Arguments

| Position | Name | Variable | Description |
|----------|------|----------|-------------|
| 1 | `facts_file` | `facts_file_path` | Path to the newline-delimited facts file |
| 2 | `instance` | `mastodon_instance` | Mastodon instance domain (for example `mastodon.social`) |
| 3 | `username` | `mastodon_username` | Account username; also used as the application name during registration |
| 4 | `access_token` | `mastodon_access_token` | User access token with write scope |
| 5 | `tags` | `tags_to_add` | Space-separated static tags to append (for example `' #Fact #Random'`) |
| 6 | `language` | `language` | Language code passed to the extension hooks (for example `en`, `ro`) |

## Parsing

- Arguments are read directly from `sys.argv[1]` through `sys.argv[6]`.
- There is no argument parser, no validation, no default values, and no help output.
- A missing argument raises `IndexError` with an unhandled traceback.
- Extra arguments beyond the sixth are silently ignored.
- The `tags` argument must be quoted when it contains spaces, as in the synopsis.

## Examples

### Basic invocation

```bash
python mastodon-random-facts-bot.py facts.txt mastodon.social mybot TOKEN " #Fact #Random" en
```

### Romanian facts

```bash
python mastodon-random-facts-bot.py facts-ro.txt mastodon.social mybot TOKEN " #Fapt #Aleatoriu" ro
```

### No tags

```bash
python mastodon-random-facts-bot.py facts.txt mastodon.social mybot TOKEN "" en
```

An empty fifth argument results in no static tags; the filtering block is skipped when both static and dynamic tags are empty.

## Environment

The bot reads no environment variables. All configuration arrives through the six positional arguments. The `HOME` environment variable is not used; the secret file is created in the current working directory.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Status published successfully |
| 1 | Application registration failed, or facts file unreadable |
| 2 | Mastodon client construction failed |
| Other | Unhandled exception (media failure, publication failure, missing argument, empty facts file) |

See [Error handling](../error-handling.md) for the full taxonomy.

## Compatibility

The argument order and count are part of the operator-facing contract. Changing either breaks every existing scheduler invocation. See [Compatibility contracts](../../ARCHITECTURE.md#-compatibility-contracts) in the root architecture document.
