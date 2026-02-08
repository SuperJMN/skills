---
name: lint-and-validate
description: Use when changes to code should be checked with linting, formatting, type checks, or static analysis before completion
---

# Lint and Validate Skill

## Overview

Run the project's configured checks after code changes to catch style, type, and static analysis issues before completion.

## When to Use

- After modifying code and before reporting work as done
- When CI fails on lint, format, type, or static analysis steps
- When asked to "lint", "format", "check", "validate", "types", or "static analysis"

## Core Loop

1. Identify the repo's configured commands.
2. Run the applicable checks for the touched ecosystem.
3. Fix issues and re-run until clean.

### Procedures by Ecosystem

#### Node.js / TypeScript
1. **Lint/Fix:** `npm run lint` or `npx eslint "path" --fix`
2. **Types:** `npm run typecheck` or `npx tsc --noEmit`
3. **Security (if used):** `npm audit --audit-level=high`

#### Python
1. **Linter (Ruff):** `ruff check "path" --fix` (Fast & Modern)
2. **Types (MyPy):** `mypy "path"`
3. **Security (if used):** `bandit -r "path" -ll`

## Error Handling
- If `lint` fails: Fix the style or syntax issues immediately.
- If `tsc` fails: Correct type mismatches before proceeding.
- If no tool is configured: Check the project root for `.eslintrc`, `tsconfig.json`, `pyproject.toml`, or `package.json` scripts and propose the minimal setup.

---
**Strict Rule:** Do not mark work as "done" without passing the applicable checks configured in the repo.

---

## Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `scripts/lint_runner.py` | Unified lint check | `python scripts/lint_runner.py <project_path>` |
| `scripts/type_coverage.py` | Type coverage analysis | `python scripts/type_coverage.py <project_path>` |
