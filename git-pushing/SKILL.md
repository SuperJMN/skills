---
name: git-pushing
description: Safely publish local git work by auditing the worktree, committing intended changes when needed, pushing the correct branch or repositories, and verifying remote alignment. Use when the user asks to push, commit and push, save work to GitHub/remote, publish changes, preserve work remotely, or says phrases like "empuja todo", "mete push", "push changes", "commit and push", or "push this".
---

# Git Publication Workflow

Use this skill when the user wants local git state preserved or published remotely. Treat publishing as a workflow with inspection and verification, not as a blind `git add . && git push`.

## When to Use

Activate when the user:

- Explicitly asks to push changes ("push this", "commit and push")
- Mentions saving work to remote ("save to github", "push to remote")
- Asks to preserve current work remotely ("no quiero que se pierda")
- Says Spanish variants such as "empuja todo", "mete push", "empuja los cambios"
- Completes a feature and clearly wants it published

Do not activate for a local checkpoint request unless the user also asks to push. If the user asks to commit before continuing, make the local commit and stop there unless they mention a remote.

## Core Rules

- Inspect before staging: run `git status --short --branch` and review the diff shape before committing.
- Respect repo-specific instructions, submodule boundaries, and publication order. If a submodule or sibling dependency changed, publish that repository first, then commit the parent pointer.
- Preserve unrelated user work. If the dirty tree contains unrelated or surprising changes and the user did not say "all/everything", ask before including them.
- If the tree is clean but commits are ahead of upstream, push directly. Do not force a new commit.
- If the tree is clean and already aligned with upstream, verify and report that there was nothing to push.
- Never use destructive cleanup commands as part of this workflow unless explicitly requested.
- Always verify the final remote state.

## Workflow

1. Find the repo root and inspect state:

```bash
git rev-parse --show-toplevel
git status --short --branch
git diff --stat
```

2. If submodules are present, inspect them before committing the parent:

```bash
git submodule status --recursive
git submodule foreach --recursive 'git status --short --branch'
```

3. Validate the change if validation is reasonable for the repo and the work just completed. Prefer the repo's established checks.

4. Commit if there are intended local changes:

```bash
git add -A :/
git commit -m "feat: describe the change"
```

If the worktree is clean, skip the commit step.

5. Push the branch:

```bash
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
git push
```

If there is no upstream yet:

```bash
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
```

6. Verify after pushing:

```bash
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
git rev-parse HEAD
git ls-remote origin "refs/heads/$(git rev-parse --abbrev-ref HEAD)"
```

The ahead/behind count should be `0 0` for a fully aligned branch. If the upstream remote or ref is not `origin/<branch>`, adjust the `git ls-remote` command to match the configured upstream.

## Commit Messages

Use a concise conventional commit message that describes the actual change:

- `feat: add battle playback sync markers`
- `fix: preserve appimage icon metadata`
- `docs: update deployment handoff`
- `chore: publish current work`

Avoid generic messages like `chore: update code` unless the user only asked for a preservation commit and the diff is broad.

## Failure Handling

- If `origin` is missing, inspect remotes and either create/configure the remote if the user requested first publication, or ask which remote to use.
- If the branch has no upstream, push with `-u origin <branch>`.
- If the push is rejected, fetch and inspect divergence before rebasing or merging.
- If verification fails, do not claim the work is published; report the exact blocker and current local/remote state.
