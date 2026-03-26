"""
dashboard_theme.py - Shared dashboard theme tokens and branding asset paths.

Stage 0 keeps the current presentation mostly intact while centralizing the
values that later redesign stages will swap more aggressively.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_ASSETS_DIR = _REPO_ROOT / "assets"
BRANDING_ASSETS_DIR = DASHBOARD_ASSETS_DIR / "branding"
DEFAULT_LOGO_ASSET_RELATIVE_PATH = "branding/ai_supply_chain_risk_atlas_logo.png"


@dataclass(frozen=True)
class DashboardPalette:
    page_gradient_start: str
    page_gradient_mid: str
    page_gradient_end: str
    page_glow_warm: str
    page_glow_cool: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent_primary: str
    accent_primary_dark: str
    accent_secondary: str
    surface_background: str
    surface_border: str
    surface_shadow: str
    graph_canvas_background: str
    graph_edge: str
    graph_legend_background: str
    graph_legend_border: str
    selected_fill: str
    selected_outline: str
    vulnerable: str
    unknown: str
    not_vulnerable: str


@dataclass(frozen=True)
class DashboardTypography:
    font_ui: str
    font_display: str
    eyebrow_spacing: str
    detail_kind_spacing: str


@dataclass(frozen=True)
class DashboardSpacing:
    content_max_width: str
    page_padding_top: str
    page_padding_x: str
    page_padding_bottom: str
    page_padding_mobile_top: str
    page_padding_mobile_x: str
    page_padding_mobile_bottom: str
    grid_gap: str
    panel_padding: str
    card_padding: str
    radius_panel: str
    radius_field: str
    shadow_blur: str


@dataclass(frozen=True)
class DashboardBranding:
    assets_dir: Path
    logo_asset_relative_path: str
    logo_alt_text: str

    @property
    def logo_filesystem_path(self) -> Path:
        return DASHBOARD_ASSETS_DIR / self.logo_asset_relative_path


@dataclass(frozen=True)
class DashboardTheme:
    palette: DashboardPalette
    typography: DashboardTypography
    spacing: DashboardSpacing
    branding: DashboardBranding


DEFAULT_DASHBOARD_THEME = DashboardTheme(
    palette=DashboardPalette(
        page_gradient_start="#f7f3ea",
        page_gradient_mid="#eef4f2",
        page_gradient_end="#f7fafc",
        page_glow_warm="rgba(245, 158, 11, 0.18)",
        page_glow_cool="rgba(15, 118, 110, 0.16)",
        text_primary="#0f172a",
        text_secondary="#334155",
        text_muted="#64748b",
        accent_primary="#0f766e",
        accent_primary_dark="#0b3f3a",
        accent_secondary="#f59e0b",
        surface_background="rgba(255, 255, 255, 0.8)",
        surface_border="rgba(15, 23, 42, 0.08)",
        surface_shadow="rgba(15, 23, 42, 0.08)",
        graph_canvas_background="rgba(255, 255, 255, 0.9)",
        graph_edge="rgba(15, 23, 42, 0.18)",
        graph_legend_background="rgba(255, 255, 255, 0.78)",
        graph_legend_border="rgba(15, 23, 42, 0.08)",
        selected_fill="#f97316",
        selected_outline="#7c2d12",
        vulnerable="#dc2626",
        unknown="#f59e0b",
        not_vulnerable="#22c55e",
    ),
    typography=DashboardTypography(
        font_ui='"Avenir Next", "Trebuchet MS", "Gill Sans", sans-serif',
        font_display='"Georgia", "Palatino Linotype", serif',
        eyebrow_spacing="0.12em",
        detail_kind_spacing="0.14em",
    ),
    spacing=DashboardSpacing(
        content_max_width="1440px",
        page_padding_top="32px",
        page_padding_x="28px",
        page_padding_bottom="40px",
        page_padding_mobile_top="22px",
        page_padding_mobile_x="16px",
        page_padding_mobile_bottom="28px",
        grid_gap="16px",
        panel_padding="18px",
        card_padding="18px",
        radius_panel="20px",
        radius_field="12px",
        shadow_blur="10px",
    ),
    branding=DashboardBranding(
        assets_dir=BRANDING_ASSETS_DIR,
        logo_asset_relative_path=DEFAULT_LOGO_ASSET_RELATIVE_PATH,
        logo_alt_text="AI Supply Chain Risk Atlas logo",
    ),
)


def build_theme_css_variables(
    theme: DashboardTheme = DEFAULT_DASHBOARD_THEME,
) -> dict[str, str]:
    """Expose theme tokens as CSS custom properties for the Dash layout shell."""
    return {
        "--atlas-page-gradient-start": theme.palette.page_gradient_start,
        "--atlas-page-gradient-mid": theme.palette.page_gradient_mid,
        "--atlas-page-gradient-end": theme.palette.page_gradient_end,
        "--atlas-page-glow-warm": theme.palette.page_glow_warm,
        "--atlas-page-glow-cool": theme.palette.page_glow_cool,
        "--atlas-text-primary": theme.palette.text_primary,
        "--atlas-text-secondary": theme.palette.text_secondary,
        "--atlas-text-muted": theme.palette.text_muted,
        "--atlas-accent-primary": theme.palette.accent_primary,
        "--atlas-accent-primary-dark": theme.palette.accent_primary_dark,
        "--atlas-accent-secondary": theme.palette.accent_secondary,
        "--atlas-surface-background": theme.palette.surface_background,
        "--atlas-surface-border": theme.palette.surface_border,
        "--atlas-surface-shadow": theme.palette.surface_shadow,
        "--atlas-graph-canvas-background": theme.palette.graph_canvas_background,
        "--atlas-graph-edge": theme.palette.graph_edge,
        "--atlas-graph-legend-background": theme.palette.graph_legend_background,
        "--atlas-graph-legend-border": theme.palette.graph_legend_border,
        "--atlas-selected-fill": theme.palette.selected_fill,
        "--atlas-selected-outline": theme.palette.selected_outline,
        "--atlas-status-vulnerable": theme.palette.vulnerable,
        "--atlas-status-unknown": theme.palette.unknown,
        "--atlas-status-not-vulnerable": theme.palette.not_vulnerable,
        "--atlas-font-ui": theme.typography.font_ui,
        "--atlas-font-display": theme.typography.font_display,
        "--atlas-eyebrow-spacing": theme.typography.eyebrow_spacing,
        "--atlas-detail-kind-spacing": theme.typography.detail_kind_spacing,
        "--atlas-content-max-width": theme.spacing.content_max_width,
        "--atlas-page-padding-top": theme.spacing.page_padding_top,
        "--atlas-page-padding-x": theme.spacing.page_padding_x,
        "--atlas-page-padding-bottom": theme.spacing.page_padding_bottom,
        "--atlas-page-padding-mobile-top": theme.spacing.page_padding_mobile_top,
        "--atlas-page-padding-mobile-x": theme.spacing.page_padding_mobile_x,
        "--atlas-page-padding-mobile-bottom": theme.spacing.page_padding_mobile_bottom,
        "--atlas-grid-gap": theme.spacing.grid_gap,
        "--atlas-panel-padding": theme.spacing.panel_padding,
        "--atlas-card-padding": theme.spacing.card_padding,
        "--atlas-radius-panel": theme.spacing.radius_panel,
        "--atlas-radius-field": theme.spacing.radius_field,
        "--atlas-shadow-blur": theme.spacing.shadow_blur,
        "--atlas-branding-logo-path": theme.branding.logo_asset_relative_path,
    }
