---
name: avalonia-layout-zafiro
description: Guidelines for modern Avalonia UI layout using Zafiro.Avalonia, emphasizing shared styles, generic components, and avoiding XAML redundancy.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Avalonia Layout with Zafiro.Avalonia

> Master modern, clean, and maintainable Avalonia UI layouts.
> **Focus on semantic containers, shared styles, and minimal XAML.**

## 🚨 RULE ZERO: All Layouts Are Responsive by Default

**Every view, page, or component you create MUST use responsive panels.** This is not optional. Zafiro.Avalonia targets Desktop, Mobile, and Browser — a layout that only works at one size is a bug.

Before writing any AXAML layout, ask yourself:
1. **Is this a toolbar / bar / row of items?** → Use `FlexPanel` (not StackPanel).
2. **Is this a grid of content that should reflow?** → Use `BootstrapGridPanel` with per-breakpoint spans (not Grid/UniformGrid).
3. **Is this app-level structure?** → Use `SemanticPanel` or `BlueprintPanel`.

**Read `responsive.md` before any layout work.** It contains the complete reference.

## 🎯 Selective Reading Rule

**Read ONLY files relevant to the layout challenge!**

---

## 📑 Content Map

| File | Description | When to Read |
|------|-------------|--------------|
| `responsive.md` | **Responsive layout: FlexPanel, BootstrapGridPanel, nesting, panel selection** | **Any layout that must adapt to different screen sizes (ALWAYS read this first)** |
| `themes.md` | Theme organization and shared styles | Setting up or refining app themes |
| `containers.md` | Semantic containers (`HeaderedContainer`, `EdgePanel`, `Card`) | Structuring views and layouts |
| `icons.md` | Icon usage with `IconExtension` and `IconOptions` | Adding and customizing icons |
| `behaviors.md` | `Xaml.Interaction.Behaviors` and avoiding Converters | Implementing complex interactions |
| `components.md` | Generic components and avoiding nesting | Creating reusable UI elements |
| `scripts/avalonia_style_probe.py` | Style/resource scanner with computed-style estimate | Before applying local visual attributes |

---

## 🔗 Related Project (Exemplary Implementation)

For a real-world example, refer to the **Angor** project:
`/mnt/fast/Repos/angor/src/Angor/Avalonia/Angor.Avalonia.sln`

---

## ✅ Checklist for Clean Layouts

- [ ] **Responsive by default?** Used `FlexPanel`/`BootstrapGridPanel` instead of fixed Grid/StackPanel? (See `responsive.md`)
- [ ] **Mobile-first breakpoints?** Set `Col` (base) first, then override with `ColMd`, `ColLg`, etc.?
- [ ] **FlexPanel for toolbars?** Used `Grow`/`Shrink`/`MarginLeftAuto` instead of fixed StackPanel?
- [ ] **Used semantic containers?** (e.g., `HeaderedContainer` instead of `Border` with manual header)
- [ ] **Used `HeaderedContainer` for title+body cards?** If a block is "header + content", prefer `HeaderedContainer` with `Header`, `Content`, `HeaderClasses`, `ContentClasses`.
- [ ] **Avoided redundant properties?** Use shared styles in `axaml` files.
- [ ] **Scanned effective styles first?** Run `scripts/avalonia_style_probe.py` before adding local attributes.
- [ ] **Minimized nesting?** Flatten layouts using `EdgePanel` or generic components.
- [ ] **Icons via extension?** Use `{Icon fa-name}` and `IconOptions` for styling.
- [ ] **Behaviors over code-behind?** Use `Interaction.Behaviors` for UI-logic.
- [ ] **Avoided Converters?** Prefer ViewModel properties or Behaviors unless necessary.
- [ ] **Kept readability while compressing XAML?** Prefer explicit semantic markup over clever local abstractions.
- [ ] **Theme-aware interactive states?** Hover/selected/focus colors should come from `DynamicResource` backed by `ThemeDictionaries`, not hardcoded literals.

---

## ❌ Anti-Patterns

