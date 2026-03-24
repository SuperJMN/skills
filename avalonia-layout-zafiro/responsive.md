# Responsive Layout — The Three Tricks

> How to build adaptive UIs that work on Desktop, Tablet, Mobile, and Browser — using the same three primitives that make web layouts "magic".

## 🚨 Mandatory: Responsive Is the Default, Not an Upgrade

**Every layout you produce MUST be responsive.** There is no "desktop-only" mode. When creating any view:

- **Never use `StackPanel Orientation="Horizontal"` for toolbars** → Use `FlexPanel` with `Wrap="Wrap"`.
- **Never use `Grid ColumnDefinitions="..."` for content that should reflow** → Use `BootstrapGridPanel` with `Col`/`ColMd`/`ColLg`.
- **Never use `UniformGrid Columns="N"` for cards** → Use `BootstrapGridPanel` with per-breakpoint spans.

The only acceptable uses of fixed `Grid` are: form field alignment (label + input), and truly fixed structural elements (e.g., a dialog with known dimensions). Everything else is responsive.

---

## 🗺️ The Web ↔ Zafiro Map

| Web Primitive | Zafiro Panel | Use For |
|---|---|---|
| CSS Flexbox | **`FlexPanel`** | 1D flow: toolbars, button groups, navbars, centering |
| Bootstrap Grid (12-col) | **`BootstrapGridPanel`** | Content reflow: cards, forms, dashboards |
| CSS Grid / `@media` | **`SemanticPanel`** / **`BlueprintPanel`** | App-level structure: sidebar + primary + secondary |
| `display:none` / `@media` swap | **`AdaptivePanel`** / **`ResponsivePresenter`** | Show/hide or swap content at breakpoints |

---

## 🔧 Trick 1 — FlexPanel for Toolbars and Bars

Use `FlexPanel` whenever you need items in a row/column with **auto + stretch** mixing. This covers toolbars, navbars, button bars, and any row where one element should stretch.

```xml
<!-- Toolbar: hamburger (auto) + title (stretch) + account button (auto) -->
<panels:FlexPanel Direction="Row" AlignItems="Center" Gap="8">
    <Button panels:FlexPanel.Shrink="0">☰</Button>
    <TextBlock panels:FlexPanel.Grow="1" Text="My App" />
    <Button panels:FlexPanel.Shrink="0">👤</Button>
</panels:FlexPanel>
```

```xml
<!-- Action bar that wraps on narrow screens -->
<panels:FlexPanel Direction="Row" Wrap="Wrap" Gap="8" JustifyContent="SpaceBetween">
    <Button panels:FlexPanel.Shrink="0">Save</Button>
    <Button panels:FlexPanel.Shrink="0">Export</Button>
    <Button panels:FlexPanel.Shrink="0">Share</Button>
    <Button panels:FlexPanel.MarginLeftAuto="True" panels:FlexPanel.Shrink="0">Settings</Button>
</panels:FlexPanel>
```

```xml
<!-- Equal columns (like CSS flex: 1 1 0) -->
<panels:FlexPanel Direction="Row" Gap="8">
    <Border panels:FlexPanel.Grow="1" panels:FlexPanel.Shrink="1" panels:FlexPanel.Basis="0">A</Border>
    <Border panels:FlexPanel.Grow="1" panels:FlexPanel.Shrink="1" panels:FlexPanel.Basis="0">B</Border>
    <Border panels:FlexPanel.Grow="1" panels:FlexPanel.Shrink="1" panels:FlexPanel.Basis="0">C</Border>
</panels:FlexPanel>
```

### Key Properties

| Property | Values | CSS Equivalent |
|---|---|---|
| `Direction` | `Row`, `RowReverse`, `Column`, `ColumnReverse` | `flex-direction` |
| `Wrap` | `NoWrap`, `Wrap`, `WrapReverse` | `flex-wrap` |
| `JustifyContent` | `Start`, `End`, `Center`, `SpaceBetween`, `SpaceAround`, `SpaceEvenly` | `justify-content` |
| `AlignItems` | `Start`, `End`, `Center`, `Stretch`, `Baseline` | `align-items` |
| `AlignContent` | `Start`, `End`, `Center`, `SpaceBetween`, `SpaceAround`, `SpaceEvenly`, `Stretch` | `align-content` |
| `Gap` / `RowGap` / `ColumnGap` | double | `gap` |

