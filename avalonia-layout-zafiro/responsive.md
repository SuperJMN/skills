# Responsive Layout — The Four Tricks

> How to build adaptive UIs that work on Desktop, Tablet, Mobile, and Browser — using the same primitives that make web layouts "magic": **Flexbox + Bootstrap Grid + Container Queries**.

## 🚨 Mandatory: Responsive Is the Default, Not an Upgrade

**Every layout you produce MUST be responsive.** There is no "desktop-only" mode. When creating any view:

- **Never use `StackPanel Orientation="Horizontal"` for toolbars** → Use `FlexPanel` with `Wrap="Wrap"`.
- **Never use `Grid ColumnDefinitions="..."` for content that should reflow** → Use `BootstrapGridPanel` with `Col`/`ColMd`/`ColLg`.
- **Never use `UniformGrid Columns="N"` for cards** → Use `BootstrapGridPanel` with per-breakpoint spans.

The only acceptable uses of fixed `Grid` are: form field alignment (label + input), and truly fixed structural elements (e.g., a dialog with known dimensions). Everything else is responsive.

---

## 🗺️ The Web ↔ Zafiro Map

| Web Primitive | Zafiro / Avalonia | Use For |
|---|---|---|
| CSS Flexbox | **`FlexPanel`** | 1D flow: toolbars, button groups, navbars, centering |
| Bootstrap Grid (12-col) | **`BootstrapGridPanel`** | Content reflow: cards, forms, dashboards |
| `@container` queries | **`ContainerQuery`** (Avalonia native) | Change properties when container crosses a width/height threshold |
| `@media` queries | `ContainerQuery` on `TopLevel` | Same, but responding to window size |
| `@media (form-factor)` | **`OnFormFactor`** | Resolve once at startup: Desktop vs Mobile vs TV |
| CSS Grid / `@media` | **`SemanticPanel`** / **`BlueprintPanel`** | App-level structure: sidebar + primary + secondary |
| `display:none` / `@media` swap | **`AdaptivePanel`** / **`ResponsivePresenter`** | Show/hide or swap content at breakpoints |

---

## ⚠️ Critical Rule: Local Values vs ContainerQuery

**The #1 gotcha with ContainerQuery.** In Avalonia, local values (attributes set directly on a control) **always win** over styles — including ContainerQuery styles. This is equivalent to CSS inline `style="..."` beating `@container`.

```xml
<!-- ❌ WRONG — ContainerQuery can NEVER override this Direction -->
<FlexPanel x:Name="Shell" Direction="ColumnReverse" />

<!-- ✅ RIGHT — Default set via Style, ContainerQuery can override -->
<Style Selector="FlexPanel#Shell">
    <Setter Property="Direction" Value="ColumnReverse" />
</Style>
<FlexPanel x:Name="Shell" />
```

**Rule: Any property that ContainerQuery must control MUST be set via a Style, not as a local attribute.**

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

## 🔧 Trick 3 — ContainerQuery for Responsive Property Changes

**This is the missing link that makes Avalonia layouts work exactly like the web.** Avalonia's native `ContainerQuery` is the equivalent of CSS `@container` queries — it changes style properties when a container crosses a size threshold.

### The Pattern: FlexPanel + ContainerQuery = Responsive Shell

This is how web developers build responsive sidebars, and it works identically in Avalonia:

**CSS equivalent:**
```css
.shell { display: flex; flex-direction: column-reverse; }
.sidebar { flex-shrink: 0; }
.content { flex-grow: 1; }
@container shell (min-width: 500px) {
    .shell { flex-direction: row; }
    .sidebar { width: 200px; }
    .sidebar-nav { flex-direction: column; }
}
```

**Avalonia equivalent:**
```xml
<UserControl.Styles>
    <!-- Mobile-first defaults (MUST be Styles, not local values!) -->
    <Style Selector="FlexPanel#ShellLayout">
        <Setter Property="Direction" Value="ColumnReverse" />
    </Style>
    <Style Selector="FlexPanel#SidebarNav">
        <Setter Property="Direction" Value="Row" />
        <Setter Property="JustifyContent" Value="SpaceEvenly" />
    </Style>
</UserControl.Styles>

<!-- Container that tracks its own width -->
<Border Container.Name="shell" Container.Sizing="Width">
    <Border.Styles>
        <!-- Desktop: sidebar left, nav vertical -->
        <ContainerQuery Name="shell" Query="min-width:500">
            <Style Selector="FlexPanel#ShellLayout">
                <Setter Property="Direction" Value="Row" />
            </Style>
            <Style Selector="Border#Sidebar">
                <Setter Property="Width" Value="200" />
            </Style>
            <Style Selector="FlexPanel#SidebarNav">
                <Setter Property="Direction" Value="Column" />
            </Style>
        </ContainerQuery>
    </Border.Styles>

    <FlexPanel x:Name="ShellLayout" AlignItems="Stretch">
        <Border x:Name="Sidebar" FlexPanel.Shrink="0">
            <FlexPanel x:Name="SidebarNav" Gap="4" AlignItems="Center">
                <TextBlock Text="🏠 Home" />
                <TextBlock Text="📊 Analytics" />
                <TextBlock Text="⚙️ Settings" />
            </FlexPanel>
        </Border>
        <Border FlexPanel.Grow="1">
            <!-- Content fills remaining space -->
        </Border>
    </FlexPanel>
</Border>
```

