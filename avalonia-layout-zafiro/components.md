# Building Generic Components

Reducing nesting and complexity is achieved by breaking down views into generic, reusable components.

## 🧊 Generic Components

Instead of building large, complex views, extract recurring patterns into small `UserControl`s.

### Example: A generic "Summary Item"
Instead of repeating a `Grid` with labels and values:

```xml
<!-- ❌ BAD: Repeated Grid -->
<Grid ColumnDefinitions="*,Auto">
   <TextBlock Text="Total:" />
   <TextBlock Grid.Column="1" Text="{Binding Total}" />
</Grid>
```

Create a generic component (or use `EdgePanel` with a Style):

```xml
<!-- ✅ GOOD: Use a specialized control or style -->
<EdgePanel StartContent="Total:" EndContent="{Binding Total}" Classes="SummaryItem" />
```

## 📉 Flattening Layouts

Avoid deep nesting. Deeply nested XAML is hard to read and can impact performance.

- **StackPanel vs Grid**: Use `StackPanel` (with `Spacing`) for simple linear layouts.
- **EdgePanel**: Great for "Label - Value" or "Icon - Text - Action" rows.
- **UniformGrid**: Use for grids where all cells are the same size.

## 🔧 Component Granularity

- **Atomical**: Small controls like custom buttons or icons.
- **Molecular**: Groups of atoms like a `HeaderedContainer` with specific content.
- **Organisms**: Higher-level sections of a page.

Aim for components that are generic enough to be reused but specific enough to simplify the parent view significantly.

---

## 🔀 FlowEditor — Node-based Visual Editor

`FlowEditor` is a `TemplatedControl` for building node/graph editors with draggable nodes and visual edge connections.

**Namespace:** `Zafiro.Avalonia.Controls.Flow`
**Source:** `src/Zafiro.Avalonia/Controls/Flow/`

### Properties

| Property | Type | Description |
|---|---|---|
| `Nodes` | `IEnumerable<IHaveLocation>` | Collection of node objects (must implement `IHaveLocation` for `Left`/`Top`) |
| `Edges` | `IEnumerable<IHaveFromTo>` | Collection of edge objects connecting nodes |
| `NodeTemplate` | `IDataTemplate` | Template for rendering each node |
| `SelectedNodes` | `AvaloniaList<object>` | Multi-select support — tracks currently selected nodes |

### Key Interfaces

- **`IHaveLocation`** — Nodes must expose `double Left` and `double Top` (two-way bindable).
- **`IHaveFromTo`** — Edges must expose `object From` and `object To` referencing node instances.
- **`IEdge<T>`** — Optional generic edge interface from `Zafiro.DataAnalysis.Graphs`.

### Architecture

- Nodes are rendered inside a `ListBox` using a `MidpointCanvas` (centered coordinate system).
- Each `ListBoxItem` gets a `DragDeltaBehavior` automatically via the `FlowListBoxItem` ControlTheme.
- Edges are drawn by a `Connectors` control that tracks node positions in the host `ListBox`.
- Multi-selection is supported via checkbox overlay on pointer hover.

### Usage

```xml
<controls:FlowEditor Nodes="{Binding Nodes}"
                     Edges="{Binding Edges}"
                     SelectedNodes="{Binding SelectedNodes}">
    <controls:FlowEditor.NodeTemplate>
        <DataTemplate DataType="local:MyNode">
            <Border Background="{DynamicResource SystemControlBackgroundAltHighBrush}"
                    BorderBrush="{DynamicResource SystemControlForegroundBaseMediumBrush}"
                    BorderThickness="1" CornerRadius="5" Padding="10"
                    MinWidth="100" MinHeight="60">
                <TextBlock Text="{Binding Name}" FontWeight="Bold" HorizontalAlignment="Center" />
            </Border>
        </DataTemplate>
    </controls:FlowEditor.NodeTemplate>
</controls:FlowEditor>
```

### Node ViewModel Pattern

```csharp
public class MyNode : ReactiveObject, IHaveLocation
{
    [Reactive] public double Left { get; set; }
    [Reactive] public double Top { get; set; }
    [Reactive] public string Name { get; set; }
}
```

### Edge Pattern

```csharp
public class MyEdge : IEdge<object>, IHaveFromTo
{
    public MyEdge(MyNode from, MyNode to) { From = from; To = to; }
    public object From { get; }
    public object To { get; }
}
```

### Sample Reference
`samples/TestApp/TestApp/Samples/Flow/`

---

## 🔧 PropertyGrid — Inspector-style Property Editor

`PropertyGrid` is a `UserControl` that automatically discovers and edits the common public properties of one or more selected objects. Ideal for inspector panels paired with FlowEditor or any multi-select scenario.

**Namespace:** `Zafiro.Avalonia.Controls.PropertyGrid`
**Source:** `src/Zafiro.Avalonia/Controls/PropertyGrid/`

### Properties

| Property | Type | Description |
|---|---|---|
| `SelectedObjects` | `IList<object>` | Objects whose common properties are displayed and editable |

### Architecture

- **`PropertyGridViewModel`** — Uses reflection to find common writable properties across all selected objects. Properties are exposed as `IPropertyItem` instances via DynamicData `SourceList`.
- **`PropertyItem`** — Implements `IPropertyItem` and `ReactiveObject`. Reading gets the shared value (or `null` if values differ). Writing propagates to all target objects.
- **`PropertyEditorSelector`** — An `IDataTemplate` that selects the correct editor per property type:
  - `System.String` → `TextBox`
  - `System.Boolean` → `CheckBox`
  - `System.Int32` / `System.Double` → `NumericUpDown`
  - `Enum` types → `ComboBox` (auto-generated)
  - Fallback → `TextBox`

### Usage

```xml
<propertyGrid:PropertyGrid SelectedObjects="{Binding SelectedItems}" />
```

### Combined FlowEditor + PropertyGrid Pattern

A common pattern is a split view with FlowEditor on the left and PropertyGrid on the right, bound to the same `SelectedNodes`:

```xml
<Grid ColumnDefinitions="*, 4, 300">
    <controls:FlowEditor Nodes="{Binding Nodes}"
                         Edges="{Binding Edges}"
                         SelectedNodes="{Binding SelectedNodes}" />
    <GridSplitter Grid.Column="1" />
    <propertyGrid:PropertyGrid Grid.Column="2"
                               SelectedObjects="{Binding SelectedNodes}" />
</Grid>
```

### Sample Reference
`samples/TestApp/TestApp/Samples/PropertyGrid/`
