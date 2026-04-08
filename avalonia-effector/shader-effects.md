# Shader Effects

Shader effects use `SKRuntimeEffect` (SkSL) to execute per-pixel GPU shaders. They are ideal for patterns, overlays, post-processing, and multi-input transitions that go beyond what `SKImageFilter` pipelines express natively.

## Required Interfaces

A shader effect factory implements **all four** factory interfaces:

| Interface | Purpose |
|---|---|
| `ISkiaEffectFactory<T>` | Return `null` from `CreateFilter` — shader effects don't use `SKImageFilter` |
| `ISkiaEffectValueFactory` | Return `null` from `CreateFilter` (value-based overload) |
| `ISkiaShaderEffectFactory<T>` | Creates `SkiaShaderEffect` from the typed effect + `SkiaShaderEffectContext` |
| `ISkiaShaderEffectValueFactory` | Creates `SkiaShaderEffect` from `object[]` values (render-thread-safe) |

The `CreateFilter` methods return `null` because shaders take a different rendering path.

## Template

```csharp
using Avalonia;
using Avalonia.Media;
using Effector;
using SkiaSharp;

[SkiaEffect(typeof(MyShaderFactory))]
public sealed class MyShaderEffect : SkiaEffectBase
{
    public static readonly StyledProperty<double> IntensityProperty =
        AvaloniaProperty.Register<MyShaderEffect, double>(nameof(Intensity), 0.5d);

    static MyShaderEffect()
    {
        AffectsRender<MyShaderEffect>(IntensityProperty);
    }

    public double Intensity
    {
        get => GetValue(IntensityProperty);
        set => SetValue(IntensityProperty, value);
    }
}

public sealed class MyShaderFactory :
    ISkiaEffectFactory<MyShaderEffect>,
    ISkiaShaderEffectFactory<MyShaderEffect>,
    ISkiaEffectValueFactory,
    ISkiaShaderEffectValueFactory
{
    private const int IntensityIndex = 0;

    private const string ShaderSource =
        """
        uniform float intensity;

        half4 main(float2 coord) {
            // SkSL shader body
            return half4(0.0, 0.0, 0.0, intensity);
        }
        """;

    // Filter interfaces return null for shader effects
    public Thickness GetPadding(MyShaderEffect effect) => default;
    public SKImageFilter? CreateFilter(MyShaderEffect effect, SkiaEffectContext context) => null;
    public Thickness GetPadding(object[] values) => default;
    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context) => null;

    // Shader interfaces
    public SkiaShaderEffect CreateShaderEffect(MyShaderEffect effect, SkiaShaderEffectContext context) =>
        CreateShaderEffect(new object[] { effect.Intensity }, context);

    public SkiaShaderEffect CreateShaderEffect(object[] values, SkiaShaderEffectContext context) =>
        SkiaRuntimeShaderBuilder.Create(
            ShaderSource,
            context,
            uniforms =>
            {
                uniforms.Add("intensity", (float)Math.Clamp((double)values[IntensityIndex], 0d, 1d));
            });
}
```

## SkiaRuntimeShaderBuilder.Create

The main factory method for building shader effects:

```csharp
public static SkiaShaderEffect Create(
    string sksl,                       // SkSL source code
    SkiaShaderEffectContext context,    // Provides bounds, opacity, content shader
    Action<SKRuntimeEffectUniforms>? configureUniforms = null,
    Action<SKRuntimeEffectChildren, SkiaShaderEffectContext>? configureChildren = null,
    string? contentChildName = null,   // If set, binds the content image as a child shader
    bool isOpaque = false,
    SKBlendMode blendMode = SKBlendMode.SrcOver,
    bool isAntialias = true,
    SKRect? destinationRect = null,    // Defaults to context.EffectBounds
    SKMatrix? localMatrix = null,
    Action<SKCanvas, SKImage, SKRect>? fallbackRenderer = null,  // CPU fallback
    Action<SKRuntimeEffectChildren, SkiaShaderEffectContext, ICollection<IDisposable>>? configureOwnedChildren = null,
    IEnumerable<IDisposable>? ownedResources = null)
```

### Key Parameters

- **`sksl`**: The SkSL shader source. Must contain `half4 main(float2 coord)`.
- **`configureUniforms`**: Set uniform values via `uniforms.Add("name", value)`.
- **`blendMode`**: How the shader composites over the content. Default `SrcOver`.
- **`fallbackRenderer`**: Optional CPU-based renderer when runtime shaders aren't available. **Always provide one for maximum compatibility.**
- **`contentChildName`**: If your shader reads the source content as a child shader, name the uniform here.
- **`configureOwnedChildren`**: Like `configureChildren` but with an `ICollection<IDisposable>` for child shaders that need lifecycle management. Use this when binding secondary shader images.
- **`ownedResources`**: Additional disposable resources (e.g., `SkiaShaderImageLease`) tied to the effect's lifetime.

