# Proteus UI reviewer conventions

The authoritative, evidence-grounded convention set for `QuantumSi/proteus-ui`,
distilled from three months of PR reviews (weighted toward recurring Vilius
comments). It is one artifact serving two branches:

- as an **audit reference**, when reviewing or correcting a branch;
- as the **pre-PR recipe** — the "smell of a well-made PR" — the author runs
  before opening or updating a PR.

Close every mechanical and stylistic item yourself so review comments stay on
engineering substance. Apply rules only to code the branch adds or materially
changes; never churn unrelated mainline code to match this reference.

## Evidence hierarchy

1. Current user request, issue, spec, or roadmap.
2. Current repository `AGENTS.md`, `.editorconfig`, projects, and tests.
3. Observable behavior in the chosen base, normally `origin/main` for a
   behavior-neutral refactor.
4. Recurring Vilius comments and prior automatic review findings (tagged below).
5. Local stylistic precedent in adjacent code.

When two sources conflict, report the conflict and follow the higher source.
Evidence tags below are `(PR#nn)` for the discussion that established the rule,
or `MF-`/`SF-` for the codified automatic-review finding that enforces it.

## Mechanical — expect zero reviewer comments here

- [ ] No dangling/trailing commas in enums, collection/array/object
  initializers, or record definitions. Do a once-over across the whole diff, not
  just the line you touched. (PR#112)
- [ ] Single-line `//` comments have no trailing period. Only `///` XML docs use
  normal grammatical punctuation.
  (https://github.com/QuantumSi/proteus-ui/pull/110#pullrequestreview-4705522746;
  MF-1)
- [ ] At most one consecutive blank line. No leftover blank lines at the top of a
  file, after `{`, or between members. (PR#54/55/76/113; SF-1)
- [ ] No commented-out code, dead code, or leftovers from testing (temporary
  `CtaButton` styles, debug values, throwaway names). (PR#52/55/60/76)
- [ ] No redundant `using` directives; one `using` per namespace, unused ones
  removed. (PR#55)
- [ ] No `global using`, no project-level `<Using>` items, no implicit usings —
  declare usings per class file. Do not remove inherited implicit-usings config
  from unrelated projects merely to satisfy this. (PR#110)
- [ ] Namespace matches the file's folder/project. (SF-14)
- [ ] Access modifiers are explicit (`private`, etc.); do not rely on defaults.
  (PR#110)
- [ ] No primary constructors except on `record`/`struct`. (PR#110)
- [ ] Member order inside a type: public properties/events/commands → private
  fields → constructor → public/protected methods → private methods. All methods
  live below the constructor.
  (https://github.com/QuantumSi/proteus-ui/pull/110#discussion_r3588759225;
  PR#113)
- [ ] Asset files (`.svg`, `.png`) sit in the correct folder, follow the
  existing naming format, and unused assets are deleted. (PR#76)
- [ ] `.editorconfig` governs file-scoped namespaces, braces, modifier order,
  readonly fields, naming, and spacing.

## Comments & XML docs

Treat missing or invalid documentation on a new public product API as Must Fix.

- [ ] Every branch-added public type, member, and constructor has a concise
  `<summary>`, a `<param>` for each parameter (including every public positional
  record component), and `<returns>` for value/`Task`-returning members. (MF-2)
- [ ] `/// <inheritdoc/>` on interface implementations and overrides when the
  inherited contract is complete — including converters' `Convert`, `Dispose`,
  `GetName`, `OnNavigatedTo`. (SF-12; PR#76)
- [ ] `<see cref="..."/>` for code symbols, and every `cref` resolves.
  (https://github.com/QuantumSi/proteus-ui/pull/110#discussion_r3588743267)
- [ ] Interface/`<summary>` docs describe the observable contract only — never
  name the concrete implementation, view, organism, navigation host, or DI
  mechanism. Naming an implementation is not a `cref` and drifts out of sync.
  (PR#110)
- [ ] No "Gets or sets" boilerplate; write a short domain description. (PR#110)
- [ ] XML docs updated whenever a signature or parameter list changes. (PR#110)
- [ ] Do not drop accessibility just to silence `CS1591`; prove the public
  surface is unnecessary and Avalonia stays correct first.
- [ ] Regular `//` comments are rare and essential; none narrate a refactor,
  justify a review decision, record history, or note a port ("ported from
  `DialogManager`"). No narrative XAML comments. (PR#110)
- [ ] Preserve comments inherited unchanged from the base unless the task changes
  their policy.

Interface summaries — prefer the contract, not the rendering:

```csharp
/// <summary>
/// Provides the actions available while reviewing the run configuration.
/// </summary>
```

Avoid:

```csharp
/// <summary>
/// Supplies commands to ReviewConfigurationView inside the organism.
/// </summary>
```

### Documentation diagnostic

Normal builds stay clean while a documentation-enabled build exposes `CS1591`
(missing docs) or `CS1574` (invalid `cref`):

```bash
DOTNET_ENVIRONMENT=Testing dotnet build Proteus.Ui.sln --no-restore \
  -p:GenerateDocumentationFile=true
```

Intersect `CS1591`/`CS1574` by file and line with the branch-added lines:

```bash
git diff --unified=0 <base>...HEAD -- '*.cs'
```

Target: zero branch-added product declarations with `CS1591` and zero
branch-added invalid `cref`. Pre-existing base warnings are evidence, not
license for unrelated cleanup.

## Naming, types & values

- [ ] Repeated state is a collection, not N hard-coded copies (4 wells / 4
  columns → a collection of item view models; no `NotifyAll`). (PR#48/55/88)
- [ ] Enums, not magic strings, for severity/state; bind or `switch` on the enum
  directly instead of wrapping it in booleans. (PR#55/61)
- [ ] Enum member names carry meaning, not implementation detail
  (`Default/Add/Remove/Success/Error`, not `BlueAdd/GreenSuccess`). (PR#76)
- [ ] Magic numbers and time delays extracted to named constants / `TimeSpan`.
  (MF-8; SF-16)
- [ ] `nameof(Type)` for configuration section names and similar identifiers.
  (PR#113)
- [ ] Exception/message wording is clear and canonical (e.g. "Current run
  session cannot be null"). (PR#112)
- [ ] Prefer `[NotifyPropertyChangedFor(nameof(X))]` over manual notification
  helpers. (PR#48/55)

## Avalonia / XAML & design tokens

- [ ] No hard-coded visual values — padding, spacing, corner radius, thickness,
  width, font size, and animation duration all come from Figma design tokens /
  resources. This is the single most frequent reviewer comment.
  (PR#58/60/76/105/110; SF-9)
- [ ] Reuse existing typography styles, `ControlTheme`s, converters, and
  resources before defining a local one (e.g.
  `TypographyHeadingsDisplayH6TextBlock`). (PR#105)
- [ ] No code-behind for view logic — use an attached behavior, a
  custom/templated control, or resources. (PR#63/76)
- [ ] Converters never throw; expose brushes/values as settable properties wired
  from a resource dictionary rather than hard-coding them. (PR#76)
- [ ] Do not add `x:CompileBindings="True"` in projects that already set
  `<AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>`
  (e.g. `Proteus.Ui.Pages`, `Proteus.Ui`) — it is redundant there. Just declare a
  proper `x:DataType`; compiled bindings are already the default. Only set
  `x:CompileBindings` explicitly in a project/view where the default is off and
  the binding contract supports it. (user-reported)
- [ ] No stray `x:Name`/`Name`, no wrapping elements (e.g. `Image` in a
  `Border`) without a reason. (PR#54/58)
- [ ] Do not copy Figma structure literally into the view model or navigation
  model.

## Structure & architecture

- [ ] Each type is in the correct project/namespace and respects dependency
  direction: domain types in `Proteus.Ui.Domain`, shared contracts in
  `Proteus.Ui.Shared.Interfaces`; `Proteus.Ui.Shared` must not depend on
  `Proteus.Ui.Components`. (PR#112)
- [ ] Views and their view models stay in the same project. (PR#110)
- [ ] UI concerns stay out of domain classes. (PR#110)
- [ ] No abstraction that abstracts nothing (pointless factories/interfaces);
  use the existing type or `IRuntimeInterface` directly unless a wrapper adds a
  real contract. (PR#110/112)
- [ ] Prefer DI resolution over view models holding references to one another.
  (PR#112)
- [ ] Data comes from its authority (scan the DB/protobuf for metric names)
  rather than a hard-coded catalog. (PR#113)
- [ ] No duplicated helpers; extract shared formatters/utilities. (SF-3)
- [ ] Keep navigation, flow coordination, and page presentation as distinct
  contracts; do not change a state machine unless a transition bug is reproduced
  or the task changes its contract.

## Correctness & lifetime

- [ ] No `async void` except real UI event handlers (`object sender, EventArgs
  e`); use `async Task`. Never assign an `async` lambda to an `Action<T>`. (MF-4)
- [ ] No fire-and-forget `_ = FooAsync()` that swallows exceptions; await it or
  handle failures explicitly.
- [ ] Every subscribed event handler is unsubscribed.
- [ ] `Dispose` follows the canonical Microsoft shape, even when no finalizer
  exists: `Dispose()` calls `Dispose(true)` then `GC.SuppressFinalize(this)`,
  and `Dispose(bool)` carries the `_isDisposed` guard, releases managed state
  under `if (disposing)`, and sets the flag last. Prefer one consistent shape
  over the minimal one. Use `protected virtual Dispose(bool)` on unsealed types
  and `private void Dispose(bool)` on sealed types. (JPUI-105;
  https://github.com/QuantumSi/proteus-ui/pull/127#issuecomment-5330766287;
  https://github.com/QuantumSi/proteus-ui/pull/125#pullrequestreview-4962843632)
- [ ] The disposed guard never lives in `Dispose()` while the work sits in
  `Dispose(bool)`; a derived override would then run before the guard. (PR#125)
- [ ] Seal a disposable type when nothing derives from it, so the overload can
  be `private`. Name the flag `_disposed`, which is what the repo uses
  everywhere except `SkiaImage`. (JPUI-105)
- [ ] State/identifiers are captured into locals before an `await` to avoid
  races (e.g. a delete-during-await deleting the wrong run).
- [ ] No unsafe hard casts that throw if a factory/mapping changes.

## PR hygiene & process

- [ ] The diff contains only changes for this ticket — no unrelated edits, no
  drive-by reformatting. Reviewers ask "Why is this change in this PR?" (PR#63)
- [ ] The diff is small and reviewable; pick/rebase the right base branch so only
  relevant changes show. (PR#68/76)
- [ ] Every change traces to a ticket; defer out-of-scope improvements by filing
  a ticket, not by leaving a TODO or doing it here. (PR#52/87/88/110)
- [ ] No new external library dependency — Zafiro, `CSharpFunctionalExtensions`,
  or any other — unless the task explicitly requests it; a transitive addition
  does not bypass the rule. Verify framework compatibility before adding an
  approved one (e.g. SkiaSharp vs Avalonia 11, PR#76). Never make a production
  project depend on a test project; avoid new production-to-production
  `ProjectReference` edges.
- [ ] Pre-PR gate is green: build, tests, `dotnet format --verify-no-changes`,
  `git diff --check`, and the documentation diagnostic for public API changes.

## Findings buckets

Report audit findings as:

- **Must Fix** — defect, spec mismatch, reviewer-convention violation, invalid
  docs, unnecessary scope, or failed gate.
- **Follow-up** — beneficial but scope-expanding design work; file a ticket.
- **Inherited** — unchanged base behavior or warning, outside scope unless asked.

A PR is not review-ready until every Must Fix is closed and the standard build,
tests, format check, and diff check pass.
