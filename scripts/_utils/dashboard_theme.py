"""
dashboard_theme.py - Shared dashboard theme tokens and branding asset paths.

The Stage 1 redesign uses this module as the source of truth for the
dark-shell / light-canvas visual system and future branding polish.
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
    shell_background: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent_primary: str
    accent_primary_dark: str
    accent_secondary: str
    surface_background: str
    surface_background_alt: str
    surface_border: str
    surface_border_strong: str
    surface_shadow: str
    field_background: str
    field_border: str
    chip_background: str
    chip_border: str
    graph_canvas_background: str
    graph_canvas_text: str
    graph_canvas_muted_text: str
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
    shell_gap: str
    section_gap: str
    panel_padding: str
    card_padding: str
    topbar_padding: str
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
        page_gradient_start="#01071C",
        page_gradient_mid="#021A3B",
        page_gradient_end="#13223C",
        page_glow_warm="rgba(255, 138, 0, 0.18)",
        page_glow_cool="rgba(0, 194, 255, 0.16)",
        shell_background="rgba(1, 7, 28, 0.66)",
        text_primary="#E6E4D8",
        text_secondary="#CCD7E2",
        text_muted="#86B3CC",
        accent_primary="#00C2FF",
        accent_primary_dark="#40668A",
        accent_secondary="#E6CB8D",
        surface_background="rgba(4, 15, 38, 0.88)",
        surface_background_alt="rgba(10, 28, 61, 0.92)",
        surface_border="rgba(134, 179, 204, 0.18)",
        surface_border_strong="rgba(134, 179, 204, 0.30)",
        surface_shadow="rgba(1, 7, 28, 0.52)",
        field_background="rgba(1, 7, 28, 0.42)",
        field_border="rgba(134, 179, 204, 0.28)",
        chip_background="rgba(134, 179, 204, 0.10)",
        chip_border="rgba(134, 179, 204, 0.22)",
        graph_canvas_background="#F3F1E8",
        graph_canvas_text="#13223C",
        graph_canvas_muted_text="#40668A",
        graph_edge="rgba(19, 34, 60, 0.22)",
        graph_legend_background="rgba(243, 241, 232, 0.90)",
        graph_legend_border="rgba(64, 102, 138, 0.20)",
        selected_fill="#00C2FF",
        selected_outline="#021A3B",
        vulnerable="#D94A38",
        unknown="#FF8A00",
        not_vulnerable="#4FBF6B",
    ),
    typography=DashboardTypography(
        font_ui='"Avenir Next", "Segoe UI Variable", "Trebuchet MS", sans-serif',
        font_display='"Avenir Next Condensed", "Avenir Next", "Trebuchet MS", sans-serif',
        eyebrow_spacing="0.18em",
        detail_kind_spacing="0.16em",
    ),
    spacing=DashboardSpacing(
        content_max_width="1800px",
        page_padding_top="20px",
        page_padding_x="20px",
        page_padding_bottom="20px",
        page_padding_mobile_top="16px",
        page_padding_mobile_x="14px",
        page_padding_mobile_bottom="20px",
        grid_gap="18px",
        shell_gap="18px",
        section_gap="16px",
        panel_padding="18px",
        card_padding="14px",
        topbar_padding="20px",
        radius_panel="22px",
        radius_field="14px",
        shadow_blur="18px",
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
        "--atlas-shell-background": theme.palette.shell_background,
        "--atlas-text-primary": theme.palette.text_primary,
        "--atlas-text-secondary": theme.palette.text_secondary,
        "--atlas-text-muted": theme.palette.text_muted,
        "--atlas-accent-primary": theme.palette.accent_primary,
        "--atlas-accent-primary-dark": theme.palette.accent_primary_dark,
        "--atlas-accent-secondary": theme.palette.accent_secondary,
        "--atlas-surface-background": theme.palette.surface_background,
        "--atlas-surface-background-alt": theme.palette.surface_background_alt,
        "--atlas-surface-border": theme.palette.surface_border,
        "--atlas-surface-border-strong": theme.palette.surface_border_strong,
        "--atlas-surface-shadow": theme.palette.surface_shadow,
        "--atlas-field-background": theme.palette.field_background,
        "--atlas-field-border": theme.palette.field_border,
        "--atlas-chip-background": theme.palette.chip_background,
        "--atlas-chip-border": theme.palette.chip_border,
        "--atlas-graph-canvas-background": theme.palette.graph_canvas_background,
        "--atlas-graph-canvas-text": theme.palette.graph_canvas_text,
        "--atlas-graph-canvas-muted-text": theme.palette.graph_canvas_muted_text,
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
        "--atlas-shell-gap": theme.spacing.shell_gap,
        "--atlas-section-gap": theme.spacing.section_gap,
        "--atlas-panel-padding": theme.spacing.panel_padding,
        "--atlas-card-padding": theme.spacing.card_padding,
        "--atlas-topbar-padding": theme.spacing.topbar_padding,
        "--atlas-radius-panel": theme.spacing.radius_panel,
        "--atlas-radius-field": theme.spacing.radius_field,
        "--atlas-shadow-blur": theme.spacing.shadow_blur,
        "--atlas-branding-logo-path": theme.branding.logo_asset_relative_path,
    }