### Shader Source Caching

`SkiaRuntimeShaderBuilder` caches compiled `SKRuntimeEffect` by SkSL source string, so define shader source as a `const string` field for cache hits.

### Direct Runtime Shaders

On supported SkiaSharp 3.x runtimes, direct runtime shaders are enabled by default. Set `EFFECTOR_ENABLE_DIRECT_RUNTIME_SHADERS=false` to force the fallback path when needed; fallback renderers are still used automatically when shader compilation fails.

## SkiaShaderEffectContext

Available in shader factory methods:

| Member | Description |
|---|---|
| `EffectBounds` | `SKRect` — the full bounds including padding |
| `ContentRect` | `SKRect` — the content bounds |
| `EffectiveOpacity` | Host visual opacity |
| `UsesOpacitySaveLayer` | Whether opacity is applied via save layer |
| `ApplyOpacity(color, opacity)` | Applies effective opacity to a color |
| `CreateColor(r, g, b, opacity)` | Creates opacity-aware color |
| `CreateContentShader(tileX?, tileY?)` | Creates an `SKShader` from the rendered content image (default: Clamp) |
| `BlurRadiusToSigma(radius)` | Static: converts blur radius to sigma |
| `ClampToByte(value)` | Static: clamps double to byte |

## Fallback Renderers

Always provide a `fallbackRenderer` for environments where `SKRuntimeEffect` is unavailable. The fallback receives `(SKCanvas canvas, SKImage contentImage, SKRect rect)`:

```csharp
SkiaRuntimeShaderBuilder.Create(
    ShaderSource,
    context,
    uniforms => { /* ... */ },
    fallbackRenderer: (canvas, _, rect) =>
    {
        // CPU-based approximation using SKPaint, SKCanvas draw calls
        using var paint = new SKPaint
        {
            Color = new SKColor(0, 0, 0, 60),
            IsAntialias = false,
            Style = SKPaintStyle.Fill
        };
        // Draw approximation...
    });
```

## Secondary Shader Images

Multi-input shader effects can carry extra bitmap inputs through `SkiaShaderImageHandle`, `SkiaShaderImageRegistry`, and `SkiaShaderImageLease`. The handle is a value type compatible with Effector's immutable snapshot model.

### Registration and Acquisition

```csharp
// Register an Avalonia Bitmap to get a handle
var handle = SkiaShaderImageRegistry.Register(bitmap);

// In the factory, acquire a lease
if (SkiaShaderImageRegistry.TryAcquire(handle, out var lease))
{
    // lease.Image is an SKImage — bind as child shader
    // Pass lease as ownedResource so it's disposed with the effect
}

// Release the handle when no longer needed
SkiaShaderImageRegistry.Release(handle);
```

### Binding Secondary Images as Child Shaders

Use `configureOwnedChildren` to bind secondary images and manage their lifecycle:

```csharp
public SkiaShaderEffect? CreateShaderEffect(object[] values, SkiaShaderEffectContext context)
{
    var fromHandle = (SkiaShaderImageHandle)values[FromImageIndex];
    var toHandle = (SkiaShaderImageHandle)values[ToImageIndex];

    if (!SkiaShaderImageRegistry.TryAcquire(fromHandle, out var fromLease)
        || !SkiaShaderImageRegistry.TryAcquire(toHandle, out var toLease))
    {
        fromLease?.Dispose();
        return null;
    }

    return SkiaRuntimeShaderBuilder.Create(
        ShaderSource,
        context,
        uniforms => { /* set uniforms */ },
        configureOwnedChildren: (children, _, ownedResources) =>
        {
            var fromShader = fromLease.Image.ToShader(SKShaderTileMode.Clamp, SKShaderTileMode.Clamp);
            children.Add("fromImage", fromShader);
            ownedResources.Add(fromShader);

            var toShader = toLease.Image.ToShader(SKShaderTileMode.Clamp, SKShaderTileMode.Clamp);
            children.Add("toImage", toShader);
            ownedResources.Add(toShader);
        },
        ownedResources: new IDisposable[] { fromLease, toLease });
}
```

### Compiz-Style Route Transitions

The compiz sample demonstrates full-page shader transitions using two captured page images. The effect class uses `SkiaShaderImageHandle` properties for from/to images:

```csharp
[SkiaEffect(typeof(CompizTransitionEffectFactory))]
public sealed class CompizTransitionEffect : SkiaEffectBase
{
    public static readonly StyledProperty<CompizTransitionKind> KindProperty = ...;
    public static readonly StyledProperty<SkiaShaderImageHandle> FromImageProperty = ...;
    public static readonly StyledProperty<SkiaShaderImageHandle> ToImageProperty = ...;
    public static readonly StyledProperty<double> ProgressProperty = ...;
    public static readonly StyledProperty<double> TimeProperty = ...;
    public static readonly StyledProperty<double> ClickXProperty = ...;
    public static readonly StyledProperty<double> ClickYProperty = ...;
    // ...
}
```

