# Dashboard Redesign Plan
## AI Supply Chain Risk Atlas

## Purpose

This document defines the staged redesign plan for the local dashboard used in the AI Supply Chain Risk Atlas project.

The current dashboard already proves the data flow and basic interactive scaffold. The goal of this redesign is to transform it from a vertically stacked prototype into a graph-centric analytical application that looks polished, remains reproducible, and supports efficient local research exploration.

This dashboard is primarily for personal research use, not production deployment. The redesign should therefore prioritize clarity, analytical usability, and visual coherence over deployment infrastructure or enterprise-grade packaging.

---

## Core Product Direction

The finished dashboard should feel like:

- a graph-first investigative tool
- a polished research application
- a modern security / observability style interface
- serious and readable rather than flashy
- visually consistent with project branding

The graph must become the primary workspace. Summary metrics, filters, and detail views should support the graph rather than compete with it.

---

## Current Problems to Solve

The existing dashboard has several structural issues:

1. The layout feels like a report page rather than an application.
2. The graph is not visually dominant enough.
3. The page is too vertically stacked and scroll-heavy.
4. The typography feels document-like rather than dashboard-like.
5. The detail view is difficult to scan.
6. The graph styling and spacing do not yet feel intentional.
7. The overall visual system does not yet reflect the project identity.

---

## Design Decisions

### Technology
- Keep the dashboard in Dash.
- The current graph uses Plotly.
- The target graph renderer is Cytoscape, but the migration should happen in a later stage.

### Visual Direction
- Use a dark shell for the overall application.
- Use a light graph canvas for the main network view.
- Keep strong contrast between chrome and graph content.
- Use the project logo as an optional branded element during the visual design stage.

### Usage Context
- This is a local research workflow tool.
- Do not prioritize deployment concerns in this redesign phase.
- Responsiveness is helpful, but deployment packaging is not required.

### Interaction Decisions
- Default to single-node selection in the inspector.
- Do not implement compare mode now.
- Package labels should be hidden by default.
- Include a toggle that can reveal package labels when desired.
- Model labels may remain visible by default if legibility supports that choice.

### Graph Layout
- Prefer stable, reproducible node positions if the resulting layout is visually good.
- Do not force stability if it produces poor spacing or unreadable clustering.
- If needed, allow precomputed positions or a deterministic layout configuration.

---

## Visual Theme

Use a design system derived from the project logo.

### Primary Palette

- `#01071C` — deepest background
- `#021A3B` — top bar / primary shell
- `#13223C` — secondary panel background
- `#40668A` — muted structural blue
- `#86B3CC` — cool supporting accent
- `#00C2FF` — active selection / hover / highlight
- `#E6E4D8` — primary light text
- `#E6CB8D` — warm accent
- `#B46631` — support amber-brown
- `#FF8A00` — warning / risk accent
- `#D94A38` — vulnerable / critical
- `#4FBF6B` — not vulnerable / safe

### Usage Guidance

- Use deep navy and near-black for the shell and side panels.
- Use a soft light background for the graph canvas so graph structure remains readable.
- Use cyan / electric blue for interaction states.
- Use orange and red only for risk encoding and alert states.
- Use green sparingly for non-vulnerable states.
- Avoid overly neon effects or decorative glow that harms readability.

### Typography
- Replace any serif or document-style typography with a modern sans-serif UI style.
- Use restrained heading sizes.
- Use strong hierarchy through spacing, weight, and panel grouping rather than oversized text.
- Keep metric labels compact and easy to scan.

### UI Surfaces
- Use card-like panels with subtle border contrast.
- Prefer clear separation between shell, controls, graph canvas, and inspector.
- Use badges / chips for vulnerability status, severity, and fix availability.
- Use consistent spacing, border radii, and component padding.

---

## Branding Guidance

The project logo should be treated as an optional branding asset during the redesign.

### Asset Placement
Store the logo in a branding asset path such as:

`assets/branding/ai_supply_chain_risk_atlas_logo.png`

### Placement Experiments
During the visual theme stage, it is acceptable to test the logo in multiple locations:

1. top-left of the app header
2. inside the left sidebar near the project title
3. in a footer area at the bottom
4. omitted from the main UI, with only color branding retained

The redesign should make it easy to try these placements without coupling layout logic too tightly to any one option.

---

## Target Layout

