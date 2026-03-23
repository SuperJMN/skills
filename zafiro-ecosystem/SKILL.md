---
name: zafiro-ecosystem
description: Repository locations and agent documentation for the Zafiro ecosystem (Zafiro core + Zafiro.Avalonia).
---

# Zafiro Ecosystem — Repository Map

The Zafiro ecosystem consists of two main repositories, both located under `/mnt/fast/Repos`:

| Repository | Path | Description |
|---|---|---|
| **Zafiro** | `/mnt/fast/Repos/Zafiro` | Core library — platform-agnostic abstractions, functional helpers, and base services. |
| **Zafiro.Avalonia** | `/mnt/fast/Repos/Zafiro.Avalonia` | Avalonia UI component library — controls, panels, behaviors, converters, dialogs, wizards, navigation, and shell. Depends on Zafiro core. |

## Agent Documentation

Each repository may contain an `AGENTS.md` file at its root. This file is the **primary entry point** for AI coding agents and contains:

- Project identity and tech stack
- Critical rules and conventions
- Key abstractions and canonical file references
- Git/CI workflow (GitVersion, PR conventions)
- Links to deeper documentation (e.g., `docs/ai/`)

### How to use

When working on either repository, **always read its `AGENTS.md` first** to load the project context, conventions, and rules before making any changes.

```
cat /mnt/fast/Repos/Zafiro/AGENTS.md          # Zafiro core (when available)
cat /mnt/fast/Repos/Zafiro.Avalonia/AGENTS.md  # Zafiro.Avalonia
```

> **Note**: As of now, `AGENTS.md` exists in Zafiro.Avalonia. When it is created in the Zafiro core repo, the same conventions apply.

## Cross-Repo Considerations

- **Zafiro.Avalonia depends on Zafiro core** — changes to core abstractions may require coordinated updates.
- Both repos use **GitVersion** for semantic versioning. Squash-merge commit messages must end with `+semver:[major|minor|fix]`.
- Both repos use **Azure Pipelines** for CI (`azure-pipelines.yml`).
- Both repos follow the same C# conventions: no `Async` suffix, no `_` prefix for fields, `Result<T>`/`Maybe<T>` for error handling, ReactiveUI for MVVM.
