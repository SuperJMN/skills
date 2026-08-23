# jmnquantumsi's PR voice

The model to match. Distilled from the user's own PRs, e.g.
[proteus-ui#121](https://github.com/QuantumSi/proteus-ui/pull/121).

## Annotated exemplar (PR#121)

> **Adds the General tab.**
>
> _(screenshot)_
>
> The tab needs two controls the theme did not have. **SearchableComboBox**
> covers the Figma Search Dropdown List organism, a picker whose dropdown
> narrows a long option list as the user types, and **RadioButton** covers the
> brand radio. The search field inside the dropdown is a **FloatingTextInput**
> rather than a second implementation of the same molecule.
>
> Sections now build their content through `Section.For<T>`, so the factory no
> longer takes an object, and the composition root owns the section list instead
> of **SettingsViewModel**.
>
> **IMPORTANT NOTE**: General is created with **ActivatorUtilities** so a hidden
> tab's view model is released on deactivation rather than retained by the
> container until shutdown (this would produce a memory leak).
>
> "Upgrade Software" and "Power Off" don't have command definitions yet, and the
> values on screen are placeholders because the backend does not expose the
> services the tab needs yet.

## What each move is doing

- **Opening line** — one terse standalone sentence naming the change
  ("Adds the General tab.").
- **Body paragraphs** — plain prose, short paragraphs, no section headers.
  Explains the *why* behind non-obvious choices (why a shared molecule, why the
  composition root owns the list).
- **Bold** — type names, controls, workflow states (**SearchableComboBox**,
  **SettingsViewModel**).
- **Backticks** — code symbols and API calls (`Section.For<T>`).
- **`IMPORTANT NOTE`** — optional, and rare. Use it only when a real reviewer
  trap exists, with the consequence spelled out (memory leak). Most PRs have
  none, so leave it out rather than inventing one to fill the template. Never
  more than one.
- **Closing paragraph** — what is deliberately left out: placeholders, commands
  not wired, backend services missing. Scope stays explicit. Not a validation
  report: never end with tests passing, warning counts, or `dotnet format`
  results, since all of that is taken for granted.
- **Register** — first person, matter-of-fact, screenshots for UI work.

## Language

Write like a fluent human at B2 level, not like a language model. Keep it plain
and readable, and let the writing carry the small irregularities of real prose.

- Short, direct sentences. Use a comma or a full stop where a longer sentence
  would drift. Split a long thought into two sentences.
- Everyday vocabulary. Prefer "take out" over "extract", "left inside" over
  "stranded", "set again" over "re-initialised". Skip words that read as
  polished machine output.
- Punctuation that a person types on a keyboard: comma, full stop, parentheses.
  No em-dash (—), no semicolon, no en-dash between words. The workflow arrow `→`
  stays, since it is the repo's own state-machine convention.
- No stock AI phrasing ("delve", "seamless", "leverage", "it's worth noting",
  "additionally", tidy three-item lists that all start the same way).

This register applies to everything the skill writes: the PR body, review
replies and comment threads, Jira comments, and any code comments it touches.