The target interface should use a full-height application shell.

### Main Structure

- **Top bar**
  - project title
  - optional logo
  - dataset / sample badge
  - reset controls
  - optional layout / label toggles

- **Left sidebar**
  - search
  - filters
  - compact summary widgets
  - clickable “Top Reused Vulnerable Packages” table

- **Center pane**
  - graph canvas
  - graph legend / compact status controls
  - graph count summary

- **Right sidebar**
  - selection inspector
  - node-specific details
  - vulnerabilities and connected-node information

### Layout Goals

- Keep the graph visible and dominant above the fold.
- Avoid long vertical scrolling for the primary interface.
- Keep controls discoverable but secondary to the graph.
- Make the right panel the main explanation area for graph selections.

---

## Staged Implementation Plan

## Stage 0 — Audit and Refactor Preparation

### Goal
Prepare the codebase so UI work and graph-rendering work can proceed cleanly.

### Tasks
- Identify the current Dash app structure and rendering flow.
- Separate data transformation logic from UI rendering where possible.
- Locate current graph construction, selection handling, filters, and metrics.
- Introduce a theme / tokens module for colors, spacing, and typography constants.
- Add a clear location for branding assets.
- Document the current dashboard architecture in brief comments or a small developer note if useful.

### Acceptance Criteria
- Existing dashboard behavior still works.
- There is a dedicated place for theme values.
- Branding assets can be added without ad hoc file placement.
- Code is organized enough to support later layout and Cytoscape work.

---

## Stage 1 — New App Shell, Layout, and Theme

### Goal
Transform the prototype from a stacked report page into a graph-centric dashboard shell.

### Tasks
- Replace the current vertical report layout with:
  - top bar
  - left control sidebar
  - center graph region
  - right detail sidebar
- Convert current KPI metrics into compact cards.
- Apply the new dark-shell / light-canvas visual system.
- Replace oversized document-like typography with restrained dashboard typography.
- Improve spacing, panel grouping, and general visual hierarchy.
- Keep the existing Plotly graph for now.
- Preserve current filter/search/selection behavior unless a presentation change requires minor adaptation.

### Acceptance Criteria
- The graph is visually central and occupies the majority of the page.
- The dashboard feels like an application rather than a report.
- Metrics, filters, and details are visible without dominating the page.
- The visual theme reflects the brand palette.
- No Cytoscape migration yet.

---

## Stage 2 — Branding Pass and Visual Refinement

### Goal
Polish the application so it feels cohesive and intentional.

### Tasks
- Introduce the project logo in one or more experimental placements.
- Make logo placement easy to enable, disable, or relocate.
- Refine panel styling, badges, headings, spacing, and microcopy.
- Improve empty states, placeholder states, and panel headers.
- Add a compact legend style that does not visually overpower the graph.
- Make status indicators clearer and more attractive.

### Acceptance Criteria
- The dashboard has a visually coherent identity.
- Branding can be tested without destabilizing layout.
- The UI looks polished even before the graph renderer is replaced.

---

## Stage 3 — Graph Migration from Plotly to Cytoscape

### Goal
Replace the current network rendering with Cytoscape for better graph aesthetics and control.

### Tasks
- Replace Plotly graph rendering with Cytoscape.
- Preserve current graph semantics and data mappings.
- Encode:
  - node type by shape
  - vulnerability state by color
  - reuse / impact by size
  - dependency scope by edge style
- Use a light graph canvas inside the dark shell.
- Implement deterministic or stable layout settings where possible.
- Add layout controls only if they do not overcomplicate the UI.
- Keep package labels hidden by default.
- Include a toggle to reveal more labels when desired.
- Keep model labels visible only if legibility remains acceptable.
- Add hover and selection styling.

### Acceptance Criteria
- Cytoscape replaces Plotly successfully.
- The graph is more legible and aesthetically controlled.
- The label strategy avoids clutter.
- Layout is reasonably stable and visually acceptable.

---

## Stage 4 — Selection Workflow and Inspector Redesign

### Goal
Turn node selection into the core analytical interaction.

### Tasks
- Redesign the right sidebar as a true inspector panel.
- Support clean single-node inspection for:
  - model nodes
  - package nodes
- On selection:
  - center or focus the node in the graph
  - highlight its neighborhood
  - dim unrelated nodes and edges
  - populate inspector content clearly
