# Config Variants

Each file maps to a template in variants/.

The `configs/*.example.json` files are the ones intended to be committed.
Create a local copy without the `.example` suffix if you want to test or run
personal values that should stay private.

## Config keys vs GitHub secrets

These are intentionally different types of names:

- Config keys are JSON paths used by the script.
- GitHub secrets are environment variable names injected at runtime.

Mapping used by the sync script:

- `discord.app_id_env` -> app id env var name (default `DISCORD_APP_ID`)
- `discord.user_id_env` -> user id env var name (default `DISCORD_USER_ID`)
- `discord.bot_token_env` -> points to the token env var name (default `DISCORD_BOT_TOKEN`)

Runtime priority:

1. Environment variables from GitHub Actions secrets
2. Values in the config file

This lets one committed example config work for local testing and Actions without storing secrets in Git.

Use one of these approaches:

1. Local run:
   - `set CONFIG_PATH=configs/<file>.json` (or PowerShell `$env:CONFIG_PATH = "configs/<file>.json"`)
2. GitHub Actions:
   - Set repository variable `WIDGET_CONFIG_PATH` to one of the paths below.

## Top + Bottom variants

- `configs/top-contained__bottom-stats-grid.example.json`
- `configs/top-contained__bottom-stats-grid-collection.example.json`
- `configs/top-contained__bottom-progress.example.json`
- `configs/top-hero__bottom-stats-grid.example.json`
- `configs/top-hero__bottom-stats-grid-collection.example.json`
- `configs/top-hero__bottom-progress.example.json`

## Mini profile variants

- `configs/mini-profile-contained-stat.example.json`
- `configs/mini-profile-hero-stat.example.json`

## Example profile widget

- `configs/live-example.example.json`
- `configs/work-progress-bst.example.json` (Mon-Fri 08:00-18:00 Europe/London work progress)

## Runtime placeholders

The sync script can inject runtime placeholders into type 1 text values using
`{{token_name}}`.

Supported base tokens:

- `{{unix_now}}`
- `{{now_utc_iso}}`

When `widget.work_schedule` is configured, these are also available:

- `{{work_timezone}}`
- `{{work_status}}`
- `{{work_progress_percent}}`
- `{{work_progress_bar}}`
- `{{work_progress_text}}`
- `{{work_unix_start}}`
- `{{work_unix_end}}`
- `{{work_unix_next_start}}`
- `{{work_unix_next_end}}`
- `{{work_local_now}}`

All values are editable and fully data-driven.
