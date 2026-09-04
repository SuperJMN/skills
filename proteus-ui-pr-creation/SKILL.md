---
name: proteus-ui-pr-creation
description: Write as jmnquantumsi in QuantumSi/proteus-ui, and create or update pull requests on their behalf. Use for any proteus-ui text published in their name, including PR summaries, review replies and comment threads, and Jira comments and ticket descriptions on the JPUI project.
---

# Proteus UI PR creation

Open a `QuantumSi/proteus-ui` pull request as **jmnquantumsi**, with a summary
in jmnquantumsi's **voice**. Do the account, review-conventions, and validation
legwork yourself so only the engineering is left.

## Fix the identity

`gh` may hold several accounts. The PR must be created as **jmnquantumsi**, and
branch commits must use an accepted company identity, never the personal
`SuperJMN` identity.

1. Run `gh auth status`; confirm `jmnquantumsi` is present and record the account
   that was active before this workflow.
2. If necessary, run `gh auth switch --user jmnquantumsi`, then re-check before
   any GitHub mutation.
3. Inspect the repository-local `user.name` and `user.email`, plus every branch
   commit with `git log --format='%an <%ae>' origin/main..HEAD`. Accept the
   repository's configured company/noreply identity and established company
   identities; reject a personal `SuperJMN` author.
4. If an existing commit has the wrong author, report it. Rewriting commit
   authors or pushed history requires explicit authorization; do not amend
   automatically as part of opening the PR.

Done when: the active `gh` account is `jmnquantumsi`, and no branch commit uses
the personal identity.

## Audit against the repo review conventions

Before validating or pushing, run the branch through the
**proteus-ui-review-conventions** skill (its
`references/reviewer-conventions.md` is the source of truth). This is the
"smell of a well-made PR" self-check, so review comments stay on substance.

Cover at least: comment and comma hygiene (single-line `//` with no trailing
period, no dangling commas), member ordering, XML docs on any branch-added
public API, design tokens over hard-coded visual values, interface-contract
docs, project and dependency boundaries (no new external or production-to-
production references), and diff scope (only this ticket).

Fix every Must Fix yourself with the smallest diff before moving on.

Done when: the branch passes the review conventions with no open Must Fix.

## Land the branch green

Open a PR only on a validated branch. From the repo root, sized to the change:

```bash
DOTNET_ENVIRONMENT=Testing dotnet build Proteus.Ui.sln
DOTNET_ENVIRONMENT=Testing dotnet test Proteus.Ui.sln --no-build   # --filter to narrow
dotnet format Proteus.Ui.sln --verify-no-changes --no-restore
git diff --check
```

Then inspect and push:

- `git status --short --branch` and `git log --oneline origin/main..HEAD`.
- An unpushed branch is safe to amend; once pushed, keep history as is unless the
  user asks to rewrite it.
- `git push -u origin <branch>`.

Done when: build clean, targeted tests green, format and diff-check clean, branch
pushed.

## Base and title

- Base on `main` unless the user names another base.
- Title `JPUI-<NN> <short imperative description>`, matching the ticket prefix
  already on the branch (e.g. `JPUI-74 Route failed run-start to consumables
  removal flow`).

## Write the summary in jmnquantumsi's voice

Write the summary in jmnquantumsi's voice, and use the same plain B2-level
register for any code comment you touch. Match the annotated model in
[references/pr-voice.md](references/pr-voice.md): a terse opening sentence, plain
prose in short paragraphs (no Markdown section headers), **bold** for types and
workflow states, `backticks` for code symbols, and a closing paragraph naming
what is deliberately left out. First person, everyday words, keyboard
punctuation only (no em-dash, no semicolon).

Friendly but technical. No idioms, since the readers are an international team.
When a choice can trap a reviewer, say it in the paragraph where it belongs and
name the consequence. Never under a label or a banner: a warning in a fixed
block becomes a template and stops being read.

Keep it high level and brief, the kind of summary someone writes in three to
five minutes. Say what the change does and why the shape of it is what it is.
Leave the implementation to the diff: no signatures, no call sequences, no
walk-through of the classes involved. When a decision needs deep justification,
that belongs in a review reply or the ticket, not in the summary.

No numbers about the work itself: no test counts, no file or line counts, no
percentages, no warning tallies. Do not close with a validation summary either.
Green build, passing tests, and a clean `dotnet format` are the assumed baseline
for any PR, so restating them adds nothing.

Write the body to a temp file, then create — or, to restyle an existing PR, edit.
Keep each paragraph on a single line in that file, with a blank line between
paragraphs. GitHub turns every newline inside a paragraph into a visible line
break, so a body wrapped at 80 columns renders with ragged breaks down the page.

```bash
gh pr create --base main --head <branch> --title "JPUI-<NN> <title>" --body-file /tmp/pr-body.md
gh pr edit <NN> --body-file /tmp/pr-body.md   # rewrite an existing summary instead
```

Verify and clean up:

```bash
gh pr view <NN> --json number,title,author,url,baseRefName,headRefName
rm -f /tmp/pr-body.md
```

After verification, restore the previously active `gh` account when it was not
`jmnquantumsi`, then confirm the switch. Done when: the PR exists with
`author.login` `jmnquantumsi`, base `main`, and a body that matches the voice,
with the caller's prior GitHub account state restored.
