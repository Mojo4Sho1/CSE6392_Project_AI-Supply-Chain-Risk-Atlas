# Dashboard Architecture Note

**Last updated:** 2026-03-26

This note captures the dashboard structure after Stage 0 so the next redesign stages can work from stable seams instead of rediscovering the codebase.

## Current layer map

- `scripts/run_dashboard.py`
  - CLI entrypoint and runtime contract handling
- `scripts/_utils/dashboard_data.py`
  - artifact loading, GraphML coercion, seeded layout positions, and lookup construction
- `scripts/_utils/dashboard_view.py`
  - pure filter/search/detail payload logic
- `scripts/_utils/dashboard_controller.py`
  - orchestration from UI inputs to visible graph, detail payload, and renderer output
- `scripts/_utils/dashboard_layout.py`
  - Dash component tree and static panel builders
- `scripts/_utils/dashboard_render_plotly.py`
  - current Plotly renderer only
- `scripts/_utils/dashboard_theme.py`
  - theme tokens, repo `assets/` location, and branding asset paths
- `assets/dashboard.css`
  - CSS surfaces driven by the theme-backed custom properties from `dashboard_theme.py`
- `assets/branding/`
  - reserved home for optional branding assets; default logo target is `assets/branding/ai_supply_chain_risk_atlas_logo.png`

## Why the split matters

- Stage 1 should be able to redesign the shell mostly inside `dashboard_layout.py`, `dashboard_theme.py`, and `assets/dashboard.css`.
- Stage 2 should be able to experiment with logo placement without inventing a new asset path.
- Stage 3 should be able to add a new renderer module without rewriting artifact loading or filter logic.

## Guardrails for future stages

- Keep `dashboard_data.py` and `dashboard_view.py` renderer-agnostic.
- Preserve the current read-only artifact contract from `docs/specs/dashboard-showcase.md`.
- Treat `dashboard_controller.py` as the place where interaction state is resolved before any renderer-specific work happens.