**DON'T:**

 - Use hardcoded colors or sizes (literals) in views.
 - **Use fixed Grid/StackPanel for layouts that should adapt to screen size.** Use `BootstrapGridPanel` or `FlexPanel` instead.
 - **Use `UniformGrid Columns="3"` for cards.** Use `BootstrapGridPanel` with per-breakpoint spans.
 - **Use `StackPanel Orientation="Horizontal"` for toolbars.** Use `FlexPanel` with `Wrap="Wrap"`.
 - Create deep nesting of `Grid` and `StackPanel`.
 - Add local properties before checking what styles already apply.
 - Repeat visual properties across multiple elements (use Styles).
 - Use `IValueConverter` for simple logic that belongs in the ViewModel.
 - Build cards as `Border + StackPanel + TextBlock(header) + TextBlock(content)` when `HeaderedContainer` fits.
 - Over-abstract readability away (many local style aliases/classes for one small view).
 - Hardcode light-mode hover colors without a dark-mode counterpart.
 - When a button has an icon, don't do this:

  ```
  <EnhancedButton Command="{Binding Invest}" DockPanel.Dock="Right" Classes="Outline">
      <StackPanel Orientation="Horizontal" Spacing="10">   
          <TextBlock Text="📈" />
          TextBlock Text="Invest Now" />
      </StackPanel> 
  </EnhancedButton>
  ```
  Instead, go with

   ```
  <EnhancedButton Icon="{Icon fa-chart-line}" Content="Invest Now" />
  ```


**DO:**
- Use `DynamicResource` for colors and brushes.
- Extract repeated layouts into generic components.
- Leverage `Zafiro.Avalonia` specific panels like `EdgePanel` for common UI patterns.

## 🧠 Semantic Container Decision Rules

Use this decision rule during layout work:

1. If a visual block has **title + content** semantics, default to `HeaderedContainer`.
2. If it also needs start/end adornments, prefer `EdgePanel` inside `HeaderedContainer` (or as header content).
3. Keep `Border` for purely decorative wrappers with no semantic header/content meaning.

**Preferred pattern (card-like block):**
```xml
<HeaderedContainer Classes="Card White Radius-M"
                   Header="Desktop App"
                   Content="Coming soon"
                   HeaderClasses="Size-L Weight-Bold Text-Strong"
                   ContentClasses="Size-S Text-Muted" />
```

**Avoid when equivalent semantic container exists:**
```xml
<Border Classes="ColorPanel White Radius-M">
  <StackPanel Classes="Gap-XS">
    <TextBlock Classes="Size-L Weight-Bold Text-Strong">Desktop App</TextBlock>
    <TextBlock Classes="Size-S Text-Muted">Coming soon</TextBlock>
  </StackPanel>
</Border>
```

## 👀 Readability vs Compression Guardrails

Compression is good only when intent remains obvious on first read.

- Prefer explicit semantic properties (`Header`, `Content`, `HeaderClasses`, `ContentClasses`) over "magic" local aliases when scope is small.
- Avoid introducing many local style names for a single view unless they are reused several times or improve clarity.
- After refactoring, do a quick readability pass: a teammate should understand structure without jumping across many style definitions.

## 🌗 Theme-aware Interactive State Rules

For stateful visuals (hover, selected, focus, pressed):

- Define state brushes via `ThemeDictionaries` (`Light` and `Dark`).
- Bind state setters to `{DynamicResource ...}`.
- Never ship light-only literals for interactive state colors.

**Pattern:**
```xml
<UserControl.Resources>
  <ResourceDictionary>
    <ResourceDictionary.ThemeDictionaries>
      <ResourceDictionary x:Key="Light">
        <SolidColorBrush x:Key="Highlight.Background">#F9FBFB</SolidColorBrush>
      </ResourceDictionary>
      <ResourceDictionary x:Key="Dark">
        <SolidColorBrush x:Key="Highlight.Background">#1F2937</SolidColorBrush>
      </ResourceDictionary>
    </ResourceDictionary.ThemeDictionaries>
  </ResourceDictionary>
</UserControl.Resources>

<Style Selector=":is(TemplatedControl):pointerover.Highlight">
  <Setter Property="Background" Value="{DynamicResource Highlight.Background}" />
</Style>
```

## 🚨 Mandatory Preflight: Style Scan Before Local Attributes

