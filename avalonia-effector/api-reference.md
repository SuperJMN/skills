# API Reference

Complete reference for all public Effector types (Avalonia 12.0.0, Effector 0.5.0).

## Effect Base Classes

### SkiaEffectBase

```csharp
namespace Effector;

public abstract class SkiaEffectBase : Animatable
{
    protected static void AffectsRender<T>(params AvaloniaProperty[] properties) where T : SkiaEffectBase;
    protected void InvalidateEffect();
}
```

- Derive from this for non-interactive effects
- Call `AffectsRender<T>(...)` in the **static constructor** for all properties that trigger re-render
- `InvalidateEffect()` manually requests a re-render

### SkiaInteractiveEffectBase

```csharp
namespace Effector;

public abstract class SkiaInteractiveEffectBase : SkiaEffectBase, ISkiaInputEffectHandler
{
    public virtual void OnAttached(SkiaEffectHostContext context);
    public virtual void OnDetached(SkiaEffectHostContext context);
    public virtual void OnHostBoundsChanged(SkiaEffectHostContext context);
    public virtual void OnPointerEntered(SkiaEffectHostContext context, PointerEventArgs e);
    public virtual void OnPointerExited(SkiaEffectHostContext context, PointerEventArgs e);
    public virtual void OnPointerMoved(SkiaEffectHostContext context, PointerEventArgs e);
    public virtual void OnPointerPressed(SkiaEffectHostContext context, PointerPressedEventArgs e);
    public virtual void OnPointerReleased(SkiaEffectHostContext context, PointerReleasedEventArgs e);
    public virtual void OnPointerCaptureLost(SkiaEffectHostContext context, PointerCaptureLostEventArgs e);
    public virtual void OnPointerWheelChanged(SkiaEffectHostContext context, PointerWheelEventArgs e);
}
```

---

## Attributes

### SkiaEffectAttribute

```csharp
[AttributeUsage(AttributeTargets.Class, AllowMultiple = false, Inherited = false)]
public sealed class SkiaEffectAttribute : Attribute
{
    public SkiaEffectAttribute(Type factoryType);
    public Type FactoryType { get; }
    public string? Name { get; set; }  // For Effect.Parse("name(...)")
}
```

- Applied to effect classes to link them with their factory
- `Name` enables string-based parsing: `Effect.Parse("tint(color=#FF0000, strength=0.5)")`

---

## Factory Interfaces

### ISkiaEffectFactory\<T\>

```csharp
public interface ISkiaEffectFactory<in TEffect> where TEffect : class, IEffect
{
    Thickness GetPadding(TEffect effect);
    SKImageFilter? CreateFilter(TEffect effect, SkiaEffectContext context);
}
```

### ISkiaEffectValueFactory

```csharp
public interface ISkiaEffectValueFactory
{
    Thickness GetPadding(object[] values);
    SKImageFilter? CreateFilter(object[] values, SkiaEffectContext context);
}
```

### ISkiaShaderEffectFactory\<T\>

```csharp
public interface ISkiaShaderEffectFactory<in TEffect> where TEffect : class, IEffect
{
    SkiaShaderEffect? CreateShaderEffect(TEffect effect, SkiaShaderEffectContext context);
}
```

### ISkiaShaderEffectValueFactory

```csharp
public interface ISkiaShaderEffectValueFactory
{
    SkiaShaderEffect? CreateShaderEffect(object[] values, SkiaShaderEffectContext context);
}
```

### ISkiaInputEffectHandler

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

---

## Context Types

### SkiaEffectContext

Passed to filter-based factories. Carries opacity state.

```csharp
public readonly struct SkiaEffectContext
{
    public double EffectiveOpacity { get; }
    public bool UsesOpacitySaveLayer { get; }

    public SKColor ApplyOpacity(SKColor color, double opacity = 1d);
    public SKColor CreateColor(byte red, byte green, byte blue, double opacity = 1d);

    public static float BlurRadiusToSigma(double radius);
    public static byte ClampToByte(double value);
}
```

### SkiaShaderEffectContext

Extends filter context with content image and bounds. Passed to shader factories.