### How it works
1. **Mobile-first**: `Direction="ColumnReverse"` puts sidebar at bottom, nav is horizontal
2. **Desktop** (≥500px): `ContainerQuery` overrides to `Direction="Row"`, sidebar gets fixed width, nav becomes vertical
3. **One property flip** on the panel reorganizes the entire layout

### ContainerQuery Syntax Reference

**Declaring a container:**
```xml
<Border Container.Name="mycontainer" Container.Sizing="Width">
```

`Container.Sizing` values: `Normal` (none), `Width`, `Height`, `WidthAndHeight`

**Writing queries:**
```xml
<ContainerQuery Name="mycontainer" Query="min-width:600">
    <Style Selector="...">
        <Setter Property="..." Value="..." />
    </Style>
</ContainerQuery>
```

**Combining conditions:**
```xml
<!-- AND: both must match -->
<ContainerQuery Name="x" Query="min-width:400 and max-width:800">

<!-- OR: either can match -->
<ContainerQuery Name="x" Query="max-width:300,min-height:600">
```

**Window-level queries:** Set `Container.Name` and `Container.Sizing` on the `TopLevel` (window) to make ContainerQuery behave like CSS `@media` queries.

### Why FlexPanel + ContainerQuery over DockPanel

| Aspect | FlexPanel | DockPanel |
|---|---|---|
| Layout change | 1 setter: `Direction` on panel | N setters: `DockPanel.Dock` on each child |
| Fill remaining space | `Grow="1"` (explicit, any child) | `LastChildFill` (implicit, last child only) |
| Cross-axis alignment | `AlignItems`, `JustifyContent` | None |
| Auto-margin push | `MarginLeftAuto` | None |
| Wrapping | `Wrap="Wrap"` | None |

**Use FlexPanel** for any layout that needs to adapt. Reserve DockPanel/SmartDockPanel for fixed structural shells that never change.

---

## 🔧 Trick 4 — Nest Them

The real power comes from combining panels. Each panel handles one level of the layout hierarchy:

```
App Window
 └─ FlexPanel + ContainerQuery  → responsive shell (sidebar + content)
     ├─ Sidebar zone
     │   └─ FlexPanel Column    → vertical nav links (Row on mobile)
     └─ Content zone
         └─ BootstrapGridPanel  → responsive content grid
             ├─ Card (Col=12, ColMd=6, ColLg=4)
             └─ Card (...)
```

### Nesting Rules

1. **FlexPanel + ContainerQuery** for responsive structural layout (sidebar/content, toolbar direction changes).
2. **BootstrapGridPanel inside content zones** for responsive grids (no ContainerQuery needed — breakpoints are built in).
3. **FlexPanel inside grid cells** for local auto/stretch row behavior.
4. **SemanticPanel or BlueprintPanel** for app-level structure with predefined roles (if role-based semantics are needed).
5. **Standard panels (StackPanel, Grid, DockPanel)** for leaf-level local layout.

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
| Sidebar + content (responsive) | `FlexPanel` + `ContainerQuery` | Direction flip, Grow for fill |
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

### Don't set local values on properties controlled by ContainerQuery

```xml
<!-- ❌ WRONG — local value beats ContainerQuery, layout never changes -->
<FlexPanel x:Name="Shell" Direction="ColumnReverse" />

<!-- ✅ RIGHT — default via Style, ContainerQuery can override -->
<Style Selector="FlexPanel#Shell">
    <Setter Property="Direction" Value="ColumnReverse" />
</Style>
<FlexPanel x:Name="Shell" />
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
- `samples/TestApp/TestApp/Samples/Layout/ResponsiveLayoutsView.axaml` — **Verified responsive layout demo** (FlexPanel + ContainerQuery + BootstrapGridPanel)
- `samples/TestApp/TestApp/Samples/Layout/FlexPanelView.axaml` — FlexPanel demo (7 scenarios)
- `samples/TestApp/TestApp/Samples/Panels/PanelsView.axaml` — BootstrapGridPanel demo
- `docs/ai/responsive-design.md` — Responsive design recipes with complete examples
- `test/Zafiro.Avalonia.Tests/Panels/BootstrapGridPanelTests.cs` — 44 headless tests validating all BootstrapGridPanel behavior