Before touching any local visual property (`Background`, `Foreground`, `FontSize`, `Padding`, etc.), the agent must inspect the project's style/resource graph and estimate the final computed properties for the target control.

Use:
```bash
python3 /home/jmn/skills/avalonia-layout-zafiro/scripts/avalonia_style_probe.py \
  --project-root <repo-root> \
  --control <ControlType> \
  --classes <Class1,Class2> \
  --show-tree
```

Resolution mode:
- By default, the probe auto-detects root style files (`App.axaml`/`App.xaml`, fallback `Styles.axaml`/`Styles.xaml`) and traverses transitive includes from there.
- Use `--root <file>` to force one or more root files explicitly.
- Use `--scan-all` only for exploratory scans (less faithful to runtime).

Rules:
- **Always run the probe first** when styling Avalonia XAML.
- **Do not add local attributes** unless the probe output shows the property is not already set as needed.
- If a local override is still needed, keep it minimal and explain why shared style/theme could not cover it.

## 🕵️ Method: Discovering & Applying Styles

**Principle:** Never invent class names (e.g., `H1`, `Card`, `Caption`). Instead, **scan the project resources** to find the definitions.

### 1. Locate the Theme/Style Definitions
Search for the theme configuration. Common locations:
- `App.axaml`: Often contains `<StyleInclude>` for the main theme.
- `Themes/` or `Styles/` directories: Look for `.axaml` files.
- `Styles.axaml`: In library projects.

### 2. Scan for Defined Classes
Open the relevant `.axaml` files (e.g., `Typography.axaml`, `Buttons.axaml`, `Containers.axaml`) and search for `Style Selector`.

**Pattern to look for:**
```xml
<Style Selector="TextBlock.Title"> ... </Style>
<Style Selector="Border.Panel"> ... </Style>
<Style Selector="HeaderedContainer.WizardSection"> ... </Style>
```
*The part after the dot (e.g., `Title`, `Panel`) is the Class name.*

### 3. Probe the Effective Result for the Target Control
Run `scripts/avalonia_style_probe.py` with the target control and classes to estimate:
- merged styles and resource includes
- winning setter per property
- likely final values (including `StaticResource` / `DynamicResource` resolution when available)

### 4. Verify & Apply
Once you confirm the class exists, apply it using the `Classes` property.

```xml
<!-- ✅ CORRECT: Verified class 'Title' exists in Typography.axaml -->
<TextBlock Classes="Title" Text="My Header" />

<!-- ❌ INCORRECT: Guessing a class name -->
<TextBlock Classes="H1" Text="My Header" />
```

### 5. Check for Resources (Keys)
If you can't find a class, look for `ControlTheme` or `StaticResource` keys in `ResourceDictionary`.

```xml
<!-- Finding the key -->
<ControlTheme x:Key="TransparentButton" ... />

<!-- Applying it -->
<EnhancedButton Theme="{StaticResource TransparentButton}" ... />
```

### 6. Apply TextBlock Classes to Headers (No Style Chaining)
When a header is just a string (e.g., `Header="Project Statistics"`), you cannot "apply a style to another style".
Wrap the header with a `HeaderTemplate` and use atomic classes on a `TextBlock`.

```xml
<Style Selector="HeaderedContainer.Big">
  <Setter Property="HeaderTemplate">
    <DataTemplate>
      <TextBlock Classes="Size-XL Weight-Bold" Text="{Binding}" />
    </DataTemplate>
  </Setter>
</Style>
```

**Notes:**
- The template applies only when the header is not already a control.
- Prefer existing semantic classes (e.g., `Title`) if they match your intent.

---

## 🎨 Common "Zafiro-like" Patterns (Verify first!)

While every project is different, Zafiro-based projects often use these semantic patterns. **Scan files to confirm**:

*   **Typography**: Look for `Title`, `Subtitle`, `Header`, `Caption`, or atomic sizes (`Size-S`, `Size-L`) and weights (`Weight-Bold`).
*   **Containers**: Look for `Panel` (often a Border with shadow/bg) or `Section` styles for `HeaderedContainer`.
*   **Buttons**: Look for semantic roles (`Primary`, `Secondary`) or visual styles (`Outline`, `Ghost`/`Transparent`).