| Attached Property | Default | CSS Equivalent |
|---|---|---|
| `Grow` | 0 | `flex-grow` |
| `Shrink` | 1 | `flex-shrink` |
| `Basis` | Auto | `flex-basis` |
| `AlignSelf` | null (inherit) | `align-self` |
| `Order` | 0 | `order` |
| `MarginLeftAuto` | false | `margin-left: auto` (push right) |
| `MarginRightAuto` | false | `margin-right: auto` (push left) |
| `MarginTopAuto` | false | `margin-top: auto` (push down) |
| `MarginBottomAuto` | false | `margin-bottom: auto` (push up) |

### Rules

- **Use `Grow="1"` for the stretchy element**, `Shrink="0"` for fixed elements (buttons, icons).
- **Use `MarginLeftAuto="True"`** to push an element to the right end.
- **Prefer `Wrap="Wrap"`** over horizontal scroll for action bars and chip lists.
- **For equal columns**: Set `Grow="1" Shrink="1" Basis="0"` on each child.
- **For sticky footer**: Use `Direction="Column"` with `Grow="1"` on the content area, `MarginTopAuto="True"` on the footer.

---

## 🔧 Trick 2 — BootstrapGridPanel for Responsive Content Reflow

Use `BootstrapGridPanel` when content should **change column count at different screen widths**. This is Bootstrap 5's grid system, faithfully ported to Avalonia.

```xml
<!-- Cards: 1-col mobile, 2-col tablet, 3-col desktop -->
<panels:BootstrapGridPanel MaxColumns="12" Gutter="16" FluidContainer="True">
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6"
            panels:BootstrapGridPanel.ColLg="4">Card 1</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6"
            panels:BootstrapGridPanel.ColLg="4">Card 2</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6"
            panels:BootstrapGridPanel.ColLg="4">Card 3</Border>
</panels:BootstrapGridPanel>
```

```xml
<!-- App layout: stacked on mobile, sidebar + content on desktop -->
<panels:BootstrapGridPanel MaxColumns="12" Gutter="16" FluidContainer="True">
    <Border panels:BootstrapGridPanel.Col="12">Nav bar</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="3">Sidebar</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="9">Main content</Border>
    <Border panels:BootstrapGridPanel.Col="12">Footer</Border>
</panels:BootstrapGridPanel>
```

### 6 Breakpoint Tiers (identical to Bootstrap 5)

| Tier | Attached Property | Activates at width ≥ | Default Threshold |
|---|---|---|---|
| **Xs** | `Col` (base) | 0 | — |
| **Sm** | `ColSm` | `SmallBreakpoint` | 576 |
| **Md** | `ColMd` | `MediumBreakpoint` | 768 |
| **Lg** | `ColLg` | `LargeBreakpoint` | 992 |
| **Xl** | `ColXl` | `ExtraLargeBreakpoint` | 1200 |
| **Xxl** | `ColXxl` | `XXLBreakpoint` | 1400 |

### Cascading

If `ColLg` is not set, the panel falls back to `ColMd` → `ColSm` → `Col`. The same cascade applies to `Offset*` and `Order*` attached properties.

### Special Column Values

| Value | Meaning |
|---|---|
| Integer 1–12 | Fixed span (number of columns) |
| Auto (0, **default**) | Equal share of remaining columns in the row |
| AutoContent (-1) | Span computed from child's natural width. Set via `SetColAuto(child)` |

### Additional Per-Breakpoint Attached Properties

- `Offset` / `OffsetSm` / `OffsetMd` / `OffsetLg` / `OffsetXl` / `OffsetXxl` — shift position by N columns
- `Order` / `OrderSm` / `OrderMd` / `OrderLg` / `OrderXl` / `OrderXxl` — visual reordering
- `RowBreak` — force a new row even when there's space left

### Rules

