---
name: avalonia-viewmodels-zafiro
description: Optimal ViewModel and Wizard creation patterns for Avalonia using Zafiro and ReactiveUI.
---

# Avalonia ViewModels with Zafiro

This skill provides a set of best practices and patterns for creating ViewModels, Wizards, and managing navigation in Avalonia applications, leveraging the power of **ReactiveUI** and the **Zafiro** toolkit.

## Core Principles

1.  **Functional-Reactive Approach**: Use ReactiveUI (`ReactiveObject`, `WhenAnyValue`, etc.) to handle state and logic.
2.  **Enhanced Commands**: Utilize `IEnhancedCommand` for better command management, including progress reporting and name/text attributes.
3.  **Wizard Pattern**: Implement complex flows using `SlimWizard` and `WizardBuilder` for a declarative and maintainable approach.
4.  **Automatic Section Discovery**: Use the `[Section]` attribute to register and discover UI sections automatically.
5.  **Clean Composition**: map ViewModels to Views using `DataTypeViewLocator` and manage dependencies in the `CompositionRoot`.
6.  **Collection Aggregates**: When a value is derived from a collection (totals/counts), use DynamicData aggregation (`Sum`, `Count`) on the change set and expose it as `IObservable<T>`; bind in XAML with `^`. Avoid `AutoRefresh` unless item properties change.

## Guides

- [ViewModels & Commands](viewmodels.md): Creating robust ViewModels and handling commands.
- [Wizards & Flows](wizards.md): Building multi-step wizards with `SlimWizard`.
- [Navigation & Sections](navigation_sections.md): Managing navigation and section-based UIs.
- [Composition & Mapping](composition.md): Best practices for View-ViewModel wiring and DI.

## Example Reference

For real-world implementations, refer to the **Angor** project:
- `CreateProjectFlowV2.cs`: Excellent example of complex Wizard building.
- `HomeViewModel.cs`: Simple section ViewModel using functional-reactive commands.


## Design-Time Data Support

To ensure previewability in the IDE and design tools, follow this pattern:

### 1. Structure

Create three files/types for your ViewModel:

1.  **Interface (`I{Name}ViewModel`)**: Defines the data and commands exposed to the View.
2.  **Runtime ViewModel (`{Name}ViewModel`)**: Implements `I{Name}ViewModel` with real logic/services.
3.  **Design Sample (`{Name}ViewModelSample`)**: Implements `I{Name}ViewModel` with static/mock data for the designer.

### 2. View Implementation

Use `x:DataType` with the **interface** and set `Design.DataContext` to the **sample**.

```xml
<UserControl x:Class="MyApp.Views.MyView"
             x:DataType="vm:IMyViewModel">

    <Design.DataContext>
        <vm:MyViewModelSample />
    </Design.DataContext>

    <- Sobreescrie el historial de origin/master con Controls bind to interface properties -->
    <TextBlock Text="{Binding Name}" />
</UserControl>
```

### 3. Sample Data Best Practices

- Use **Sub-interfaces** for complex properties if creating real instances is difficult.
  - Example: `IAccountsViewModel` has a list of `IPerson` instead of `Person`.
  - Create `PersonSample : IPerson` for design data.
- Keep samples efficient and dependency-free.
