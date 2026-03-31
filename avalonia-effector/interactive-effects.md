# Interactive Effects

Interactive effects respond to pointer input (hover, press, move, wheel). They derive from `SkiaInteractiveEffectBase` and combine pointer event handling with shader (or filter) rendering.

## Base Class: SkiaInteractiveEffectBase

Extends `SkiaEffectBase` and implements `ISkiaInputEffectHandler`. Override the virtual methods you need:

```csharp
public abstract class SkiaInteractiveEffectBase : SkiaEffectBase, ISkiaInputEffectHandler
{
    public virtual void OnAttached(SkiaEffectHostContext context) { }
    public virtual void OnDetached(SkiaEffectHostContext context) { }
    public virtual void OnHostBoundsChanged(SkiaEffectHostContext context) { }
    public virtual void OnPointerEntered(SkiaEffectHostContext context, PointerEventArgs e) { }
    public virtual void OnPointerExited(SkiaEffectHostContext context, PointerEventArgs e) { }
    public virtual void OnPointerMoved(SkiaEffectHostContext context, PointerEventArgs e) { }
    public virtual void OnPointerPressed(SkiaEffectHostContext context, PointerPressedEventArgs e) { }
    public virtual void OnPointerReleased(SkiaEffectHostContext context, PointerReleasedEventArgs e) { }
    public virtual void OnPointerCaptureLost(SkiaEffectHostContext context, PointerCaptureLostEventArgs e) { }
    public virtual void OnPointerWheelChanged(SkiaEffectHostContext context, PointerWheelEventArgs e) { }
}
```

## SkiaEffectHostContext

The host context passed to every interaction callback:

| Member | Type | Description |
|---|---|---|
| `Effect` | `SkiaEffectBase` | The owning effect |
| `Visual` | `Visual` | The host visual |
| `InputElement` | `InputElement?` | The host as `InputElement`, if applicable |
| `Bounds` | `Rect` | Host visual bounds |
| `Size` | `Size` | Host size |
| `InputBounds` | `Rect` | Resolved input bounds (content-aware) |
| `InputSize` | `Size` | Input bounds size |
| `HasInput` | `bool` | Whether the host is an `InputElement` |
| `GetPosition(e)` | `Point` | Raw pointer position relative to visual |
| `GetNormalizedPosition(e, clamp?)` | `Point` | Pointer position normalized to 0..1 |
| `Normalize(position, clamp?)` | `Point` | Normalize any point to 0..1 |
| `CapturePointer(e)` | `void` | Capture pointer on the host element |
| `ReleasePointerCapture(e)` | `void` | Release pointer capture |
| `Invalidate()` | `void` | Request effect re-render |

## Property Strategy for Interactive Effects

Use `DirectProperty<T>` for rapidly changing state (pointer position, hover/press flags) to avoid boxing and notification overhead:

```csharp
public static readonly DirectProperty<MyEffect, double> PointerXProperty =
    AvaloniaProperty.RegisterDirect<MyEffect, double>(
        nameof(PointerX),
        effect => effect.PointerX,
        (effect, value) => effect.PointerX = value);

private double _pointerX = 0.5d;

public double PointerX
{
    get => _pointerX;
    set => SetAndRaise(PointerXProperty, ref _pointerX, value);
}
```

Use `StyledProperty<T>` for user-configurable parameters that change infrequently (radius, color, strength).

**Both** types must be included in `AffectsRender<T>(...)`.

## Template: Pointer-Driven Shader Effect

