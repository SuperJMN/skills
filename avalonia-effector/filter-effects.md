# Filter Effects

Filter effects produce `SKImageFilter` instances that Avalonia applies during rendering. They are the simplest Effector category and suitable for color corrections, blur, glow, pixelation, convolution, and composition.

## Required Interfaces

| Interface | Purpose |
|---|---|
| `ISkiaEffectFactory<T>` | Creates `SKImageFilter?` from the typed effect + `SkiaEffectContext` |
| `ISkiaEffectValueFactory` | Creates `SKImageFilter?` from `object[]` values (render-thread-safe immutable snapshot) |

## Template

```csharp
using Avalonia;
using Avalonia.Media;
using Effector;
using SkiaSharp;

[SkiaEffect(typeof(MyEffectFactory))]
public sealed class MyEffect : SkiaEffectBase
{
    public static readonly StyledProperty<double> AmountProperty =
        AvaloniaProperty.Register<MyEffect, double>(nameof(Amount), 1d);

    static MyEffect()
    {
        AffectsRender<MyEffect>(AmountProperty);
    }

    public double Amount
    {
        get => GetValue(AmountProperty);
        set => SetValue(AmountProperty, value);
    }
}

public sealed class MyEffectFactory :
    ISkiaEffectFactory<MyEffect>,
    ISkiaEffectValueFactory
{
    private const int AmountIndex = 0;

    public Thickness GetPadding(MyEffect effect) => default;
    public Thickness GetPadding(object[] values) => default;

    public SKImageFilter? CreateFilter(MyEffect effect, SkiaEffectContext context) =>
        CreateFilter(new object[] { effect.Amount }, context);

    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context)
    {
        var amount = (float)Math.Clamp((double)values[AmountIndex], 0d, 1d);
        // Build and return an SKImageFilter
        return SkiaFilterBuilder.ColorFilter(
            SKColorFilter.CreateColorMatrix(ColorMatrixBuilder.CreateGrayscale(amount)));
    }
}
```

## SkiaFilterBuilder Methods

| Method | Description |
|---|---|
| `ColorFilter(SKColorFilter, input?)` | Applies a color matrix or blend filter |
| `Blur(radius, input?)` | Gaussian blur (radius → sigma via `BlurRadiusToSigma`) |
| `Convolution(w, h, kernel, gain, bias, convolveAlpha, input?)` | Matrix convolution (sharpen, edge detect) |
| `Pixelate(cellSize)` | Downscale → upscale pixelation |
| `Merge(filters...)` | Composites multiple filters |
| `Compose(outer, inner)` | Chains two filters |
| `Offset(x, y, input?)` | Translates filter output |
| `Matrix(matrix, sampling?, input?)` | Arbitrary matrix transform |
| `Dilate(rx, ry, input?)` | Morphological dilation |
| `Erode(rx, ry, input?)` | Morphological erosion |

## ColorMatrixBuilder

A helper for 5×4 color matrices (`float[20]`):

| Static Method | Description |
|---|---|
| `CreateIdentity()` | No-op matrix |
| `CreateGrayscale(amount)` | Desaturation (0 = original, 1 = full grayscale) |
| `CreateSepia(amount)` | Sepia tone |
| `CreateSaturation(saturation)` | Adjust saturation (0 = gray, 1 = normal, >1 = vivid) |
| `CreateBrightnessContrast(brightness, contrast)` | Combined brightness/contrast |
| `CreateInvert(amount)` | Color inversion |
| `Blend(from, to, amount)` | Interpolates two matrices |

Also available as a fluent builder:

```csharp
var filter = new ColorMatrixBuilder()
    .SetSaturation(1.2f)
    .ToColorFilter();
```

## Opacity Handling

`SkiaEffectContext` carries `EffectiveOpacity` and `UsesOpacitySaveLayer`. Use `context.ApplyOpacity(color)` or `context.CreateColor(r, g, b, opacity)` to correctly handle host opacity.

## Padding (Effects That Grow Bounds)

If your effect expands beyond the visual's bounds (glow, shadow, blur), return non-default padding:

```csharp
public Thickness GetPadding(GlowEffect effect) =>
    new(Math.Ceiling(Math.Max(0d, effect.BlurRadius)) + 1d);

public Thickness GetPadding(object[] values) =>
    new(Math.Ceiling(Math.Max(0d, (double)values[BlurRadiusIndex])) + 1d);
```

## Examples

### Grayscale