```csharp
public readonly struct SkiaShaderEffectContext
{
    public double EffectiveOpacity { get; }
    public bool UsesOpacitySaveLayer { get; }
    public SKRect ContentRect { get; }
    public SKRect EffectBounds { get; }

    public SKColor ApplyOpacity(SKColor color, double opacity = 1d);
    public SKColor CreateColor(byte red, byte green, byte blue, double opacity = 1d);
    public SKShader CreateContentShader(
        SKShaderTileMode tileModeX = SKShaderTileMode.Clamp,
        SKShaderTileMode tileModeY = SKShaderTileMode.Clamp);
    public SKShader CreateContentShader(
        SKShaderTileMode tileModeX,
        SKShaderTileMode tileModeY,
        SKMatrix localMatrix);

    public static float BlurRadiusToSigma(double radius);
    public static byte ClampToByte(double value);
}
```

### SkiaEffectHostContext

Passed to interactive effect handlers. Provides pointer and visual utilities.

```csharp
public readonly struct SkiaEffectHostContext
{
    public SkiaEffectBase Effect { get; }
    public Visual Visual { get; }
    public InputElement? InputElement { get; }
    public Rect Bounds { get; }
    public Size Size { get; }
    public Rect InputBounds { get; }
    public Size InputSize { get; }
    public bool HasInput { get; }

    public Point GetPosition(PointerEventArgs e);
    public Point GetNormalizedPosition(PointerEventArgs e, bool clamp = true);
    public Point Normalize(Point position, bool clamp = true);
    public void CapturePointer(PointerEventArgs e);
    public void ReleasePointerCapture(PointerEventArgs e);
    public void Invalidate();
}
```

---

## Shader Types

### SkiaShaderEffect

Encapsulates a compiled shader, blend mode, owned resources, and optional fallback renderer. **Disposable.**

```csharp
public sealed class SkiaShaderEffect : IDisposable
{
    public SkiaShaderEffect(
        SKShader? shader,
        SKBlendMode blendMode = SKBlendMode.SrcOver,
        bool isAntialias = true,
        SKRect? destinationRect = null,
        SKMatrix? localMatrix = null,
        Action<SKCanvas, SKImage, SKRect>? fallbackRenderer = null,
        IEnumerable<IDisposable>? ownedResources = null);

    public SKShader? Shader { get; }
    public SKBlendMode BlendMode { get; }
    public bool IsAntialias { get; }
    public SKRect? DestinationRect { get; }
    public SKMatrix? LocalMatrix { get; }
    public Action<SKCanvas, SKImage, SKRect>? FallbackRenderer { get; }

    public void RenderFallback(SKCanvas canvas, SKImage contentImage);
    public void Dispose();
}
```

The `ownedResources` are disposed in reverse order when the effect is disposed. Use this for `SkiaShaderImageLease`, child `SKShader` instances, or any transient GPU resources tied to the effect's lifetime.

### SkiaRuntimeShaderBuilder

Static factory for creating `SkiaShaderEffect` from SkSL source:

```csharp
public static class SkiaRuntimeShaderBuilder
{
    public static SkiaShaderEffect Create(
        string sksl,
        SkiaShaderEffectContext context,
        Action<SKRuntimeEffectUniforms>? configureUniforms = null,
        Action<SKRuntimeEffectChildren, SkiaShaderEffectContext>? configureChildren = null,
        string? contentChildName = null,
        bool isOpaque = false,
        SKBlendMode blendMode = SKBlendMode.SrcOver,
        bool isAntialias = true,
        SKRect? destinationRect = null,
        SKMatrix? localMatrix = null,
        Action<SKCanvas, SKImage, SKRect>? fallbackRenderer = null,
        Action<SKRuntimeEffectChildren, SkiaShaderEffectContext, ICollection<IDisposable>>? configureOwnedChildren = null,
        IEnumerable<IDisposable>? ownedResources = null);
}
```

- Caches compiled `SKRuntimeEffect` by SkSL string — use `const string` for cache hits
- Falls back to `fallbackRenderer` when `EffectorRuntime.DirectRuntimeShadersEnabled` is false or compilation fails
- **`configureOwnedChildren`**: Like `configureChildren` but with an `ICollection<IDisposable>` for child shaders that must be disposed when the effect is disposed
- **`ownedResources`**: Additional disposable resources (e.g., `SkiaShaderImageLease`) to tie to the effect's lifetime

---

## Secondary Shader Image Types

### SkiaShaderImageHandle

Value-type handle referencing a registered `SKImage`. Compatible with Effector's immutable snapshot model (safe in `StyledProperty<SkiaShaderImageHandle>`).

```csharp
public readonly struct SkiaShaderImageHandle : IEquatable<SkiaShaderImageHandle>
{
    public long Value { get; }
    public bool IsEmpty { get; }
}
```

