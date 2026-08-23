---
name: avalonia-zafiro-development
description: Use when an Avalonia task actually changes Zafiro controls, behaviors, styles, bindings, or reactive UI composition and needs repository-grounded implementation guidance. Do not trigger for unrelated C# work merely because the application references Zafiro.
---

# Avalonia and Zafiro development

Treat the current repository and the local Zafiro sources as the oracle. Generic
preferences never override an established application contract.

## Establish the local contract

1. Read repository instructions and the task specification.
2. Inspect adjacent views, styles, resources, ViewModels, and tests.
3. When a Zafiro abstraction is involved, inspect its source instead of
   inferring behavior from its name or package metadata:
   - `/mnt/fast/Repos/Zafiro`
   - `/mnt/fast/Repos/Zafiro.Avalonia`
4. Preserve the existing control, namespace, preview, and composition patterns
   unless the task explicitly changes them.

## Make evidence-based choices

- Use `EnhancedButton` when the application already uses it or when its verified
  command state, role, intent, or icon contract is needed. A standard `Button`
  is valid when that is the established or sufficient contract.
- Use namespace prefixes exactly as the target project requires. Confirm local
  namespace registration or compile behavior before removing a prefix.
- Add `x:DataType` when the binding contract supports compiled bindings. Do not
  invent a concrete design-time type when consumers intentionally bind through
  an interface or a dynamic contract.
- Choose `Design.DataContext`, `Design.PreviewWith`, or no preview from the
  surrounding file type and repository precedent. A preview is not mandatory
  for every AXAML edit.
- Register a new style or theme file in the style/resource graph that actually
  owns it. Do not assume every application uses `App.axaml` or a root
  `Styles.axaml`.
- Prefer existing resources and semantic classes over local visual literals.
  When resolution is unclear, inspect the resource graph; use
  `scripts/avalonia_style_probe.sh` for an ambiguous styling change rather than
  as ceremony for unrelated edits.
- Keep ViewModels independent of Avalonia where the repository's architecture
  requires it. Keep view-only interactions in the view or established behavior
  layer.

## Read detailed guidance only when needed

- Reactive UI and DynamicData decisions:
  [avalonia-reactive-rules.md](avalonia-reactive-rules.md)
- Existing Zafiro/Rx helpers:
  [zafiro-shortcuts.md](zafiro-shortcuts.md)
- Reusable ViewModel patterns:
  [patterns.md](patterns.md)
- Broader technical guidance:
  [core-technical-skills.md](core-technical-skills.md)
- Hierarchical shell work:
  [references/hierarchical-shell.md](references/hierarchical-shell.md)
- Xaml.Behaviors lookup:
  [references/xaml-behaviors-catalog.md](references/xaml-behaviors-catalog.md)

Load only the reference that matches the decision at hand.

## Testing and validation

Match proof to observable risk:

- C# behavior: focused behavioral test when the behavior changed.
- Bindings/resources: compiled build and focused runtime inspection.
- Visual layout or interaction: runtime/MCP validation when available.
- Structural cleanup with unchanged behavior: affected build/tests; do not add a
  reflection or markup-shape test merely to record the edit.

Inspect the final diff for redundant attributes, invented abstractions, package
changes, and unrelated formatting. New packages, tools, SDKs, project
references, commits, and publication require the authority provided by the
user and repository instructions; this skill supplies none of it.

## Completion

Complete the task only when the result follows the verified local pattern, the
changed UI behavior is demonstrated at the appropriate seam, and no generic
Zafiro preference has widened the requested scope.
