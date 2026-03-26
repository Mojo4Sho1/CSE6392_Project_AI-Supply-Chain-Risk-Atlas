"""Unit tests for dashboard_theme.py."""

from __future__ import annotations

from pathlib import Path

from scripts._utils.dashboard_theme import (
    BRANDING_ASSETS_DIR,
    DASHBOARD_ASSETS_DIR,
    DEFAULT_DASHBOARD_THEME,
    build_theme_css_variables,
)


def test_build_theme_css_variables_exposes_core_theme_tokens():
    css_vars = build_theme_css_variables()

    assert css_vars["--atlas-accent-primary"] == DEFAULT_DASHBOARD_THEME.palette.accent_primary
    assert css_vars["--atlas-font-ui"] == DEFAULT_DASHBOARD_THEME.typography.font_ui
    assert css_vars["--atlas-graph-canvas-text"] == (
        DEFAULT_DASHBOARD_THEME.palette.graph_canvas_text
    )
    assert css_vars["--atlas-branding-logo-path"] == (
        DEFAULT_DASHBOARD_THEME.branding.logo_asset_relative_path
    )


def test_branding_paths_resolve_under_repo_assets():
    assert BRANDING_ASSETS_DIR == DASHBOARD_ASSETS_DIR / "branding"
    assert DEFAULT_DASHBOARD_THEME.branding.logo_filesystem_path == (
        DASHBOARD_ASSETS_DIR / DEFAULT_DASHBOARD_THEME.branding.logo_asset_relative_path
    )
    assert Path(DEFAULT_DASHBOARD_THEME.branding.logo_asset_relative_path).parts[0] == "branding"