- Use badges for:
  - vulnerability status
  - severity
  - fix availability
- Present package details in structured fields.
- Present model details in structured fields.
- Show associated vulnerability IDs and connected entities in a readable format.

### Acceptance Criteria
- Selecting a node clearly updates both graph focus and inspector content.
- The detail panel is easy to scan.
- The inspector is visually structured, not a raw text dump.

---

## Stage 5 — Filters, Search, and Linked Summary Views

### Goal
Make the dashboard efficient for investigation.

### Tasks
- Improve search behavior for:
  - model IDs
  - package names
  - ecosystem
  - version where useful
- Make the “Top Reused Vulnerable Packages” table interactive.
- Clicking a package row should focus or highlight that package in the graph.
- Add filters for:
  - node type
  - dependency scope
  - vulnerability status
  - severity
  - impacted model count or related threshold where appropriate
- Add graph status summaries such as visible node / edge counts.
- Ensure filters and summaries remain synchronized.

### Acceptance Criteria
- Search and filters feel coherent and responsive.
- Summary lists act as navigation into the graph.
- The dashboard supports faster local analysis.

---

## Stage 6 — Final Polish for Local Research Use

### Goal
Add the finishing touches that make the dashboard presentation-ready.

### Tasks
- Refine loading states and empty states.
- Improve keyboard / hover / focus behavior where practical.
- Tidy any rough edges in spacing, panel sizing, or label overflow.
- Add optional export-friendly touches if easy, such as a screenshot-friendly layout mode.
- Ensure the UI remains readable during real exploratory use.

### Acceptance Criteria
- The application looks complete and intentional.
- It is comfortable to use for repeated local research exploration.
- The graph remains the dominant and most useful element.

---

## Graph Styling Guidance

These rules apply once Cytoscape is introduced.

### Node Types
- Model nodes should use a distinct shape from package nodes.
- Package nodes should remain visually simple and numerous.
- Model nodes should stand out as anchor entities.

### Node Colors
- Vulnerable: red / red-orange
- Unknown: amber / orange
- Not vulnerable: green
- Model nodes: neutral blue / teal family distinct from vulnerability colors

### Node Sizes
- Package nodes may scale by impacted model count or reuse count.
- Model nodes may scale by dependency footprint if that improves readability.
- Avoid excessive size variation that makes the graph visually unstable.

### Edge Styles
- Direct dependency edges: solid
- Transitive dependency edges: dashed
- Default edge color should be subdued.
- Highlight selected-path or neighborhood edges more strongly.

### Labels
- Package labels hidden by default.
- Package labels shown on hover and selection.
- Optional toggle for showing more labels.
- Model labels may stay visible at default zoom if legible.
- Avoid graph-wide label clutter.

---

## Inspector Content Guidance

### For Package Nodes
Show:
- package name
- ecosystem
- version
- vulnerability status
- vulnerability count
- severity bucket
- fix availability
- impacted model count
- associated vulnerability IDs
- connected models

### For Model Nodes
Show:
- model ID
- dependency counts
- direct vs transitive dependency counts
- vulnerable dependency count
- unknown dependency count
- notable connected packages

### Presentation Rules
- Use a structured key-value layout.
- Use chips / badges instead of repeating raw status text.
- Avoid long walls of concatenated metadata.
- Keep the most important facts near the top.

---

## Non-Goals for This Redesign

The following are explicitly out of scope for now:

- deployment optimization
- production authentication / access control
- enterprise responsiveness guarantees
- compare mode for multiple selected nodes
- major backend or data-pipeline redesign
- changing analytical semantics unless clearly necessary

---

## Implementation Constraints

- Preserve current data correctness and analytical meaning.
- Do not silently change filtering semantics.
- Do not combine multiple major stages into one implementation pass.
- At each stage, keep changes scoped and reviewable.
- Prefer incremental changes that can be visually reviewed after each stage.

---

## How to Use This Plan with Codex

Codex should be instructed to implement one stage at a time.

Example prompt:

> Read `docs/dashboard_redesign_plan.md` and implement Stage 1 only. Do not begin later stages. Preserve existing dashboard behavior and analytical semantics unless Stage 1 explicitly changes presentation. Summarize files changed, note any blockers, and explain any assumptions.

Subsequent stages should be requested the same way, one at a time.

---