- **Always set `FluidContainer="True"`** unless you specifically need Bootstrap's fixed max-widths.
- **Start mobile-first**: Set `Col` (base/Xs) first, then override upward: `ColSm`, `ColMd`, etc. Only set breakpoints that change the span.
- **Prefer `Gutter` over manual Margin**: The panel handles column and row gaps uniformly.
- **Use `RowBreak` for semantic rows**: Don't rely on overflow wrapping when you want an explicit row boundary.

---

## 🔧 Trick 3 — Nest Them

The real power comes from combining panels. Each panel handles one level of the layout hierarchy:

```
App Window
 └─ SemanticPanel               → app structure (sidebar + content zones)
     ├─ Sidebar zone
     │   └─ FlexPanel Column    → vertical nav links
     ├─ Primary zone
     │   └─ BootstrapGridPanel  → responsive content grid
     │       ├─ Card (Col=12, ColMd=6, ColLg=4)
     │       └─ Card (...)
     └─ ActionPrimary zone
         └─ FlexPanel Row       → toolbar with auto + stretch
```

### Nesting Rules

1. **SemanticPanel at the top** for app structure — never nest SemanticPanels.
2. **BootstrapGridPanel inside content zones** for responsive grids.
3. **FlexPanel inside grid cells** for local auto/stretch row behavior.
4. **Standard panels (StackPanel, Grid, DockPanel)** for leaf-level local layout.

---

## 🔧 Supporting Controls

### AdaptivePanel — Overflow Detection

Shows `Content` normally; swaps to `OverflowContent` when content doesn't fit. Use for collapsing toolbars, "show more" patterns.

```xml
<panels:AdaptivePanel OverflowDirection="Horizontal" SwitchTolerance="10">
    <panels:AdaptivePanel.Content>
        <StackPanel Orientation="Horizontal">
            <Button>Save</Button><Button>Export</Button><Button>Share</Button>
        </StackPanel>
    </panels:AdaptivePanel.Content>
    <panels:AdaptivePanel.OverflowContent>
        <Button>⋯</Button>
    </panels:AdaptivePanel.OverflowContent>
</panels:AdaptivePanel>
```

### ResponsivePresenter — Width-Based Template Swap

Swaps between `Narrow` and `Wide` content templates at a width breakpoint. Good for switching between table and card list views.

```xml
<controls:ResponsivePresenter Breakpoint="600">
    <controls:ResponsivePresenter.Wide>
        <DataTemplate><!-- Full table view --></DataTemplate>
    </controls:ResponsivePresenter.Wide>
    <controls:ResponsivePresenter.Narrow>
        <DataTemplate><!-- Card list view --></DataTemplate>
    </controls:ResponsivePresenter.Narrow>
</controls:ResponsivePresenter>
```

### BlueprintPanel — Text DSL Grid with Breakpoints

Grid layout defined by a text template. Numbers are child indices, `.` is empty. Supports breakpoint-specific layouts.

```xml
<panels:BlueprintPanel RowSpacing="8" ColumnSpacing="8">
    <panels:BlueprintPanel.Layouts>
        <panels:LayoutBreakpoint MinWidth="800" Blueprint="0 1 1 2 / 0 1 1 2 / 3 3 3 3" />
        <panels:LayoutBreakpoint MinWidth="500" Blueprint="0 1 / 2 1 / 3 3" />
        <panels:LayoutBreakpoint Blueprint="0 / 1 / 2 / 3" />
    </panels:BlueprintPanel.Layouts>
    <Border>Sidebar</Border>
    <Border>Main</Border>
    <Border>Widget</Border>
    <Border>Footer</Border>
</panels:BlueprintPanel>
```

---

## 📐 Panel Selection Decision Guide

| Scenario | Panel | Why |
|---|---|---|
| Toolbar / nav bar / button row | `FlexPanel` `Direction="Row"` | Auto + stretch, `MarginLeftAuto` for push-right |
| Cards / tiles that reflow by screen width | `BootstrapGridPanel` | Per-breakpoint column spans |
| App-level structure (sidebar + content) | `SemanticPanel` | Role-based zones, 3 size classes |
| Grid with text template + breakpoints | `BlueprintPanel` | DSL + `LayoutBreakpoint` collection |
| Uniform cards with aspect ratio | `CardPanel` | Auto-columns from aspect ratio + max width |
| Uniform items, auto-columns | `ResponsiveUniformGrid` or `BalancedWrapGrid` | Auto-columns from `MinColumnWidth` |
| Show/hide on overflow | `AdaptivePanel` | Swaps Content ↔ OverflowContent |
| Swap entire UI at a width threshold | `ResponsivePresenter` | Narrow/Wide templates |
| True-center with side elements | `TrueCenterPanel` | Center child truly centered regardless of sides |

