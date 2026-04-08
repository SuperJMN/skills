---
name: avalonia-effector
description: Creating custom Skia-backed visual effects for Avalonia UI using the Effector library. Filter effects, runtime shaders, interactive pointer-driven effects, and MSBuild integration.
---

# Avalonia Effector — Custom Visual Effects

Effector brings extensible Skia-backed custom effects to **Avalonia 12.0.0** while preserving the public `Visual.Effect : IEffect?` contract. It uses compile-time effect weaving and app-local Avalonia assembly patching — no runtime detours.

**Repository:** <https://github.com/wieslawsoltes/Effector>
**NuGet:** `Effector` (v0.5.0)
**SkiaSharp:** `3.119.3-preview.1.1`

## When to Use This Skill

- User wants to add visual effects (blur, glow, tint, pixelate, etc.) to Avalonia controls
- User needs runtime SkSL shader effects in Avalonia
- User wants pointer-driven interactive effects (spotlight, ripple, reactive grid)
- User needs multi-input shader effects with secondary images (route transitions, blend effects)
- User is building a custom `IEffect` for Avalonia's `Visual.Effect` property
- User asks about `SkiaEffectBase`, `SkiaShaderEffect`, or Effector types

## Architecture Overview

Effector has three layers:

1. **Authoring API** (`Effector.dll`) — public types you use to define effects
2. **Assembly weaving** — after `CoreCompile`, Effector scans metadata and rewrites effect types with Mono.Cecil, injecting immutable helpers and render-safe snapshot accessors
3. **Avalonia patching** — patches local copies of `Avalonia.Base.dll` and `Avalonia.Skia.dll` so Avalonia calls `EffectorRuntime` for immutable conversion, padding, parsing, animation, and Skia filter/shader entry points

## Effect Categories

There are three kinds of effects, each with its own guide:

| Category | Base Class | Factory Interfaces | Guide |
|---|---|---|---|
| **Filter effects** | `SkiaEffectBase` | `ISkiaEffectFactory<T>` + `ISkiaEffectValueFactory` | [filter-effects.md](filter-effects.md) |
| **Shader effects** | `SkiaEffectBase` | Above + `ISkiaShaderEffectFactory<T>` + `ISkiaShaderEffectValueFactory` | [shader-effects.md](shader-effects.md) |
| **Interactive effects** | `SkiaInteractiveEffectBase` | Same as shader + `ISkiaInputEffectHandler` | [interactive-effects.md](interactive-effects.md) |

## Quick Start

### Install

```bash
dotnet add package Effector
```

### Minimal Filter Effect (Tint)

```csharp
using Avalonia;
using Avalonia.Media;
using Effector;
using SkiaSharp;

// 1. Mutable effect class — lives on the UI thread
[SkiaEffect(typeof(TintEffectFactory))]
public sealed class TintEffect : SkiaEffectBase
{
    public static readonly StyledProperty<Color> ColorProperty =
        AvaloniaProperty.Register<TintEffect, Color>(nameof(Color), Colors.DeepSkyBlue);

    public static readonly StyledProperty<double> StrengthProperty =
        AvaloniaProperty.Register<TintEffect, double>(nameof(Strength), 0.55d);

    static TintEffect()
    {
        AffectsRender<TintEffect>(ColorProperty, StrengthProperty);
    }

    public Color Color
    {
        get => GetValue(ColorProperty);
        set => SetValue(ColorProperty, value);
    }

    public double Strength
    {
        get => GetValue(StrengthProperty);
        set => SetValue(StrengthProperty, value);
    }
}

// 2. Factory — creates SKImageFilter from immutable values on the render thread
public sealed class TintEffectFactory :
    ISkiaEffectFactory<TintEffect>,
    ISkiaEffectValueFactory
{
    private const int ColorIndex = 0;
    private const int StrengthIndex = 1;

    public Thickness GetPadding(TintEffect effect) => default;
    public Thickness GetPadding(object[] values) => default;

    public SKImageFilter? CreateFilter(TintEffect effect, SkiaEffectContext context) =>
        CreateFilter(new object[] { effect.Color, effect.Strength }, context);

    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context)
    {
        var color = (Color)values[ColorIndex];
        var strength = (double)values[StrengthIndex];
        var tintMatrix = new[]
        {
            color.R / 255f, 0f, 0f, 0f, 0f,
            0f, color.G / 255f, 0f, 0f, 0f,
            0f, 0f, color.B / 255f, 0f, 0f,
            0f, 0f, 0f, 1f, 0f
        };
        var matrix = ColorMatrixBuilder.Blend(
            ColorMatrixBuilder.CreateIdentity(), tintMatrix,
            (float)Math.Clamp(strength, 0d, 1d));
        return SkiaFilterBuilder.ColorFilter(SKColorFilter.CreateColorMatrix(matrix));
    }
}
```

