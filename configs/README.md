# Config Variants

Each file maps to a template in variants/.

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

All values are editable and fully data-driven.
