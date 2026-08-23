---
name: git-pushing
description: Safely publish local Git work by auditing scope, identity, remote ownership, staged changes, and final remote alignment. Use when the user asks to commit and push, push changes, save work to a remote, or otherwise publish the current work; a local-only commit, PR, merge, issue closure, or cleanup remains a separate action unless explicitly requested.
---

# Git publication

Publish only the intended work to the intended branch and remote, then prove that
the remote contains the exact local commit.

## Authorization boundary

- A request to push authorizes the commits needed to publish the intended local
  changes, unless the user explicitly limits the request to already committed
  work.
- A local checkpoint or commit request stops locally unless publication is also
  requested.
- Opening or updating a PR, merging, closing an issue, deleting branches or
  worktrees, and force-pushing require their own explicit authorization.
- Preserve unrelated user work. "Push all/everything" includes all audited
  changes in the repository; otherwise stage only paths that belong to the
  requested work.

## 1. Audit the publication target

Read repository instructions first. Resolve the repository root and inspect the
branch, worktree, remotes, upstream, author identity, and change shape:

```bash
git rev-parse --show-toplevel
git status --short --branch
git symbolic-ref --quiet --short HEAD
git remote -v
git config --get user.name
git config --get user.email
git diff --stat
git diff --check
```

Complete this step only when all of the following are known:

- the branch is attached and is the branch the user intends to publish;
- the remote URL and owner match the repository and any account/identity rules;
- the configured commit identity is appropriate for that repository;
- every dirty path is classified as intended, explicitly included by "all", or
  unrelated and excluded.

If identity, ownership, branch, or scope is ambiguous or mismatched, stop before
staging or pushing and ask for the missing authority. Do not repair identity or
remote configuration implicitly.

If submodules are present, inspect their branches and dirty state. Publish an
intentionally changed submodule or sibling repository before committing the
parent pointer.

## 2. Validate and stage the exact scope

Run the repository's established validation appropriate to the change. A push
request does not justify weakening or bypassing a known publication gate.

Stage explicit paths by default:

```bash
git add -- path/to/intended-file path/to/other-file
```

Use repository-wide staging only after the audit established that every change
is intended or the user explicitly requested all audited work:

```bash
git add -A :/
```

Review the actual index, not merely the pre-staging worktree:

```bash
git status --short
git diff --cached --name-status
git diff --cached --stat
git diff --cached --check
```

Inspect the staged content path by path with bounded diff reads. Complete this
step only when the staged diff contains every intended change, no unrelated
change, and no credential or generated artifact that should remain local.

## 3. Commit only when needed

If intended local changes are staged, create a concise message describing the
actual change:

```bash
git commit -m "<type>: <concise summary>"
```

If the worktree is clean and commits are already ahead of upstream, publish
those commits without manufacturing another commit. If local and upstream state
are already aligned, skip mutation and proceed to verification.

## 4. Push the resolved branch and remote

Use the configured upstream when it exists:


```bash
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
git push
```

If no upstream exists, inspect the available remotes and select one only when
repository instructions or the user's request makes it unambiguous:

```bash
git push -u <remote> "$(git symbolic-ref --quiet --short HEAD)"
```

If a push is rejected, fetch and inspect the divergence. Rebasing, merging,
rewriting history, or force-pushing is a new decision; report the evidence and
obtain authorization when the requested publication cannot be completed by a
normal push.

## 5. Prove remote alignment

Resolve the actual upstream and verify both graph alignment and the remote ref:

```bash
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
git rev-parse HEAD
git rev-parse '@{u}'
git ls-remote <upstream-remote> 'refs/heads/<upstream-branch>'
```

Publication is complete only when the ahead/behind count is `0 0`, local `HEAD`,
the upstream tracking ref, and `ls-remote` all identify the same commit. Report
the branch, remote, commit, validation performed, and any intentionally excluded
local changes. If these checks disagree, report the blocker rather than claiming
success.