### Apply in XAML

```xml
<Border Width="240" Height="120" Background="#1F2937">
  <Border.Effect>
    <local:TintEffect Color="#00C2FF" Strength="0.35" />
  </Border.Effect>
</Border>
```

### Apply in Code

```csharp
border.Effect = new TintEffect { Color = Color.Parse("#00C2FF"), Strength = 0.35d };
```

## The Authoring Pattern (CRITICAL)

Every Effector effect follows the same two-part pattern:

### Part 1 — Effect Class (UI Thread)

- Derive from `SkiaEffectBase` (or `SkiaInteractiveEffectBase` for pointer input)
- Annotate with `[SkiaEffect(typeof(YourFactory))]`
- Declare `StyledProperty<T>` for each parameter (use `DirectProperty<T>` for frequently changing values like pointer position)
- Call `AffectsRender<T>(...)` in the static constructor for all properties that should trigger re-render
- The class is `sealed`

### Part 2 — Factory Class (Render Thread)

- Implement `ISkiaEffectFactory<T>` — creates `SKImageFilter?` from the typed effect
- Implement `ISkiaEffectValueFactory` — creates `SKImageFilter?` from `object[]` values (the immutable snapshot)
- For shader effects, also implement `ISkiaShaderEffectFactory<T>` and `ISkiaShaderEffectValueFactory`
- The typed method delegates to the `object[]` method
- Use `const int` index fields for readability

### Why Both Interfaces?

Effector weaves immutable snapshot types at build time. The `object[]`-based "value factory" interfaces are called from the render thread using those snapshots — **never access `AvaloniaObject` from the render thread**. The typed interfaces exist for convenience and typically just forward to the value-based overload.

## Key API Types

See [api-reference.md](api-reference.md) for the full reference. Summary:

| Type | Role |
|---|---|
| `SkiaEffectBase` | Base class for non-interactive effects |
| `SkiaInteractiveEffectBase` | Base class with pointer input hooks |
| `SkiaEffectAttribute` | Links an effect class to its factory (`Name` property for string parsing) |
| `SkiaEffectContext` | Passed to filter factories — carries `EffectiveOpacity`, `UsesOpacitySaveLayer`, color helpers |
| `SkiaShaderEffectContext` | Passed to shader factories — adds `ContentRect`, `EffectBounds`, `CreateContentShader()` |
| `SkiaEffectHostContext` | Passed to interactive handlers — carries `Visual`, `Bounds`, normalized position helpers, pointer capture |
| `SkiaFilterBuilder` | Static helper: `Blur`, `ColorFilter`, `Convolution`, `Pixelate`, `Merge`, `Compose`, `Offset`, `Dilate`, `Erode` |
| `ColorMatrixBuilder` | Static + fluent builder: `CreateIdentity`, `CreateGrayscale`, `CreateSepia`, `CreateSaturation`, `CreateBrightnessContrast`, `CreateInvert`, `Blend` |
| `SkiaRuntimeShaderBuilder` | Creates `SkiaShaderEffect` from SkSL source with uniform configuration, owned resources, and optional fallback renderer |
| `SkiaShaderEffect` | Encapsulates compiled shader + blend mode + owned resources + fallback. Disposable. |
| `SkiaShaderImageHandle` | Value-type handle for secondary shader images (immutable-snapshot compatible) |
| `SkiaShaderImageRegistry` | Registers and acquires `SKImage` instances for multi-input shaders |
| `SkiaShaderImageLease` | RAII lease keeping a registered `SKImage` alive. Disposable. |

## Secondary Shader Images

Multi-input shader effects can carry extra bitmap inputs through the `SkiaShaderImageHandle` / `SkiaShaderImageRegistry` / `SkiaShaderImageLease` API. The handle is a value type compatible with Effector's immutable snapshot model, while a lease keeps the underlying `SKImage` alive until the `SkiaShaderEffect` is disposed.

### Usage Pattern