```csharp
using System;
using Avalonia;
using Avalonia.Input;
using Avalonia.Media;
using Effector;
using SkiaSharp;

[SkiaEffect(typeof(PointerHighlightFactory))]
public sealed class PointerHighlightEffect : SkiaInteractiveEffectBase
{
    // Rapidly changing — use DirectProperty
    public static readonly DirectProperty<PointerHighlightEffect, double> PointerXProperty =
        AvaloniaProperty.RegisterDirect<PointerHighlightEffect, double>(
            nameof(PointerX), e => e.PointerX, (e, v) => e.PointerX = v);

    public static readonly DirectProperty<PointerHighlightEffect, double> PointerYProperty =
        AvaloniaProperty.RegisterDirect<PointerHighlightEffect, double>(
            nameof(PointerY), e => e.PointerY, (e, v) => e.PointerY = v);

    public static readonly DirectProperty<PointerHighlightEffect, bool> IsPointerOverProperty =
        AvaloniaProperty.RegisterDirect<PointerHighlightEffect, bool>(
            nameof(IsPointerOver), e => e.IsPointerOver, (e, v) => e.IsPointerOver = v);

    // User-configurable — use StyledProperty
    public static readonly StyledProperty<double> RadiusProperty =
        AvaloniaProperty.Register<PointerHighlightEffect, double>(nameof(Radius), 0.25d);

    public static readonly StyledProperty<Color> ColorProperty =
        AvaloniaProperty.Register<PointerHighlightEffect, Color>(nameof(Color), Colors.White);

    private double _pointerX = 0.5d;
    private double _pointerY = 0.5d;
    private bool _isPointerOver;

    static PointerHighlightEffect()
    {
        AffectsRender<PointerHighlightEffect>(
            PointerXProperty, PointerYProperty, IsPointerOverProperty,
            RadiusProperty, ColorProperty);
    }

    public double PointerX
    {
        get => _pointerX;
        set => SetAndRaise(PointerXProperty, ref _pointerX, value);
    }

    public double PointerY
    {
        get => _pointerY;
        set => SetAndRaise(PointerYProperty, ref _pointerY, value);
    }

    public bool IsPointerOver
    {
        get => _isPointerOver;
        set => SetAndRaise(IsPointerOverProperty, ref _isPointerOver, value);
    }

    public double Radius
    {
        get => GetValue(RadiusProperty);
        set => SetValue(RadiusProperty, value);
    }

    public Color Color
    {
        get => GetValue(ColorProperty);
        set => SetValue(ColorProperty, value);
    }

    // Lifecycle
    public override void OnAttached(SkiaEffectHostContext context)
    {
        PointerX = 0.5d;
        PointerY = 0.5d;
    }

    // Pointer events
    public override void OnPointerEntered(SkiaEffectHostContext context, PointerEventArgs e)
    {
        UpdatePointer(context, e);
        IsPointerOver = true;
    }

    public override void OnPointerExited(SkiaEffectHostContext context, PointerEventArgs e)
    {
        IsPointerOver = false;
    }

    public override void OnPointerMoved(SkiaEffectHostContext context, PointerEventArgs e)
    {
        UpdatePointer(context, e);
    }

    private void UpdatePointer(SkiaEffectHostContext context, PointerEventArgs e)
    {
        var point = context.GetNormalizedPosition(e);
        PointerX = point.X;
        PointerY = point.Y;
    }
}

public sealed class PointerHighlightFactory :
    ISkiaEffectFactory<PointerHighlightEffect>,
    ISkiaShaderEffectFactory<PointerHighlightEffect>,
    ISkiaEffectValueFactory,
    ISkiaShaderEffectValueFactory
{
    private const int PointerXIndex = 0;
    private const int PointerYIndex = 1;
    private const int IsPointerOverIndex = 2;
    private const int RadiusIndex = 3;
    private const int ColorIndex = 4;

    private const string ShaderSource =
        """
        uniform float width;
        uniform float height;
        uniform float pointerX;
        uniform float pointerY;
        uniform float radius;
        uniform float hover;
        uniform float red;
        uniform float green;
        uniform float blue;

        half4 main(float2 coord) {
            float nx = coord.x / max(width, 1.0);
            float ny = coord.y / max(height, 1.0);
            float dx = nx - pointerX;
            float dy = ny - pointerY;
            float dist = sqrt(dx * dx + dy * dy);
            float fade = 1.0 - smoothstep(0.0, max(radius, 0.001), dist);
            float alpha = fade * hover * 0.3;
            return half4(red * alpha, green * alpha, blue * alpha, alpha);
        }
        """;

    public Thickness GetPadding(PointerHighlightEffect effect) => default;
    public SKImageFilter? CreateFilter(PointerHighlightEffect effect, SkiaEffectContext context) => null;
    public Thickness GetPadding(object[] values) => default;
    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context) => null;

    public SkiaShaderEffect CreateShaderEffect(PointerHighlightEffect effect, SkiaShaderEffectContext context) =>
        CreateShaderEffect(new object[]
        {
            effect.PointerX, effect.PointerY, effect.IsPointerOver,
            effect.Radius, effect.Color
        }, context);

    public SkiaShaderEffect CreateShaderEffect(object[] values, SkiaShaderEffectContext context)
    {
        var color = (Color)values[ColorIndex];
        return SkiaRuntimeShaderBuilder.Create(
            ShaderSource,
            context,
            uniforms =>
            {
                uniforms.Add("width", context.EffectBounds.Width);
                uniforms.Add("height", context.EffectBounds.Height);
                uniforms.Add("pointerX", (float)(double)values[PointerXIndex]);
                uniforms.Add("pointerY", (float)(double)values[PointerYIndex]);
                uniforms.Add("radius", (float)Math.Clamp((double)values[RadiusIndex], 0.05d, 1d));
                uniforms.Add("hover", (bool)values[IsPointerOverIndex] ? 1f : 0f);
                uniforms.Add("red", color.R / 255f);
                uniforms.Add("green", color.G / 255f);
                uniforms.Add("blue", color.B / 255f);
            },
            blendMode: SKBlendMode.Screen);
    }
}
```

