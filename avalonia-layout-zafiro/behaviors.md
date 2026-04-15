# Interactions and Logic

To keep XAML clean and maintainable, minimize logic in views and avoid excessive use of converters.

## 🎭 Xaml.Interaction.Behaviors

Use `Interaction.Behaviors` to handle UI-related logic that doesn't belong in the ViewModel, such as focus management, animations, or specialized event handling.

```xml
<TextBox Text="{Binding Address}">
    <Interaction.Behaviors>
        <UntouchedClassBehavior />
    </Interaction.Behaviors>
</TextBox>
```

### Why use Behaviors?
- **Encapsulation**: UI logic is contained in a reusable behavior class.
- **Clean XAML**: Avoids code-behind and complex XAML triggers.
- **Testability**: Behaviors can be tested independently of the View.

## 🚫 Avoiding Converters

Converters often lead to "magical" logic hidden in XAML. Whenever possible, prefer:

1.  **ViewModel Properties**: Let the ViewModel provide the final data format (e.g., a `string` formatted for display).
2.  **MultiBinding**: Use for simple logic combinations (And/Or) directly in XAML.
3.  **Behaviors**: For more complex interactions that involve state or events.

### When to use Converters?
Only use them when the conversion is purely visual and highly reusable across different contexts (e.g., `BoolToOpacityConverter`).

## 🧩 Simplified Interactions

If you find yourself needing a complex converter or behavior, consider if the component can be simplified or if the data model can be adjusted to make the view binding more direct.

---

## 🖱️ DragDeltaBehavior — Draggable Elements

`DragDeltaBehavior` enables drag-to-move on any `Control`, binding position deltas to `Left`/`Top` properties. Used internally by `FlowEditor` for draggable nodes, but available for any custom canvas-based layout.

**Namespace:** `Zafiro.Avalonia.Behaviors`
**Source:** `src/Zafiro.Avalonia/Behaviors/DragDeltaBehavior.cs`

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `Left` | `double` | 0 | Two-way bound X position |
| `Top` | `double` | 0 | Two-way bound Y position |
| `DragButton` | `MouseButton` | `Left` | Which mouse button initiates drag |
| `DragThreshold` | `double` | 3.0 | Pixel distance before drag starts (prevents accidental drags) |
| `RoutingStrategy` | `RoutingStrategies` | `Tunnel` | Event routing strategy |

### Key Features

- **Threshold-based activation** — Drag only starts after moving beyond `DragThreshold` pixels, preventing accidental drags during clicks.
- **Pointer capture** — Captures the pointer on drag start and releases on pointer up or capture lost.
- **Coordinate system** — Uses the first visual ancestor as the coordinate reference for delta calculations.
- **Rx pipeline** — Entirely reactive: `PointerPressed → PointerMoved (until Released)` with `SelectMany` for drag sessions.

### Usage in AXAML

```xml
<ListBoxItem>
    <Interaction.Behaviors>
        <behaviors:DragDeltaBehavior Left="{Binding Left}"
                                     Top="{Binding Top}"
                                     DragThreshold="5"
                                     x:DataType="local:IHaveLocation" />
    </Interaction.Behaviors>
</ListBoxItem>
```

### Note
In `FlowEditor`, this behavior is automatically applied via the `FlowListBoxItem` ControlTheme — no manual setup required.
