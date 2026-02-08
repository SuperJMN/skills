---
name: avalonia-zafiro-development
description: Mandatory skills, conventions, and behavioral rules for Avalonia UI development using the Zafiro toolkit.
---

# Avalonia Zafiro Development

This skill defines the mandatory conventions and behavioral rules for developing cross-platform applications with Avalonia UI and the Zafiro toolkit. These rules prioritize maintainability, correctness, and a functional-reactive approach.

## Core Pillars

1.  **Functional-Reactive MVVM**: Pure MVVM logic using DynamicData and ReactiveUI.
2.  **Safety & Predictability**: Explicit error handling with `Result` types and avoidance of exceptions for flow control.
3.  **Cross-Platform Excellence**: Strictly Avalonia-independent ViewModels and composition-over-inheritance.
4.  **Zafiro First**: Leverage existing Zafiro abstractions and helpers to avoid redundancy.

## Zafiro Controls Best Practices

### Use `EnhancedButton` Instead of `Button`

**CRITICAL**: Always use `EnhancedButton` from Zafiro.Avalonia instead of the standard Avalonia `Button`.

**Why?**
- **IEnhancedCommand Support**: Natural binding for `IEnhancedCommand` with automatic execution state tracking
- **IsCommandRunning**: Automatically reflects command execution state (shows loading/busy state)
- **Role-Based Styling**: Supports `ButtonRole` enum for semantic button types
- **Icon Support**: Built-in `Icon` property for richer UI
- **Intent-Based Semantics**: `ButtonIntent` for additional context (Success, Warning, Danger, etc.)

#### ButtonRole Values:

```csharp
public enum ButtonRole
{
    Primary,    // Main action button (e.g., "Save", "Submit")
    Secondary,  // Less important action (e.g., "Cancel")
    Ghost,      // Minimal style, almost invisible
    Destructive,// Dangerous action (e.g., "Delete")
    Link        // Looks like a hyperlink
}
```

#### Usage Examples:

```xml
<!-- Basic usage with IEnhancedCommand -->
<EnhancedButton Content="Save" 
                Command="{Binding SaveCommand}" />

<!-- With Role for semantic styling -->
<EnhancedButton Content="Delete" 
                Command="{Binding DeleteCommand}"
                c:EnhancedButton.Role="Destructive" />

<!-- With Icon -->
<EnhancedButton Content="Create New">
    <EnhancedButton.Icon>
        <ui:Icon Source="mdi-plus" />
    </EnhancedButton.Icon>
</EnhancedButton>

<!-- Multiple buttons with different roles -->
<StackPanel Orientation="Horizontal" Spacing="10">
    <EnhancedButton Content="Cancel" 
                    c:EnhancedButton.Role="Secondary"
                    Command="{Binding CancelCommand}" />
    <EnhancedButton Content="Save" 
                    c:EnhancedButton.Role="Primary"
                    Command="{Binding SaveCommand}" />
</StackPanel>
```

#### Key Features:

- **Automatic Busy State**: When an `IEnhancedCommand` is executing, `IsCommandRunning` is automatically set to `true`
- **Semantic Roles**: Use `ButtonRole` to convey intent, not just visual style
- **Consistent Styling**: All buttons follow Zafiro's design system when using roles
- **Better DX**: IntelliSense shows available roles and intents

**Pattern:**
```csharp
// ViewModel
public IEnhancedCommand SaveCommand { get; }

// View
<EnhancedButton Content="Save" 
                Command="{Binding SaveCommand}"
                c:EnhancedButton.Role="Primary" />
```

**Anti-Pattern:**
```xml
<!-- ❌ Don't use standard Button -->
<Button Content="Save" Command="{Binding SaveCommand}" />

<!-- ✅ Use EnhancedButton -->
<EnhancedButton Content="Save" Command="{Binding SaveCommand}" />
```

---

### Omit `xmlns` Prefixes for Zafiro Controls

**IMPORTANT**: All `Zafiro.Avalonia*` namespaces are registered as **local namespaces** in the project. This means you do NOT need to declare or use prefixes for Zafiro controls.

**Why?**
- **Cleaner XAML**: Less namespace clutter
- **Consistent**: Zafiro controls work just like built-in Avalonia controls
- **Auto-registered**: The framework handles namespace resolution automatically

#### Correct Pattern:

```xml
<!-- ✅ No prefix needed for Zafiro controls -->
<EnhancedButton Content="Save" Command="{Binding SaveCommand}" />

<HeaderedContainer Header="My Section">
    <TextBlock Text="Content here" />
</HeaderedContainer>

<Icon Source="mdi-check" />
```

#### Anti-Pattern:

