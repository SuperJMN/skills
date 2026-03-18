---
name: dotnet-avalonia-workflow
description: Use when working on Avalonia UI apps with the Zafiro toolkit and needing the standard .NET development workflow and verification steps
---

# .NET Avalonia Workflow (Zafiro)

## Overview

Minimal, repeatable workflow for Avalonia + Zafiro changes, with verification that fits .NET projects.

## When to Use

- Modifying Avalonia UI apps using Zafiro.
- Editing XAML styles, lookless controls, or ViewModels.
- Preparing to finish a change and needing verification steps.

## Required Skills

- **REQUIRED SUB-SKILL:** avalonia-zafiro-development
- **REQUIRED SUB-SKILL:** csharp-development-zafiro
- **REQUIRED SUB-SKILL:** dotnet-testing-khorikov
- **REQUIRED SUB-SKILL:** avalonia-layout-zafiro (when layout changes)
- **REQUIRED SUB-SKILL:** avalonia-viewmodels-zafiro (when ViewModels or wizards change)

## Core Workflow

1. Search for existing patterns or helpers before adding new ones.
2. Implement using Zafiro conventions and functional-reactive MVVM.
3. If a new style file is added, register it in `App.axaml` or `Styles.axaml`.
4. Add or update tests when behavior changes, following Khorikov principles.
5. Verify with the standard .NET commands.

## XAML Critical Checks

- Use `EnhancedButton` instead of `Button`.
- Add `x:DataType` for compiled bindings.
- Use `Design.PreviewWith` in style and theme files.
- Register new `.axaml` files in the root style file.
- Use `[ControlName].axaml.cs` for lookless controls.

## Verification

- `dotnet build`
- `dotnet test` (if tests exist)
- `dotnet format` (if configured)

## Default PR Workflow (GitVersion)

When working on features in repositories that use GitVersion, follow this default workflow:

1. Create a branch for the feature.
2. Implement the feature.
3. Push changes.
4. Push to master (one or more commits, depending on the flow).
5. Create a PR with an explanatory message excluding boilerplate, focusing on the global idea and important future details.
6. Wait for CI to pass.
7. Squash merge the PR using GitVersion semver: The squash merge commit message MUST end with `+semver:[major|minor|fix]` so GitVersion correctly bumps the version.
