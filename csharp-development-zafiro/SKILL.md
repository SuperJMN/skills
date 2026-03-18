---
name: csharp-development-zafiro
description: General C# development standards and functional programming patterns for Zafiro projects.
---

# C# Development Standards (Zafiro)

This skill encompasses the general C# coding standards and functional programming patterns used across all Zafiro projects.

## Naming & Coding Standards

- **Explicit Names**: Favor clarity over cleverness.
- **Async Suffix**: Do **NOT** use the `Async` suffix in method names, even if they return `Task`.
- **Private Fields**: Do **NOT** use the `_` prefix for private fields.
- **Static State**: Avoid static state unless explicitly justified and documented.
- **Method Design**: Keep methods small, expressive, and with low cyclomatic complexity.

## Functional Programming & Error Handling

Zafiro relies heavily on **CSharpFunctionalExtensions** for clean, predictable flow control.

- **Result & Maybe**: Use these types for flow control and error handling instead of nulls or exceptions.
- **Exceptions**: Reserved strictly for truly exceptional, unrecoverable situations.
- **Boundaries**: Never allow exceptions to leak across architectural boundaries.

### Prefer Functional Mapping over Explicit Checks

Favor functional operators over explicit `if (result.HasValue)` or `if (result.IsSuccess)` checks for cleaner and more declarative code.

- **`Map`**: Use when you want to transform the value.
- **`Tap`**: Use for side effects (e.g., logging) when you want to keep the flow.
- **`Bind`**: Use when the transformation itself returns a `Result` or `Maybe`.
- **`Match`**: Use when you need to handle both cases (Success/Failure or Some/None) and return a value or Task (branching).

### Prefer Returning `Result<T>` Directly When Caller Expects `Result`

When a method returns `Task<Result>` and the SDK/service returns `Task<Result<T>>`, prefer returning the chained result directly instead of manually converting with `Match`/`if`.

- Keep side effects with `Tap(...)`.
- Let failures flow naturally without re-wrapping.
- Avoid extra conversions like `result.Match(_ => Result.Success(), Result.Failure)` unless branching logic is actually needed.

#### Preferred Pattern
```csharp
private async Task<Result> ApproveInvestment(...)
{
    return await service
        .ApproveInvestment(request)
        .Tap(_ => Load.Execute(null));
}
```

#### Anti-Pattern
```csharp
if (result.HasValue)
{
    await notificationService.Show($"Success: {result.Value}", "Done");
}
```

#### Preferred Pattern
```csharp
// Use Tap for side effects
result.Tap(x => notificationService.Show($"Success: {x}", "Done"));
```

> [!NOTE]
> Use the imperative `if` check only if using the functional approach significantly impacts readability.

## Verification

- **Compilation Check**: Before finishing a task, you **MUST** always check that the code is compilable using `dotnet build` and verifying that there are no errors.