```xml
<!-- ❌ Don't add unnecessary prefixes -->
<c:EnhancedButton Content="Save" Command="{Binding SaveCommand}" />

<zafiro:HeaderedContainer Header="My Section">
    <TextBlock Text="Content here" />
</zafiro:HeaderedContainer>

<ui:Icon Source="mdi-check" />
```

**Exception**: Only use prefixes when there's a naming conflict or the code doesn't compile without them.

**Example with necessary prefix**:
```xml
<!-- If there's a conflict, then use prefix -->
<local:MyCustomButton />  <!-- ✅ Necessary if conflicts with Zafiro.Avalonia -->
```

## Guides

- [General C# Development Standards](../csharp-development-zafiro/SKILL.md): Fundamental C# naming and functional patterns.
- [Core Technical Skills & Architecture](core-technical-skills.md): Fundamental skills and architectural principles.
- [Avalonia, Zafiro & Reactive Rules](avalonia-reactive-rules.md): Specific guidelines for UI, Zafiro integration, and DynamicData pipelines.
- [Zafiro Shortcuts](zafiro-shortcuts.md): Concise mappings for common Rx/Zafiro operations.
- [Common Patterns](patterns.md): Advanced patterns like `RefreshableCollection` and Validation.

## Xaml.Behaviors (Avalonia)

Use Xaml.Behaviors when you need view-side interactions without code-behind. Attach behaviors with `Interaction.Behaviors` (or `BehaviorCollectionTemplate` in styles). Prefer `ExecuteCommandOn*Behavior` for direct event-to-command, `EventTriggerBehavior` for multi-action workflows, `DataTriggerBehavior`/`MultiDataTriggerBehavior` for property conditions, and `ObservableStreamBehavior` for `IObservable` streams. For drag-and-drop use `ContextDragBehavior`/`ContextDropBehavior` (or `TypedDragBehavior` for typed payloads, `ManagedContext*` for managed flows). For responsive layout use `AdaptiveBehavior`/`AspectRatioBehavior`. For file pickers use the `Button*PickerBehavior` or `MenuItem*PickerBehavior`.

Docs and examples (repo):
- docfx/articles/intro.md, docfx/articles/mvvm-and-behaviors.md, docfx/articles/architecture.md
- docfx/articles/interactivity/*, docfx/articles/interactions/*, docfx/articles/interactions-custom/*, docfx/articles/events/*, docfx/articles/responsive/*, docfx/articles/drag-and-drop/*, docfx/articles/draggable/*, docfx/articles/reactiveui/*, docfx/articles/filesystem/*, docfx/articles/network/*, docfx/articles/scripting/*, docfx/articles/source-generators/*
- samples/BehaviorsTestApplication/Views/Pages/*BehaviorView.axaml
- samples/SourceGeneratorSample/Views/Pages/*

Note: these paths are inside the `Xaml.Behaviors` repo. If you don’t have that repo locally, use the online docs (`https://wieslawsoltes.github.io/Xaml.Behaviors/`) or clone the repo.

Catalogs with per-item documentation links live in `references/xaml-behaviors-catalog.md` (Behaviors + Triggers + Actions). Use that file to look up each behavior and its docs/samples/source quickly.

Top behaviors (quick reference):
- `EventTriggerBehavior`: event → actions; use for multi-step UI reactions (common action: `AddClassAction`).
- `ExecuteCommandOn*Behavior`: event/gesture → command; use for MVVM command wiring without code-behind.
- `BindingTriggerBehavior` / `DataTriggerBehavior` / `MultiDataTriggerBehavior` / `ObservableStreamBehavior`: data conditions or `IObservable` streams.
- `AdaptiveBehavior` / `AspectRatioBehavior`: responsive class toggling based on size/aspect.
- `ContextDragBehavior` + `ContextDropBehavior` (plus `TypedDragBehavior`, `ManagedContext*`): drag & drop workflows.

## Procedure Before Writing Code

1.  **Search First**: Search the codebase for similar implementations or existing Zafiro helpers.
2.  **Reusable Extensions**: If a helper is missing, propose a new reusable extension method instead of inlining complex logic.
3.  **Reactive Pipelines**: Ensure DynamicData operators are used instead of plain Rx where applicable.

## Style Registration

**CRITICAL**: When creating new XAML style files (`.axaml` files containing `<Styles>` or `<ControlTheme>`), you **MUST** register them in the appropriate root style file.

### Finding the Registration File

The location depends on the project type:

1. **Avalonia Applications** (e.g., `TestApp`): Register in `App.axaml`
2. **Avalonia Toolkits/Libraries** (e.g., `Zafiro.Avalonia`): Register in `Styles.axaml` at the project root
3. **Unclear?**: Search the tree structure to identify where existing `.axaml` files are registered:
   ```bash
   # Find all StyleInclude references
   grep -r "StyleInclude Source" --include="*.axaml"
   ```

### Registration Pattern

```xml
<!-- In Styles.axaml or App.axaml -->
<StyleInclude Source="Path/To/YourNewStyle.axaml" />
```

### Choosing the Root Element: ResourceDictionary vs Styles

#### Use **ResourceDictionary** when…

👉 **You're defining things**, not applying them directly.

Use it if the content is primarily:

* **ControlThemes** (lookless defaults)
* **Brushes, Thickness, CornerRadius, Fonts**
* **Templates** consumed via `Theme` or `DynamicResource`
* Resources you want to be **overridable by key**
* Dictionaries to be **merged** (Light/Dark, Fluent/Simple, per-control)

👉 Key question:

> *"Do I want this to exist as a reusable resource, not to be applied by matching?"*

If yes → `ResourceDictionary`.

**Example:**
```xml
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <ControlTheme x:Key="{x:Type MyControl}" TargetType="MyControl">
        <!-- Default lookless theme -->
    </ControlTheme>
    
    <SolidColorBrush x:Key="MyBrush" Color="#FF0000" />
</ResourceDictionary>
```

**Gradient note:** When defining `LinearGradientBrush` `StartPoint`/`EndPoint`, use percentage coordinates (e.g., `0%,0%` to `100%,100%`) instead of integer coordinates to avoid inconsistent rendering.

---

### Design Previews: Always Use `<Design.PreviewWith>`

**CRITICAL**: Always include design previews in your `.axaml` files using `<Design.PreviewWith>`.

**Why?**
- Enables **visual development** in the Avalonia Previewer
- Documents **usage examples** directly in the style file
- Catches **visual regressions** during development
- Makes **code reviews** easier (reviewers can see the visual impact)

#### For Lookless Controls (Styles):

```xml
<Styles xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:view="clr-namespace:YourNamespace">

    <Design.PreviewWith>
        <view:GraphWizardView Width="500" Height="400">
            <!-- Example usage with sample data -->
            <view:GraphWizardView.DataContext>
                <DesignViewModel />
            </view:GraphWizardView.DataContext>
        </view:GraphWizardView>
    </Design.PreviewWith>

    <Style Selector="view|GraphWizardView">
        <!-- ControlTemplate definition -->
    </Style>
</Styles>
```

#### For ResourceDictionary (ControlThemes):

```xml
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:view="clr-namespace:YourNamespace">

    <Design.PreviewWith>
        <StackPanel Spacing="10" Margin="20">
            <view:MyControl Width="200" Content="Example 1" />
            <view:MyControl Width="200" Content="Example 2" IsEnabled="False" />
            <view:MyControl Width="200" Content="Hover Me" Classes="accent" />
        </StackPanel>
    </Design.PreviewWith>

    <ControlTheme x:Key="{x:Type view:MyControl}" TargetType="view:MyControl">
        <!-- Theme definition -->
    </ControlTheme>
</ResourceDictionary>
```

**Best Practices:**
- Show **multiple states** (normal, disabled, focused, etc.)
- Include **different variants** (primary, secondary, etc.)
- Use **realistic data** (not "Lorem ipsum")
- Keep preview **simple but representative**

---

### Compiled Bindings: Always Use `x:DataType`

**CRITICAL**: Always specify `x:DataType` in your `.axaml` files to enable compiled bindings.

**Why?**
- **Performance**: Compiled bindings are significantly faster than reflection-based bindings
- **Type Safety**: Compile-time errors instead of runtime binding failures
- **IntelliSense**: Better IDE support with autocomplete for properties
- **Refactoring**: Renaming properties updates bindings automatically

#### For Views (UserControl, Window):

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:vm="clr-namespace:YourNamespace.ViewModels"
             x:Class="YourNamespace.Views.MyView"
             x:DataType="vm:MyViewModel">
    
    <!-- Now bindings are compiled and type-checked -->
    <TextBlock Text="{Binding UserName}" />
    <TextBlock Text="{Binding Email}" />
</UserControl>
```

#### For DataTemplates:

```xml
<DataTemplate DataType="vm:ItemViewModel">
    <!-- DataType already provides x:DataType implicitly -->
    <TextBlock Text="{Binding Name}" />
</DataTemplate>

<!-- For explicit x:DataType in complex scenarios -->
<DataTemplate x:DataType="vm:ItemViewModel">
    <TextBlock Text="{Binding Name}" />
</DataTemplate>
```

#### For Lookless Controls:

```xml
<Styles xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:view="clr-namespace:YourNamespace">

    <Style Selector="view|GraphWizardView">
        <Setter Property="Template">
            <ControlTemplate>
                <!-- Use $parent[] syntax for type-safe parent access -->
                <TextBlock Text="{Binding $parent[view:GraphWizardView].CurrentStep.Title}" />
            </ControlTemplate>
        </Setter>
    </Style>
</Styles>
```

**Best Practices:**
- ✅ **Always** add `x:DataType` to UserControls, Windows, and Views
- ✅ Use `DataType` in DataTemplates (provides implicit `x:DataType`)
- ✅ Prefer `{Binding Property}` over `{Binding #ElementName.Property}` when possible
- ✅ Use `$parent[Type]` syntax in templates for type-safe parent access
- ❌ Avoid reflection-based bindings in production code

**Common Pattern:**
```xml
<!-- ViewModel -->
<UserControl x:DataType="vm:MyViewModel">
    <TextBlock Text="{Binding Title}" />
</UserControl>

<!-- Design-time DataContext -->
<Design.DataContext>
    <vm:MyViewModel />
</Design.DataContext>
```

---

#### Use **Styles** when…

👉 **You're applying visual rules** to controls in the visual tree.

Use it if you need:

* **Selectors** (`Button.primary`, `TextBox:focus`, `Border > TextBlock`)
* **Contextual** styles (by class, pseudo-class, hierarchy)
* Local overrides ("in this panel, all buttons…")
* Behavior dependent on **style order**
* Fine-tuning or modifying **on top of** an existing ControlTheme

👉 Key question:

> *"Do I want Avalonia to automatically match and apply this?"*

If yes → `Styles`.

**Example:**
```xml
<Styles xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <Style Selector="Button.primary">
        <Setter Property="Background" Value="Blue" />
    </Style>
    
    <Style Selector="TextBox:focus">
        <Setter Property="BorderBrush" Value="Accent" />
    </Style>
</Styles>
```

---

#### Golden Rule (Very Avalonia)

> **ControlTheme = resource → ResourceDictionary**
> **Selector = behavior → Styles**

While you can technically mix them, this criterion avoids 90% of friction.

---

#### Recommended Pattern (Avalonia Convention)

* 📦 **ResourceDictionary**
  * Control's ControlTheme
  * Control's base resources

* 🎨 **Styles**
  * Variants by class/role
  * Contextual adjustments
  * Consumer customization

---

#### Mental Model Translation

* `ResourceDictionary` → *"what this control is by default"*
* `Styles` → *"how it behaves visually here"*

---

## Lookless Control File Naming

When creating a **lookless control** (TemplatedControl), follow this file structure:

```
MyControl.axaml      ← Visual definition (Styles with ControlTemplate)
MyControl.axaml.cs   ← Code-behind (TemplatedControl class)
```

### Critical Rule

**The code-behind file MUST be named `[ControlName].axaml.cs`**, not just `[ControlName].cs`.

**Why?**
- The `.axaml.cs` suffix tells the IDE that the `.cs` file is the code-behind for the `.axaml` file
- Visual Studio/Rider will group them together in the Solution Explorer
- Enables proper XAML IntelliSense and navigation

### Correct Pattern:

```
✅ GraphWizardView.axaml
✅ GraphWizardView.axaml.cs

❌ GraphWizardView.axaml
❌ GraphWizardView.cs        ← Wrong! Won't be recognized as code-behind
```

### Code-Behind Structure:

```csharp
// GraphWizardView.axaml.cs
using Avalonia.Controls.Primitives;

namespace YourNamespace;

public class GraphWizardView : TemplatedControl
{
    // StyledProperties and logic here
}
```

**Note**: Unlike UserControls, TemplatedControls don't need `InitializeComponent()` or a constructor.

Common locations for style includes:
- **Controls**: `Controls/YourControl.axaml`
- **Wizards**: `Controls/Wizards/Type/WizardComponent.axaml` or `GraphWizard/View/ComponentView.axaml`
- **Dialogs**: Already included via `avares://Zafiro.Avalonia.Dialogs/Styles.axaml`

**Why this matters**: Avalonia requires explicit style registration. Missing this step means your ControlThemes won't be applied, resulting in invisible or unstyled controls.

### Checklist for New Style Files

- [ ] Identify the correct registration file (`App.axaml` or `Styles.axaml`)
- [ ] Create the `.axaml` style file
- [ ] Add `<StyleInclude Source="..."/>` to the registration file
- [ ] Verify the relative path is correct from the registration file
- [ ] Build and test to ensure styles are applied
