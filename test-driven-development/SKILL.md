---
name: test-driven-development
description: Use only when the user explicitly invokes strict test-driven-development or the repository explicitly mandates red-green-refactor. Do not trigger for ordinary feature work, bug fixes, refactors, API cleanup, or requests that merely mention tests.
---

# Strict test-driven development

Apply this skill only after the invocation gate in the description is satisfied.
TDD is a tool for discovering behavior through a red-green-refactor loop, not a
universal prerequisite for changing production code.

## Preserve existing work

Never delete or rewrite existing user work merely because it was written before
a test. When joining an implementation already in progress, establish its
current state and add the narrowest useful characterization or regression test
if one is justified.

## Choose the seam

State the observable behavior and identify the closest stable public seam.
Prefer behavior that callers or users can observe. Avoid private-method tests,
reflection over implementation shape, and mocks of internal collaborators.

An API-surface assertion is appropriate only when the exact surface is itself
an explicit durable requirement. Deleting an unused overload normally needs
caller migration and compilation, not a negative reflection test.

Read [testing-anti-patterns.md](testing-anti-patterns.md) only when the test
requires mocks, fakes, or new test utilities.

## Red-green-refactor

1. **Red:** write one focused test for one behavior and run it. Confirm it fails
   for the expected missing behavior, not because of setup, syntax, or an
   unrelated defect.
2. **Green:** implement the smallest coherent production change that satisfies
   that behavior. Preserve repository conventions and existing contracts.
3. **Verify:** run the focused test and the affected existing tests.
4. **Refactor:** improve the implementation only within the requested scope,
   keeping the relevant tests green.
5. Repeat only for the next independently valuable behavior.

Do not pre-write a horizontal batch of tests for imagined behavior. Let each
vertical slice inform the next one.

## When strict TDD is a poor fit

Use proportional validation instead for:

- behavior-neutral refactors and moves;
- deletion of dead code or unused API;
- generated code, documentation, formatting, and package metadata;
- exploratory prototypes whose purpose is to discover the contract;
- visual changes whose reliable proof is runtime interaction or image evidence;
- legacy code where no stable seam exists and creating one would widen scope.

For a bug, reproduce the user's exact symptom first. Convert that reproduction
into a regression test only when the test can exercise the real failure path.

## Completion

Strict TDD is complete when every new test was observed red for the intended
reason, is green after the change, protects observable behavior at a stable
seam, and the affected existing tests still pass. Report any behavior validated
through a different proof surface.
