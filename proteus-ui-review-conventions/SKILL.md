---
name: proteus-ui-review-conventions
description: Audit and minimally fix QuantumSi/proteus-ui branches against the repository's recurring review conventions — the "smell of a well-made PR" distilled from Vilius's reviews. Use when Codex reviews, prepares, cleans up, or fixes a proteus-ui branch or PR, or runs a pre-PR self-check, covering XML docs, comment and comma hygiene, member ordering, design tokens, interface contracts, project and dependency boundaries, diff scope, and pre-PR validation.
---

# Proteus UI review conventions

## Establish the contract

1. Work only inside a `QuantumSi/proteus-ui` checkout.
2. Read the repository `AGENTS.md`, the task specification, and any named
   roadmap completely before acting.
3. Inspect the live branch, worktree, upstream, and merge base. Treat live state
   as authoritative.
4. Determine the requested mode:
   - for review, report evidence without editing;
   - for preparation, cleanup, or correction, implement the smallest justified
     patch and validate it;
   - never push, alter a PR, or rewrite history unless explicitly requested.
5. Use the task specification as the behavior contract. When the work is a
   refactor, use `origin/main` as the functional oracle unless the user names an
   intentional behavior change.

[references/reviewer-conventions.md](references/reviewer-conventions.md) is the
single source of truth for the conventions. Read it before a detailed audit or
any correction pass, and run it as the pre-PR recipe — the "smell of a well-made
PR" — before opening or updating a PR, so review comments stay on engineering
substance. The audit priorities below are the ordered process; that file holds
the exhaustive, evidence-tagged rules.

## Build the exact review scope

Set the base from the task or merge base; do not assume it blindly.

```bash
git status --short --branch
git diff --name-status <base>...HEAD
git diff --stat <base>...HEAD
git diff --check <base>...HEAD
```

Include committed and uncommitted changes when preparing a live branch. Separate:

- new files;
- modifications to mainline files;
- deletions and moves;
- package and project-reference changes;
- tests;
- unrelated or pre-existing worktree changes.

Use `git cat-file -e <base>:<path>` when provenance matters. Do not rewrite
comments or style inherited unchanged from the base.

If `.codegraph/` exists, follow the repository CodeGraph instructions and use
concrete identifiers or paths. Verify relevant source and tests before drawing
architectural conclusions.

## Audit in priority order

1. **Scope and parity**
   - detect unrelated files and opportunistic fixes;
   - compare changed behavior with the base;
   - preserve explicitly accepted architectural gains;
   - do not absorb bugs already present in `main` unless requested.
2. **Correctness and lifetime**
   - inspect navigation, DI registrations, observable subscriptions, disposal,
     async commands, and page/viewmodel lifetime;
   - distinguish defects from judgment-only follow-ups.
3. **Public contracts and XML**
   - require complete, valid, concise XML docs for branch-added public product
     APIs;
   - keep interface docs implementation-independent;
   - resolve every `cref`.
4. **Reviewer style**
   - apply the expected member ordering;
   - avoid new class primary constructors and new global/project-level usings;
   - keep regular comments rare, short, and without a final period.
5. **Avalonia and XAML**
   - prefer compiled bindings where the view contract supports them;
   - reuse established styles, themes, converters, and resources;
   - avoid narrative XAML comments and redundant visual literals.
6. **Dependencies**
   - reject new external dependencies by default;
   - ask for explicit permission before adding any external library;
   - avoid new references between production projects;
   - allow test projects to reference the production projects they test;
   - preserve existing dependencies unless their removal is in scope.
7. **Tests**
   - add or change tests only for observable behavior or an explicit durable
     contract not already covered;
   - for an unused overload or API deletion with unchanged behavior, migrate
     every consumer and compile by default;
   - use reflection/API-surface tests only when the exact public surface is a
     stated long-term requirement and assert no broader invariant than the test
     proves;
   - do not add tests solely to bless an unrelated inherited bug fix.

Classify findings as:

- **Must Fix**: correctness, task/spec violation, reviewer rule, invalid docs,
  unjustified scope, or validation failure;
- **Follow-up**: worthwhile design improvement that would expand this PR;
- **Inherited**: unchanged base behavior or warning, outside scope unless asked.

## Correct with minimum diff

- Touch only files needed to close a concrete Must Fix.
- Prefer deletion or restoration of unnecessary branch deltas over compensating
  code.
- Keep structural moves behavior-neutral.
- Reorder members mechanically without renaming or refactoring.
- Use `inheritdoc` when it accurately supplies the full public contract.
- Add only concise contract documentation; keep rationale in the PR or roadmap.
- Do not add a package or production project reference while awaiting permission.
- Preserve unrelated user changes and re-check scope after every branch movement.
- Remove tests that merely restate a one-off structural edit without protecting
  an observable or explicitly durable contract.

## Validate

Choose tests proportional to the change, then finish a pre-PR correction with:

```bash
dotnet restore Proteus.Ui.sln
DOTNET_ENVIRONMENT=Testing dotnet build Proteus.Ui.sln --no-restore
DOTNET_ENVIRONMENT=Testing dotnet test Proteus.Ui.sln --no-build --no-restore
dotnet format Proteus.Ui.sln --verify-no-changes --no-restore
git diff --check
```

Run restore only when needed for the package graph or when assets are missing.
Do not run build and tests concurrently against the same output directories.

Also:

- repeat the branch-diff inventory against the final HEAD and worktree;
- run the documentation diagnostic described in the reference for public API
  changes;
- inspect the direct and transitive package graph after dependency changes;
- distinguish new warnings from warnings inherited from the base;
- perform runtime/MCP validation when the changed Avalonia behavior cannot be
  established confidently through build and tests.

## Report

Lead with whether the branch is review-ready. List Must Fix findings first with
exact paths and evidence, then follow-ups and inherited findings. State:

- base and reviewed scope;
- behavior/parity conclusion;
- validation commands and exact results;
- remaining uncertainty;
- whether any commit or remote action occurred.

Do not describe a branch as clean while a known Must Fix remains.