```csharp
[SkiaEffect(typeof(GrayscaleEffectFactory))]
public sealed class GrayscaleEffect : SkiaEffectBase
{
    public static readonly StyledProperty<double> AmountProperty =
        AvaloniaProperty.Register<GrayscaleEffect, double>(nameof(Amount), 1d);

    static GrayscaleEffect() { AffectsRender<GrayscaleEffect>(AmountProperty); }

    public double Amount { get => GetValue(AmountProperty); set => SetValue(AmountProperty, value); }
}

public sealed class GrayscaleEffectFactory : ISkiaEffectFactory<GrayscaleEffect>, ISkiaEffectValueFactory
{
    public Thickness GetPadding(GrayscaleEffect effect) => default;
    public Thickness GetPadding(object[] values) => default;

    public SKImageFilter? CreateFilter(GrayscaleEffect effect, SkiaEffectContext context) =>
        CreateFilter(new object[] { effect.Amount }, context);

    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context) =>
        SkiaFilterBuilder.ColorFilter(
            SKColorFilter.CreateColorMatrix(
                ColorMatrixBuilder.CreateGrayscale((float)Math.Clamp((double)values[0], 0d, 1d))));
}
```

### Glow (Multi-Filter Composition)

```csharp
[SkiaEffect(typeof(GlowEffectFactory))]
public sealed class GlowEffect : SkiaEffectBase
{
    public static readonly StyledProperty<Color> ColorProperty =
        AvaloniaProperty.Register<GlowEffect, Color>(nameof(Color), Colors.Gold);
    public static readonly StyledProperty<double> BlurRadiusProperty =
        AvaloniaProperty.Register<GlowEffect, double>(nameof(BlurRadius), 12d);
    public static readonly StyledProperty<double> IntensityProperty =
        AvaloniaProperty.Register<GlowEffect, double>(nameof(Intensity), 0.9d);

    static GlowEffect() { AffectsRender<GlowEffect>(ColorProperty, BlurRadiusProperty, IntensityProperty); }

    public Color Color { get => GetValue(ColorProperty); set => SetValue(ColorProperty, value); }
    public double BlurRadius { get => GetValue(BlurRadiusProperty); set => SetValue(BlurRadiusProperty, value); }
    public double Intensity { get => GetValue(IntensityProperty); set => SetValue(IntensityProperty, value); }
}

public sealed class GlowEffectFactory : ISkiaEffectFactory<GlowEffect>, ISkiaEffectValueFactory
{
    public Thickness GetPadding(GlowEffect effect) =>
        new(Math.Ceiling(Math.Max(0d, effect.BlurRadius)) + 1d);
    public Thickness GetPadding(object[] values) =>
        new(Math.Ceiling(Math.Max(0d, (double)values[1])) + 1d);

    public SKImageFilter? CreateFilter(GlowEffect effect, SkiaEffectContext context) =>
        CreateFilter(new object[] { effect.Color, effect.BlurRadius, effect.Intensity }, context);

    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context)
    {
        var glowColor = context.ApplyOpacity(
            new SKColor(((Color)values[0]).R, ((Color)values[0]).G, ((Color)values[0]).B, ((Color)values[0]).A),
            Math.Clamp((double)values[2], 0d, 1d));
        var glow = SkiaFilterBuilder.ColorFilter(SKColorFilter.CreateBlendMode(glowColor, SKBlendMode.SrcIn));
        var blurredGlow = SkiaFilterBuilder.Blur((double)values[1], glow);
        var identity = SkiaFilterBuilder.ColorFilter(
            SKColorFilter.CreateColorMatrix(ColorMatrixBuilder.CreateIdentity()))!;
        return SkiaFilterBuilder.Merge(blurredGlow, identity);
    }
}
```

### Sharpen (Convolution)

```csharp
public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context)
{
    var strength = (float)Math.Clamp((double)values[0], 0d, 2d);
    var center = 1f + (4f * strength);
    var edge = -strength;
    var kernel = new[] { 0f, edge, 0f, edge, center, edge, 0f, edge, 0f };
    return SkiaFilterBuilder.Convolution(3, 3, kernel);
}
```

### Edge Detect (Grayscale + Convolution + Overlay)

```csharp
public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context)
{
    var strength = (float)Math.Clamp((double)values[0], 0d, 2d);
    var kernel = new[]
    {
        -strength, -strength, -strength,
        -strength, 8f * strength, -strength,
        -strength, -strength, -strength
    };

    var grayscale = SkiaFilterBuilder.ColorFilter(
        SKColorFilter.CreateColorMatrix(ColorMatrixBuilder.CreateGrayscale(1f)));
    var edges = SkiaFilterBuilder.Convolution(3, 3, kernel,
        gain: 1f, bias: 0f, convolveAlpha: false, input: grayscale);

    // Convert edges into black alpha overlay
    var edgeOverlay = SkiaFilterBuilder.ColorFilter(
        SKColorFilter.CreateColorMatrix(new[]
        {
            0f, 0f, 0f, 0f, 0f,
            0f, 0f, 0f, 0f, 0f,
            0f, 0f, 0f, 0f, 0f,
            1f, 0f, 0f, 0f, 0f
        }),
        edges);

    var identity = SkiaFilterBuilder.ColorFilter(
        SKColorFilter.CreateColorMatrix(ColorMatrixBuilder.CreateIdentity()))!;
    return SkiaFilterBuilder.Merge(identity, edgeOverlay);
}
```
