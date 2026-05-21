# Review Checklist

Use this checklist when reviewing test additions or refactors.

## Behavior

- Does the test verify observable behavior?
- Is the behavior named in domain language?
- Would a business/domain person understand the scenario?
- Is the test protecting a meaningful regression?

## Scope

- Is the test really unit, integration, or end-to-end?
- Does a unit test avoid database, file system, network, real clock, queues, and shared mutable state?
- Does an integration test use realistic infrastructure where the mapping/integration matters?
- Is an end-to-end test justified by workflow importance?

## Dependencies

- Are in-memory domain collaborators real where practical?
- Are managed dependencies tested with real instances in integration tests?
- Are unmanaged dependencies behind adapters owned by the application?
- Are volatile inputs controlled?

## Mocks

- Is each mock verifying an external boundary interaction?
- Is any mock verifying an internal call sequence?
- Could a fake or real collaborator make the test less brittle?
- Are stubs used only to provide input?

## Maintainability

- Is setup relevant and readable?
- Is there one clear reason for failure?
- Is there one Act section?
- Are assertions semantic rather than noisy?
- Would the test survive a valid refactoring?
- Has the narrowest relevant `dotnet test` command been run?
