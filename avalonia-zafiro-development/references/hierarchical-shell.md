# Hierarchical Shell Sections

Use this reference when an Avalonia/Zafiro app needs more than root-level sections, or when changing `ShellView`, `[Section]`, section registration, or local Zafiro iteration.

## Model

- `IShell` remains the baseline contract for section selection. Use `IHierarchicalShell` when the UI needs the section tree.
- `IHierarchicalShell` exposes `RootLevel`, `ChildLevels`, and `SelectedPath`. `ShellView` is typed to this contract.
- `ISection` remains the base section contract. Hierarchical sections implement `IHierarchicalSection` and expose `ParentId`.
- `ParentId` points to another section's `Id`. Prefer explicit stable ids in `[Section("id", ...)]`; relying on generated ids makes parent strings fragile.
- Sections without `ParentId` are root sections. Child levels are derived automatically from the selected path.
- Each section keeps its scoped `INavigator`; switching sections preserves that section's internal navigation state.

## Attribute-first Definition

Prefer attributes for app sections. This keeps consumer ergonomics high and lets the source generator/registering helpers build the shell automatically.

```csharp
using Zafiro.UI.Shell.Utils;

[Section("workspace", "mdi-view-dashboard", 0, FriendlyName = "Workspace")]
public sealed class WorkspaceViewModel
{
}

[Section("reports", "mdi-chart-box-outline", 1, FriendlyName = "Reports")]
public sealed class ReportsViewModel
{
}

[Section("customers", "mdi-account-group", 0, FriendlyName = "Customers", ParentId = "workspace")]
public sealed class CustomersViewModel
{
}

[Section("active-customers", "mdi-account-check", 0, FriendlyName = "Active", ParentId = "customers")]
public sealed class ActiveCustomersViewModel
{
}
```

`[SectionGroup]` still groups sections for presentation; it does not define parent/child relationships. Use `ParentId` for hierarchy.

## Shell Wiring

Resolve `IHierarchicalShell` for `ShellView`.

```csharp
services.AddZafiroShell(logger: logger);
services.AddAllSectionsFromAttributes(logger);

var provider = services.BuildServiceProvider();
var shell = provider.GetRequiredService<IHierarchicalShell>();

this.Connect(() => new ShellView(), _ => shell, () => new Window());
```

For nested demos or isolated samples, use `AddSectionsFromAttributes(assembly, predicate)` to register only the sample section tree, then expose an `IHierarchicalShell` property from the sample ViewModel.

## UI Behavior

- `ShellView` renders `RootLevel` as the primary section strip and represents only the first child level from `ChildLevels` by default. On wide layouts, the active second level is nested under the selected root item in the sidebar; on compact layouts, root sections stay in the bottom bar and the active second level appears as tabs above the content.
- Do not hand-roll child `TabControl` nesting for the standard shell. Customize the shell view only when the product needs a different visual layout.
- Deeper levels remain part of the shell model, but the default UI intentionally focuses on two represented levels. If a product needs a third visible level, revisit the shell layout instead of assuming nested controls should keep scaling.

## Builder API

When attributes are not appropriate, use the full `SectionsBuilder.AddSection` overload and pass `parentId` explicitly. Keep the six-argument overload intact for binary compatibility.

```csharp
services.AddSections(builder =>
{
    builder.AddSection<WorkspaceViewModel>("workspace", "Workspace", new Icon { Source = "mdi-view-dashboard" });
    builder.AddSection<CustomersViewModel>("customers", "Customers", new Icon { Source = "mdi-account-group" }, null, 0, null, "workspace");
});
```

## Local Zafiro Source Workflow

Do not add `Zafiro` as a submodule of `Zafiro.Avalonia`. The repos publish independently and have independent versioning.

- CI and package builds must use NuGet by default: `UseLocalZafiroReferences=false`.
- For local cross-repo iteration, clone `Zafiro` next to `Zafiro.Avalonia` or set `ZafiroSourceRoot`.
- Enable local project references from an ignored `Directory.Build.local.props`, based on `Directory.Build.local.props.example`.

```xml
<Project>
  <PropertyGroup>
    <UseLocalZafiroReferences>true</UseLocalZafiroReferences>
    <ZafiroSourceRoot>../Zafiro</ZafiroSourceRoot>
  </PropertyGroup>
</Project>
```

If `Zafiro.Avalonia` needs new `Zafiro.UI` APIs, merge/publish `Zafiro` first, then update `Directory.Packages.props` in `Zafiro.Avalonia` to the published package version. Verify package mode as well as local source mode before pushing release-facing changes.

Useful checks:

```bash
dotnet build Zafiro.Avalonia.slnx -c Debug /p:UseLocalZafiroReferences=true
dotnet build Zafiro.Avalonia.slnx -c Release /p:UseLocalZafiroReferences=false
```

Canonical examples:

- `samples/MinimalShell/App.axaml.cs`
- `samples/TestApp/TestApp/Samples/Shell/Hierarchy/`
- `test/Zafiro.Avalonia.Tests/HierarchicalShellSampleTests.cs`