---

## ❌ Anti-Patterns

### Don't hard-code layouts for a single screen size

```xml
<!-- ❌ WRONG — fixed 3-column grid, breaks on mobile -->
<Grid ColumnDefinitions="250,*,300">
    <Border Grid.Column="0">Sidebar</Border>
    <Border Grid.Column="1">Content</Border>
    <Border Grid.Column="2">Aside</Border>
</Grid>

<!-- ✅ RIGHT — responsive: stacks on mobile, side-by-side on tablet+ -->
<panels:BootstrapGridPanel MaxColumns="12" Gutter="16" FluidContainer="True">
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="3">Sidebar</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6">Content</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="3">Aside</Border>
</panels:BootstrapGridPanel>
```

### Don't use StackPanel for toolbars (clips on narrow)

```xml
<!-- ❌ WRONG — clips on narrow screens -->
<StackPanel Orientation="Horizontal" Spacing="8">
    <Button>Save</Button><Button>Export</Button><Button>Share</Button>
</StackPanel>

<!-- ✅ RIGHT — wraps and pushes -->
<panels:FlexPanel Direction="Row" Wrap="Wrap" Gap="8">
    <Button panels:FlexPanel.Shrink="0">Save</Button>
    <Button panels:FlexPanel.Shrink="0">Export</Button>
    <Button panels:FlexPanel.MarginLeftAuto="True" panels:FlexPanel.Shrink="0">Share</Button>
</panels:FlexPanel>
```

### Don't use UniformGrid for cards (no breakpoints)

```xml
<!-- ❌ WRONG — fixed 3 columns, no reflow -->
<UniformGrid Columns="3">
    <Border>Card 1</Border><Border>Card 2</Border><Border>Card 3</Border>
</UniformGrid>

<!-- ✅ RIGHT — 1 col mobile, 2 tablet, 3 desktop -->
<panels:BootstrapGridPanel MaxColumns="12" Gutter="16" FluidContainer="True">
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6"
            panels:BootstrapGridPanel.ColLg="4">Card 1</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6"
            panels:BootstrapGridPanel.ColLg="4">Card 2</Border>
    <Border panels:BootstrapGridPanel.Col="12"
            panels:BootstrapGridPanel.ColMd="6"
            panels:BootstrapGridPanel.ColLg="4">Card 3</Border>
</panels:BootstrapGridPanel>
```

---

## 🔗 XAML Namespace

```xml
xmlns:panels="clr-namespace:Zafiro.Avalonia.Controls.Panels;assembly=Zafiro.Avalonia"
xmlns:controls="clr-namespace:Zafiro.Avalonia.Controls;assembly=Zafiro.Avalonia"
```

## 📚 Evidence

- `src/Zafiro.Avalonia/Controls/Panels/FlexPanel.cs` — 800-line CSS Flexbox implementation
- `src/Zafiro.Avalonia/Controls/Panels/BootstrapGridPanel.cs` — Full Bootstrap 5 grid with 6 breakpoint tiers
- `samples/TestApp/TestApp/Samples/Panels/PanelsView.axaml` — BootstrapGridPanel demo
- `samples/TestApp/TestApp/Samples/Layout/FlexPanelView.axaml` — FlexPanel demo (7 scenarios)
- `samples/TestApp/TestApp/Samples/Layout/AdaptivePanelView.axaml` — AdaptivePanel demo
- `samples/TestApp/TestApp/Samples/Layout/ResponsivePresenter/ResponsivePresenterView.axaml` — ResponsivePresenter demo
- `test/Zafiro.Avalonia.Tests/Panels/BootstrapGridPanelTests.cs` — 44 headless tests validating all BootstrapGridPanel behavior
