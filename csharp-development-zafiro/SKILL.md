---
name: csharp-development-zafiro
description: Use for C# changes inside Zafiro ecosystem repositories when their established conventions require Zafiro-specific naming or functional patterns. Do not trigger for arbitrary .NET code that merely consumes a Zafiro library.
---

# C# Development Standards (Zafiro)

This skill encompasses the general C# coding standards and functional programming patterns used across all Zafiro projects.

Repository instructions, `.editorconfig`, existing public contracts, and
adjacent code take precedence. Preserve an established convention rather than
renaming or restructuring unrelated code to match this reference.

## Naming & Coding Standards

- **Explicit Names**: Favor clarity over cleverness.
- **Async Suffix**: Follow the repository and API being implemented. Current
  Zafiro sources contain both domain-specific names and conventional `Async`
  suffixes; preserve inherited names and adjacent public API patterns.
- **Private Fields**: Follow the repository's current naming rules and adjacent
  code. Zafiro and Zafiro.Avalonia commonly use `_camelCase`; do not mass-rename
  existing fields to impose a different convention.
- **Static State**: Avoid static state unless explicitly justified and documented.
- **Method Design**: Keep methods small, expressive, and with low cyclomatic complexity.

## Functional Programming & Error Handling

Use **CSharpFunctionalExtensions** only when it is already an approved
dependency and the surrounding code uses it for the same contract. This skill
does not authorize adding the package.

- **Result & Maybe**: Use these types for flow control and error handling instead of nulls or exceptions.
- **Exceptions**: Reserved strictly for truly exceptional, unrecoverable situations.
- **Boundaries**: Preserve the boundary's established error contract. Translate
  exceptions into `Result` only where that is the verified contract, and never
  swallow unexpected failures.

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