The SkSL shader declares two child shader uniforms:

```glsl
uniform shader fromImage;
uniform shader toImage;
uniform float width;
uniform float height;
uniform float progress;
// ...

half4 main(float2 coord) {
    half4 fromColor = fromImage.eval(coord);
    half4 toColor = toImage.eval(coord);
    // Transition logic using progress...
    return mix(fromColor, toColor, half(reveal));
}
```

## Examples

### Scanline Overlay Shader

```csharp
private const string ShaderSource =
    """
    uniform float spacing;
    uniform float strength;

    half4 main(float2 coord) {
        float span = max(spacing, 1.0);
        float local = fract(coord.y / span);
        float alpha = local >= 0.5 ? strength : 0.0;
        return half4(0.0, 0.0, 0.0, alpha);
    }
    """;

public SkiaShaderEffect CreateShaderEffect(object[] values, SkiaShaderEffectContext context) =>
    SkiaRuntimeShaderBuilder.Create(
        ShaderSource,
        context,
        uniforms =>
        {
            uniforms.Add("spacing", (float)Math.Clamp((double)values[0], 2d, 32d));
            uniforms.Add("strength", (float)Math.Clamp((double)values[1], 0d, 1d));
        },
        fallbackRenderer: (canvas, _, rect) =>
        {
            var spacing = (float)Math.Clamp((double)values[0], 2d, 32d);
            using var paint = new SKPaint { Color = new SKColor(0, 0, 0, (byte)(255 * Math.Clamp((double)values[1], 0d, 1d))), IsAntialias = false, Style = SKPaintStyle.Fill };
            var bandHeight = MathF.Max(spacing * 0.5f, 1f);
            for (var y = rect.Top + (spacing * 0.5f); y < rect.Bottom; y += spacing)
                canvas.DrawRect(new SKRect(rect.Left, y, rect.Right, MathF.Min(y + bandHeight, rect.Bottom)), paint);
        });
```

### Grid Shader with Color

```csharp
private const string ShaderSource =
    """
    uniform float cell;
    uniform float strength;
    uniform float red;
    uniform float green;
    uniform float blue;

    half4 main(float2 coord) {
        float span = max(cell, 1.0);
        float gx = fract(coord.x / span);
        float gy = fract(coord.y / span);
        float alpha = (gx < 0.06 || gy < 0.06) ? strength : 0.0;
        half premulAlpha = half(alpha);
        return half4(red * premulAlpha, green * premulAlpha, blue * premulAlpha, premulAlpha);
    }
    """;
```

### Spotlight Shader with Blend Mode

Use `blendMode: SKBlendMode.Screen` for additive-light effects:

```csharp
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
            uniforms.Add("centerX", (float)Math.Clamp((double)values[0], 0d, 1d));
            uniforms.Add("centerY", (float)Math.Clamp((double)values[1], 0d, 1d));
            uniforms.Add("radius", (float)Math.Clamp((double)values[2], 0.05d, 1d));
            uniforms.Add("strength", (float)Math.Clamp((double)values[3], 0d, 1d));
            uniforms.Add("red", color.R / 255f);
            uniforms.Add("green", color.G / 255f);
            uniforms.Add("blue", color.B / 255f);
        },
        blendMode: SKBlendMode.Screen,
        fallbackRenderer: (canvas, _, rect) =>
        {
            // Concentric ring approximation...
        });
}
```

## SkSL Quick Reference

SkSL (Skia Shading Language) is GLSL-like:

- Entry point: `half4 main(float2 coord)` — `coord` is in pixel space
- Types: `float`, `float2`, `float3`, `float4`, `half4`, `bool`
- Built-ins: `fract`, `max`, `min`, `clamp`, `sqrt`, `sin`, `cos`, `mix`, `step`, `smoothstep`
- Uniforms declared with `uniform` keyword — set from C# via `configureUniforms`
- Child shaders declared with `uniform shader childName` — bound via `configureChildren` or `configureOwnedChildren`
- Return `half4(r, g, b, a)` in premultiplied alpha
- Access child shader output: `childName.eval(coord)`

### Passing Host Bounds to Shaders

Access `context.EffectBounds.Width` and `context.EffectBounds.Height` to pass host dimensions as uniforms:

```csharp
uniforms.Add("width", context.EffectBounds.Width);
uniforms.Add("height", context.EffectBounds.Height);
```

Then normalize coordinates in SkSL:

```glsl
float nx = coord.x / max(width, 1.0);
float ny = coord.y / max(height, 1.0);
```
