---
name: avalonia-effector
description: Creating custom Skia-backed visual effects for Avalonia UI using the Effector library. Filter effects, runtime shaders, interactive pointer-driven effects, and MSBuild integration.
---

# Avalonia Effector — Custom Visual Effects

Effector brings extensible Skia-backed custom effects to **Avalonia 11.3.12** while preserving the public `Visual.Effect : IEffect?` contract. It uses compile-time effect weaving and app-local Avalonia assembly patching — no runtime detours.

**Repository:** <https://github.com/wieslawsoltes/Effector>
**NuGet:** `Effector`

## When to Use This Skill

- User wants to add visual effects (blur, glow, tint, pixelate, etc.) to Avalonia controls
- User needs runtime SkSL shader effects in Avalonia
- User wants pointer-driven interactive effects (spotlight, ripple, reactive grid)
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
        AvaloniaProperty.Register<TintEffect, double>(nameof(Strength), 0.5d);

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
    public Thickness GetPadding(TintEffect effect) => default;
    public Thickness GetPadding(object[] values) => default;

    public SKImageFilter? CreateFilter(TintEffect effect, SkiaEffectContext context) =>
        CreateFilter(new object[] { effect.Color, effect.Strength }, context);

    public SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context)
    {
        var color = (Color)values[0];
        var strength = (double)values[1];
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
| `SkiaRuntimeShaderBuilder` | Creates `SkiaShaderEffect` from SkSL source with uniform configuration and optional fallback renderer |
| `SkiaShaderEffect` | Encapsulates compiled shader + blend mode + fallback. Disposable. |

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
  <EffectorSupportedAvaloniaVersion>11.3.12</EffectorSupportedAvaloniaVersion>
</PropertyGroup>
```

### Build Constraints

- **Use `-m:1`** (sequential build) for clean solution builds — the self-weaver can race under parallel graph builds
- Avalonia version is pinned to **11.3.12**
- Only **Avalonia.Skia** renderer is supported

### Android / Mobile (CRITICAL)

Effector's built-in patching targets only cover `$(TargetDir)` and `$(PublishDir)`, but the Android build pipeline bundles assemblies from `obj/.../android/assets/{abi}/`.  This means **Android APKs ship with unpatched `Avalonia.Base.dll`** and any effect will crash with `InvalidCastException` at the first render frame.

**Tracked upstream:** <https://github.com/wieslawsoltes/Effector/issues/3>

Until Effector ships a native fix, the Android head project needs a workaround target:

```xml
<!-- WORKAROUND for https://github.com/wieslawsoltes/Effector/issues/3
     Remove this target once Effector ships a native fix. -->
<Target Name="Effector_PatchAndroidAssemblies"
        AfterTargets="_PrepareAssemblies"
        BeforeTargets="_BuildApkEmbed"
        Condition="'$(EffectorEnabled)' == 'true' and '$(DesignTimeBuild)' != 'true'
                   and Exists('$(IntermediateOutputPath)android/assets')">
  <ItemGroup>
    <_EffectorAndroidAvaloniaBase Include="$(IntermediateOutputPath)android/assets/*/Avalonia.Base.dll" />
  </ItemGroup>
  <PatchAvaloniaAssembliesTask
      AvaloniaBaseAssemblyPath="%(FullPath)"
      AvaloniaSkiaAssemblyPath="$([System.IO.Path]::Combine('$([System.IO.Path]::GetDirectoryName(%(FullPath)))', 'Avalonia.Skia.dll'))"
      Strict="$(EffectorStrict)"
      Verbose="$(EffectorVerbose)"
      SupportedAvaloniaVersion="$(EffectorSupportedAvaloniaVersion)"
      Condition="'%(_EffectorAndroidAvaloniaBase.Identity)' != ''" />
</Target>
```

iOS likely has a similar issue (assemblies are resolved through a different pipeline), but this has not been tested yet.

```bash
dotnet build -c Release -m:1 -p:GeneratePackageOnBuild=false
```

### NativeAOT

Effector supports `PublishAot=true`. The MSBuild targets patch ILC input assemblies before native compilation:

```bash
dotnet publish -c Release -r osx-arm64 -p:PublishAot=true -p:StripSymbols=false
```

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
- [Shader Effects](shader-effects.md) — Runtime SkSL shaders (scanline, grid, spotlight)
- [Interactive Effects](interactive-effects.md) — Pointer-driven effects (pointer spotlight, reactive grid, water ripple)
- [API Reference](api-reference.md) — Complete type reference and helper utilities
