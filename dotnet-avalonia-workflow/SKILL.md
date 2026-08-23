---
name: dotnet-avalonia-workflow
description: Use for changes to Avalonia UI behavior, AXAML, controls, styles, bindings, or view lifecycle in a .NET app that uses Zafiro. Do not trigger merely because the repository is an Avalonia app, or for domain services, shared interfaces, backend code, test-only edits, or general C# refactors with no UI effect.
---

# .NET Avalonia workflow

Keep this workflow proportional to the UI change.

## Scope gate

Establish that the requested change affects at least one UI concern:

- AXAML, styles, themes, resources, or bindings;
- an Avalonia control or behavior;
- view or ViewModel lifecycle as observed by the UI;
- navigation or interaction whose visual/runtime behavior must be validated.

For a shared-interface cleanup, domain/service refactor, backend change, or
test-only task with no UI effect, stop using this skill and follow the
repository's normal .NET workflow.

## Load references conditionally

- Use `avalonia-zafiro-development` when choosing or changing a Zafiro/Avalonia
  control, behavior, style, or reactive UI pattern.
- Use `avalonia-layout-zafiro` only for layout or responsive-design changes.
- Use `avalonia-viewmodels-zafiro` only when ViewModel lifecycle, commands, or
  wizard behavior changes.
- Use `csharp-development-zafiro` only for Zafiro-specific C# conventions not
  already established by the repository.
- Use `dotnet-testing-khorikov` only after deciding that changed observable
  behavior needs a new or modified test.

Repository instructions and adjacent working code override generic guidance.

## Workflow

1. Read the task contract and inspect the existing UI path, styles, resources,
   and nearby tests.
2. Implement the smallest change that satisfies the contract. Reuse established
   controls and resources unless the task intentionally changes the pattern.
3. Choose proof that matches the change:
   - behavior change: focused test at an observable seam;
   - visual or interaction change: build plus runtime/MCP inspection when
     available;
   - binding or resource change: compiled build plus focused runtime inspection;
   - compile-time API cleanup with no UI behavior change: migrate consumers and
     build; do not add a negative reflection test unless the API surface itself
     is an explicit durable requirement and the repository has a suitable
     architecture/API test suite.
4. Run the narrowest relevant validation first, then the affected project or
   solution gates required by the repository.
5. Inspect the final diff for unrelated UI, test, package, and formatting
   changes.

## XAML testing

Prefer observable ViewModel/service behavior, compiled binding validation, and
runtime UI evidence. Add tests that parse AXAML or assert markup shape only when
the markup structure itself is the requested durable contract.

## Publication boundary

This skill does not authorize creating branches, commits, pushes, pull requests,
merges, package changes, or history rewrites. Perform those actions only when
the user explicitly requests them and use the dedicated publication workflow.

## Completion

The task is complete when the requested UI behavior is demonstrated, affected
validation passes, the diff is scoped, and every new test protects an observable
requirement that could regress.