## Pointer Capture Pattern

For effects that track drag (press → move → release), capture the pointer:

```csharp
public override void OnPointerPressed(SkiaEffectHostContext context, PointerPressedEventArgs e)
{
    UpdatePointer(context, e);
    IsPressed = true;
    context.CapturePointer(e);
}

public override void OnPointerReleased(SkiaEffectHostContext context, PointerReleasedEventArgs e)
{
    UpdatePointer(context, e);
    IsPressed = false;
    context.ReleasePointerCapture(e);
}

public override void OnPointerCaptureLost(SkiaEffectHostContext context, PointerCaptureLostEventArgs e)
{
    IsPressed = false;
}
```

## Timer-Based Animation in Interactive Effects

For effects that animate continuously (e.g., water ripple), use `DispatcherTimer`:

```csharp
private DispatcherTimer? _timer;
private double _time;

public override void OnAttached(SkiaEffectHostContext context)
{
    _time = 0d;
    _timer = new DispatcherTimer(
        TimeSpan.FromMilliseconds(16),
        DispatcherPriority.Render,
        (_, _) =>
        {
            _time += 0.016d;
            Time = _time;
        });
    _timer.Start();
}

public override void OnDetached(SkiaEffectHostContext context)
{
    _timer?.Stop();
    _timer = null;
}
```

## XAML Usage

Interactive effects are applied the same way as any other effect:

```xml
<Border Width="300" Height="200" Background="#1F2937" CornerRadius="8">
  <Border.Effect>
    <local:PointerHighlightEffect Radius="0.3" Color="#FFD26B" />
  </Border.Effect>
  <TextBlock Text="Hover me!" HorizontalAlignment="Center" VerticalAlignment="Center" />
</Border>
```

Effector automatically attaches the input handler to the host visual — no extra event wiring is needed.

## ISkiaInputEffectHandler (Low-Level)

If you need input handling without inheriting `SkiaInteractiveEffectBase`, implement `ISkiaInputEffectHandler` directly on any `SkiaEffectBase`-derived type:

```csharp
public interface ISkiaInputEffectHandler
{
    void OnAttached(SkiaEffectHostContext context);
    void OnDetached(SkiaEffectHostContext context);
    void OnHostBoundsChanged(SkiaEffectHostContext context);
    void OnPointerEntered(SkiaEffectHostContext context, PointerEventArgs e);
    void OnPointerExited(SkiaEffectHostContext context, PointerEventArgs e);
    void OnPointerMoved(SkiaEffectHostContext context, PointerEventArgs e);
    void OnPointerPressed(SkiaEffectHostContext context, PointerPressedEventArgs e);
    void OnPointerReleased(SkiaEffectHostContext context, PointerReleasedEventArgs e);
    void OnPointerCaptureLost(SkiaEffectHostContext context, PointerCaptureLostEventArgs e);
    void OnPointerWheelChanged(SkiaEffectHostContext context, PointerWheelEventArgs e);
}
```
