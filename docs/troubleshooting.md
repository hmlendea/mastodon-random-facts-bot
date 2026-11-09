# Troubleshooting

This document helps operators diagnose common failures. It maps observable symptoms to causes and fixes.

## Symptom: no posts appear on the timeline

### Diagnosis

1. Check the scheduler is active:
   ```bash
   systemctl status mastodon-random-facts-bot.timer
   systemctl list-timers --all | grep mastodon
   ```
2. Check the last run's logs:
   ```bash
   journalctl -u mastodon-random-facts-bot.service -n 100
   ```
3. Check the exit code:
   ```bash
   systemctl status mastodon-random-facts-bot.service
   ```

### Common causes

| Log signal | Cause | Fix |
|------------|-------|-----|
| `ERROR: Failed to log ... into ...` | Invalid token or instance URL | Verify token scope and instance domain |
| `ERROR: Failed to read the file: ...` | Facts file missing or unreadable | Check path and permissions |
| `Failed to create the application on instance ...` | Instance unreachable or registration disabled | Check network, instance status |
| `   > FAILURE! ...` | Media download or upload failed | Check media URL reachability |
| Traceback with `IndexError` | Empty facts file or missing argument | Add facts, fix invocation |
| Traceback with `MastodonError` | API error (rate limit, invalid media, etc.) | See [Error handling](./error-handling.md) |

## Symptom: posts appear but without media

### Diagnosis

Check the logs for `URL <url>` lines. If absent, no media URLs were recognised.

### Common causes

- Media URL uses `http://` instead of `https://` (regex only matches `https://`).
- Media URL has a query string (regex truncates at `?`).
- Media URL has an unsupported extension (only `.gif`, `.jpg`, `.jpeg`, `.png`, `.webp`).
- Media URL extension is uppercase (`.JPG` not recognised; suffix check is case-sensitive).
- Media URL contains characters outside `[a-zA-Z0-9%\./_\-]`.

### Fix

Edit the facts file to use clean, direct HTTPS image URLs with lowercase supported extensions.

## Symptom: posts appear but with duplicate hashtags

### Diagnosis

The tag filtering logic deduplicates against the body and the accumulated filtered string. Duplicates appear when:

- The fact body contains a hashtag with different casing than the tag argument (filtering is case-insensitive, so this should not happen; verify the body actually contains the tag).
- The tag argument contains a hashtag with trailing punctuation (for example `#Fact,` — the comma is part of the token).
- The dynamic tags hook returns a tag already in the body.

### Fix

- Ensure the facts file does not contain the same hashtags as the tags argument.
- Ensure the tags argument contains clean tokens separated by spaces.
- Review `dynamic_tags.py` for unintended tag generation.

## Symptom: posts appear but text is garbled

### Diagnosis

- Check the facts file encoding (must be UTF-8).
- Check for literal `\n` sequences in the facts file (they are converted to newlines; if unintended, remove them).
- Check `text_replacements.apply` for operator transformations that alter the text.

### Fix

- Save the facts file as UTF-8.
- Remove unintended `\n` escape sequences.
- Review the operator hook.

## Symptom: first run fails with registration error

### Diagnosis

`Mastodon.create_app` returned falsy. Check:

- Instance reachability (`curl https://<instance>/api/v1/instance`).
- Instance allows application registration (some instances disable it).
- Network/firewall allows outbound HTTPS.

### Fix

- Verify instance URL and network.
- If registration is disabled, register the application manually via the instance's web interface and place the credentials in `app_<instance>.secret` in the expected format.

## Symptom: media download fails

### Diagnosis

Logs show `   > FAILURE! <exception>`. Common exceptions:

- `ConnectionError`: media host unreachable.
- `Timeout`: media host slow (no timeout configured; may hang until `RuntimeMaxSec`).
- `HTTPError`: media host returned 4xx/5xx (`raise_for_status`).
- `SSLError`: certificate problem.

### Fix

- Verify the media URL is reachable from the bot host: `curl -I <url>`.
- Check the media host's availability and rate limits.
- Use a different media host in the facts file.

## Symptom: media upload fails

### Diagnosis

Logs show `   > FAILURE! <exception>` after ` > Uploading media to Mastodon: <url>`. Common causes:

- Access token lacks `write:media` scope.
- Media exceeds instance size limits.
- Instance media endpoint unavailable.
- Downloaded bytes are not a valid image (media host served an error page with `content-type: image/...`).

### Fix

- Verify token scopes.
- Check instance media size limits.
- Verify the media URL serves actual image bytes.

## Symptom: status_post fails

### Diagnosis

Unhandled traceback after ` > Posting fact:`. Common causes:

- Access token lacks `write:statuses` scope.
- Body exceeds instance character limit.
- Media IDs invalid or expired.
- Instance status endpoint unavailable.

### Fix

- Verify token scopes.
- Check fact length (including tags) against instance limits.
- Verify media upload succeeded (check `SUCCESS!` lines).

## Symptom: secret file not created

### Diagnosis

- The working directory is not writable.
- `create_app` returned falsy (see registration error above).

### Fix

- Ensure the service user has write access to the working directory.
- Check registration error logs.

## Symptom: bot runs but posts nothing (silent)

### Diagnosis

- The facts file is empty (`random.choice` raises `IndexError`; check for traceback).
- The facts file contains only blank lines (selected fact is `'\n'`; after stripping, body is empty; status may post as empty or fail).
- The scheduler is not running the service (check timer status).

### Fix

- Add facts to the file.
- Verify the timer is active and the service runs.

## General diagnostic commands

```bash
# View recent logs
journalctl -u mastodon-random-facts-bot.service -n 200

# View timer state
systemctl list-timers --all | grep mastodon

# Run manually to observe output
cd /opt/mastodon-random-facts-bot
python mastodon-random-facts-bot.py facts.txt mastodon.social mybot TOKEN " #Fact" en

# Check secret file
ls -la app_*.secret
cat app_*.secret

# Test instance reachability
curl -s https://<instance>/api/v1/instance | head

# Test media URL reachability
curl -I <media_url>
```

## Escalation

If the cause is not clear from the logs:

1. Capture the full journal output for one run.
2. Capture the facts file content (redact any sensitive URLs).
3. Capture the invocation command (redact the access token).
4. Open an issue on the repository with the captured information. See [CONTRIBUTING.md](../CONTRIBUTING.md).