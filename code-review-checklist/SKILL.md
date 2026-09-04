---
name: code-review-checklist
description: Use only when the user explicitly asks for a broad checklist-based audit spanning several risk areas such as correctness, security, performance, and maintainability. For ordinary branch or PR review, prefer the repository-specific review skill or `code-review`.
---

# Risk-based code review checklist

Use the checklist to direct evidence gathering, not to manufacture findings.
Repository standards and the originating specification outrank generic advice.

## Establish scope

1. Pin the base, diff, and complete set of changed files.
2. Read the issue, specification, or requested behavior.
3. Read repository review instructions and relevant architecture decisions.
4. Separate changed behavior from inherited code.
5. Select only the risk areas the diff can actually affect.

If the contract or fixed point is missing but can be discovered from the
repository or tracker, discover it. Ask only when a material choice remains.

## Review by applicable risk

### Correctness

- Trace changed inputs, outputs, state transitions, error paths, and lifetimes.
- Reproduce a claimed bug or exercise the changed path when practical.
- Compare behavior with the specification and functional baseline.

### Security

Review only relevant trust boundaries: authentication, authorization, secrets,
untrusted input, serialization, filesystem/network access, and dependency
changes. Tie every finding to a concrete exploit or policy violation.

### Performance

Review only changed hot paths or scale-sensitive operations. Require a
measurement, complexity argument, query plan, allocation path, or other
specific evidence; avoid speculative micro-optimization.

### Maintainability and architecture

- Check repository conventions, dependency direction, public contracts, and
  scope.
- Flag duplication or abstraction only when it creates a demonstrated change
  or understanding cost.
- Keep beneficial but scope-expanding redesigns as follow-ups, not blockers.

### Tests and validation

- Determine whether changed observable behavior is covered at a stable seam.
- Do not demand a new test merely because production code changed.
- Treat reflection, snapshots, mocks, and markup-shape assertions as justified
  only when they protect the actual durable contract.
- Verify the narrowest relevant gates and distinguish new failures from
  inherited ones.

### Documentation and dependencies

Review documentation only where a public contract or user workflow changed.
Treat new packages, tools, SDKs, and project edges according to repository
policy and explicit user authority.

## Findings

Report only actionable findings. Each finding must include:

- severity;
- exact file and location;
- violated requirement or concrete consequence;
- evidence showing the diff caused it;
- the smallest appropriate correction.

Do not emit generic checklist reminders, praise, style preferences already
enforced by tooling, or hypothetical risks without evidence. Keep unrelated
improvements separate.

## Completion

Complete the review when every changed file is accounted for, every applicable
risk area has evidence or an explicit not-applicable result, and the report
contains no checklist noise.
