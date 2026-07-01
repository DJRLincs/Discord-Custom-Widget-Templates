# Discord Custom Widget Template

A starter repository for building and maintaining your own Discord custom widget with:

- GitHub Actions automation
- JSON import templates for layout variants
- A generic sync script that publishes your configured dynamic fields

This template is intentionally not tied to GitHub stats.

## References

- This template repository: [DJRLincs/Discord-Custom-Widget-Templates](https://github.com/DJRLincs/Discord-Custom-Widget-Templates)
- TheCreativeGod Discord widget extension: [TheCreativeGod/Discord-Widgets-Extension](https://github.com/TheCreativeGod/Discord-Widgets-Extension)
- Discord widgets documentation:
  https://docs.discord.food/resources/widgets

## Variant matrix

Top variants:

- widget_top_contained
- widget_top_hero

Bottom variants:

- widget_bottom_stats
- widget_bottom_collection (stats grid collection)
- widget_bottom_progress

Ready-to-import combinations:

- variants/top-contained__bottom-stats-grid/
- variants/top-contained__bottom-stats-grid-collection/
- variants/top-contained__bottom-progress/
- variants/top-hero__bottom-stats-grid/
- variants/top-hero__bottom-stats-grid-collection/
- variants/top-hero__bottom-progress/

Mini profile variants:

- variants/mini-profile-contained-stat/
- variants/mini-profile-hero-stat/

Example profile widget:

- variants/live-example/

## Quick start

1. Fork or clone this folder as a new GitHub repository.
2. Import one variant JSON template into the Discord widget editor using the extension.
3. Edit config.example.json and set your dynamic fields.
4. Add repository secrets:
   - DISCORD_BOT_TOKEN
   - DISCORD_APP_ID
   - DISCORD_USER_ID
5. Enable .github/workflows/widget-sync.yml.

If you want a starting point for your own profile, import the live example pack
in `variants/live-example/` first. It is meant to be edited, reused, and copied
as a reference for other people.

## What should go in the repo

Commit these:

- `README.md`
- `docs/`
- `configs/*.example.json`
- `variants/**/README.md`
- `variants/**/widget-import-template.json`
- `sync_widget.py`
- `config.example.json`
- `.github/workflows/*.yml`

Keep these out of the repo:

- `config.json` and any `*.local.json`
- secrets, tokens, and personal Discord IDs
- `__pycache__/` and `*.pyc`
- generated runtime files in `generated/`
- ad-hoc test exports unless you explicitly want them shared

## Fully dynamic templates

All provided JSON templates use value_type=data for editable fields.
No labels, text, or image values are hard-coded in the templates.

## Config format

The script publishes values from widget.dynamic in config.example.json.
Use type 1 for text, type 2 for number, and type 3 for image.

Example:

```json
{
  "widget": {
    "display_name": "My Widget",
    "dynamic": [
      { "type": 1, "name": "top_title", "value": "My Title" },
      { "type": 1, "name": "top_subtitle_1", "value": "Line one" },
      { "type": 1, "name": "stat_1_label", "value": "Contributions" },
      { "type": 1, "name": "stat_1_value", "value": "3196" },
      { "type": 1, "name": "progress_label", "value": "Current Goal" },
      { "type": 1, "name": "progress_text", "value": "3 of 10 complete" },
      { "type": 1, "name": "mini_label", "value": "Profile" },
      { "type": 1, "name": "mini_text", "value": "View stats" },
      { "type": 3, "name": "top_image_url", "value": { "url": "https://example.com/top.png" } },
      { "type": 3, "name": "progress_icon_url", "value": { "url": "https://example.com/icon.png" } },
      { "type": 3, "name": "mini_icon_url", "value": { "url": "https://example.com/mini-icon.png" } },
      { "type": 3, "name": "mini_image_url", "value": { "url": "https://example.com/mini-image.png" } }
    ]
  }
}
```

## Local test

```powershell
cd "Discord-Custom-Widget-Template"
$env:DISCORD_BOT_TOKEN = "YOUR_TOKEN"
$env:DISCORD_APP_ID = "YOUR_APP_ID"
$env:DISCORD_USER_ID = "YOUR_USER_ID"
python .\sync_widget.py
```

## Notes

- Publish your widget in Developer Portal after import/update.
- Keep tokens in GitHub Actions secrets, never in committed files.