### SkiaShaderImageRegistry

Thread-safe registry for managing secondary shader images:

```csharp
public static class SkiaShaderImageRegistry
{
    public static SkiaShaderImageHandle Register(Bitmap bitmap);
    public static bool TryAcquire(SkiaShaderImageHandle handle, out SkiaShaderImageLease? lease);
    public static void Release(SkiaShaderImageHandle handle);
}
```

- `Register` converts an Avalonia `Bitmap` into an `SKImage` and returns a handle
- `TryAcquire` returns a lease that keeps the `SKImage` alive
- `Release` marks the handle for disposal (actual disposal deferred until all leases are released)

### SkiaShaderImageLease

RAII lease keeping a registered `SKImage` alive until disposed:

```csharp
public sealed class SkiaShaderImageLease : IDisposable
{
    public SKImage Image { get; }
    public void Dispose();
}
```

---

## Helper Utilities

### SkiaFilterBuilder

Static methods for creating `SKImageFilter` instances:

| Method | Signature |
|---|---|
| `ColorFilter` | `(SKColorFilter?, SKImageFilter?) → SKImageFilter?` |
| `Blur` | `(double radius, SKImageFilter?) → SKImageFilter?` |
| `Convolution` | `(int w, int h, float[] kernel, float gain, float bias, bool convolveAlpha, SKImageFilter?) → SKImageFilter` |
| `Pixelate` | `(float cellSize) → SKImageFilter` |
| `Merge` | `(params SKImageFilter?[]) → SKImageFilter` |
| `Compose` | `(SKImageFilter outer, SKImageFilter inner) → SKImageFilter` |
| `Offset` | `(double x, double y, SKImageFilter?) → SKImageFilter` |
| `Matrix` | `(SKMatrix, SKSamplingOptions?, SKImageFilter?) → SKImageFilter` |
| `Dilate` | `(float rx, float ry, SKImageFilter?) → SKImageFilter` |
| `Erode` | `(float rx, float ry, SKImageFilter?) → SKImageFilter` |

### ColorMatrixBuilder

5×4 color matrix (`float[20]`) builder:

| Static Method | Returns |
|---|---|
| `CreateIdentity()` | Identity matrix |
| `CreateGrayscale(amount)` | Grayscale (0 = original, 1 = full) |
| `CreateSepia(amount)` | Sepia tone |
| `CreateSaturation(saturation)` | 0 = gray, 1 = normal, >1 = vivid |
| `CreateBrightnessContrast(brightness, contrast)` | Combined adjustment |
| `CreateInvert(amount)` | Color inversion |
| `Blend(from, to, amount)` | Interpolate two matrices |

Fluent API:

```csharp
var filter = new ColorMatrixBuilder()
    .SetSaturation(1.3f)
    .SetBrightnessContrast(0.05f, 1.1f)
    .ToColorFilter();
```

---

## MSBuild Properties

| Property | Default | Description |
|---|---|---|
| `EffectorEnabled` | `true` | Enable/disable Effector |
| `EffectorStrict` | `true` | Fail build on weaving errors |
| `EffectorVerbose` | `false` | Emit detailed build logs |
| `EffectorSupportedAvaloniaVersion` | `12.0.0` | Expected Avalonia version |

---

## Constraints and Pitfalls

1. **Sequential builds required**: Use `-m:1` for solution builds to avoid self-weaver races
2. **Avalonia 12.0.0 only**: Effector patches specific Avalonia assembly versions
3. **Skia renderer only**: Non-Skia renderers are not supported
4. **Render-thread safety**: Factory `object[]` methods run on the render thread — never access `AvaloniaObject` or UI-thread state
5. **Value ordering**: The `object[]` array matches the property declaration order in the effect class — use `const int` index fields
6. **Shader source as `const string`**: Enables `SkiaRuntimeShaderBuilder` cache hits
7. **Always provide `fallbackRenderer`** for shader effects to support environments without runtime shader support
8. **`sealed` effect classes**: Effect classes should be `sealed` for correct weaving
9. **Owned resources**: When using secondary shader images or transient child shaders, pass them as `ownedResources` or via `configureOwnedChildren` so they are disposed with the `SkiaShaderEffect`
10. **Release shader image handles**: Call `SkiaShaderImageRegistry.Release(handle)` when the image is no longer needed; the underlying `SKImage` is disposed once all leases are returned