```csharp
// 1. Effect declares a handle property
public static readonly StyledProperty<SkiaShaderImageHandle> FromImageProperty =
    AvaloniaProperty.Register<MyTransitionEffect, SkiaShaderImageHandle>(nameof(FromImage));

// 2. Register an Avalonia Bitmap to get a handle
using var bitmap = CapturePage(...);
var fromHandle = SkiaShaderImageRegistry.Register(bitmap);

// 3. In the factory, acquire a lease and bind as child shader
if (SkiaShaderImageRegistry.TryAcquire(effect.FromImage, out var fromLease))
{
    return SkiaRuntimeShaderBuilder.Create(
        sksl,
        context,
        configureOwnedChildren: (children, _, ownedResources) =>
        {
            var fromShader = fromLease.Image.ToShader(SKShaderTileMode.Clamp, SKShaderTileMode.Clamp);
            children.Add("fromImage", fromShader);
            ownedResources.Add(fromShader);
        },
        ownedResources: new IDisposable[] { fromLease });
}

// 4. Release the handle when no longer needed
SkiaShaderImageRegistry.Release(fromHandle);
```

The compiz sample uses this path to feed current-page and next-page captures into a single shader for route transitions.

## Parsing and Animation

Custom effects participate in Avalonia's effect pipeline:

```csharp
var effect = Effect.Parse("tint(color=#0F9D8E, strength=0.55)");
```

Effects support `EffectTransition`, keyframe `Animation`, and immutable equality/snapshot comparison.

## MSBuild Configuration

The NuGet ships `buildTransitive` targets. Supported switches:

```xml
<PropertyGroup>
  <EffectorEnabled>true</EffectorEnabled>
  <EffectorStrict>true</EffectorStrict>
  <EffectorVerbose>false</EffectorVerbose>
  <EffectorSupportedAvaloniaVersion>12.0.0</EffectorSupportedAvaloniaVersion>
</PropertyGroup>
```

### Build Constraints

- **Use `-m:1`** (sequential build) for clean solution builds — the self-weaver can race under parallel graph builds
- Avalonia version is pinned to **12.0.0**
- Only **Avalonia.Skia** renderer is supported

### Android Patching

Effector now natively patches Android ABI asset copies after `_PrepareAssemblies`, so packaged APKs use the patched Avalonia binaries automatically. No manual workaround target is required.

### NativeAOT

Effector supports `PublishAot=true`. The MSBuild targets patch ILC input assemblies before native compilation:

```bash
dotnet publish -c Release -r osx-arm64 -p:PublishAot=true -p:StripSymbols=false
```

### Direct Runtime Shaders

On supported SkiaSharp 3.x runtimes, direct runtime shaders are enabled by default. Set `EFFECTOR_ENABLE_DIRECT_RUNTIME_SHADERS=false` to force the fallback path when needed; fallback renderers are still used automatically when shader compilation fails or the active draw path cannot execute runtime shaders.

## Common Patterns

### Effects That Expand Visual Bounds (Glow, Shadow)

Override `GetPadding` to return a non-zero `Thickness`:

```csharp
public Thickness GetPadding(GlowEffect effect) =>
    new(Math.Ceiling(Math.Max(0d, effect.BlurRadius)) + 1d);
```

### Composing Multiple Filters

Use `SkiaFilterBuilder.Merge(...)` or `SkiaFilterBuilder.Compose(outer, inner)`:

```csharp
var glow = SkiaFilterBuilder.ColorFilter(SKColorFilter.CreateBlendMode(glowColor, SKBlendMode.SrcIn));
var blurredGlow = SkiaFilterBuilder.Blur(blurRadius, glow);
return SkiaFilterBuilder.Merge(blurredGlow, identityFilter);
```

### Convolution Kernels (Sharpen, Edge Detect)

```csharp
var kernel = new[] { 0f, -s, 0f, -s, 1f + 4f * s, -s, 0f, -s, 0f };
return SkiaFilterBuilder.Convolution(3, 3, kernel);
```

## Guides

- [Filter Effects](filter-effects.md) — `SKImageFilter`-based effects (tint, grayscale, blur, glow, pixelate, sharpen)
- [Shader Effects](shader-effects.md) — Runtime SkSL shaders, secondary shader images, compiz transitions
- [Interactive Effects](interactive-effects.md) — Pointer-driven effects (pointer spotlight, reactive grid, water ripple)
- [API Reference](api-reference.md) — Complete type reference and helper utilities
