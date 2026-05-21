# Unit vs Integration Examples

## Unit Test Examples

Use unit tests for deterministic in-memory behavior.

Examples:

- `Order.Confirm()` changes order status according to business rules.
- `DiscountPolicy.CalculateFor(customer)` returns the right discount.
- `Subscription.IsExpired(today)` evaluates expiration.
- `Money.Add()` handles currency mismatch.
- `BattleDamageCalculator.Calculate()` applies STAB, type effectiveness, and modifiers.

These tests should use real domain objects and pure services.

## Integration Test Examples

Use integration tests when the behavior depends on infrastructure or process boundaries.

Examples:

- `CustomerRepository.Save()` persists and reloads an aggregate.
- EF Core mapping correctly stores owned value objects.
- A JSON converter serializes and deserializes a domain event.
- Dependency injection resolves an application service with its real dependencies.
- An HTTP adapter maps provider responses and errors into application results.
- A file-based package store writes, reads, and deletes packages in an isolated temp directory.

## End-to-End Test Examples

Use end-to-end tests only for critical workflows whose value justifies cost and brittleness.

Examples:

- User submits an order and receives a confirmation.
- A deployment request reaches a worker and produces a release artifact.
- A UI flow exercises navigation, validation, and persistence together.

Keep end-to-end suites small. They are not a replacement for unit and integration tests.

## Ambiguous Cases

### Repository used only to retrieve data

If testing an application service and the repository only provides input, use a stub or fake. Do not verify `GetById()` unless the retrieval itself is the behavior.

### Repository persistence

If testing the repository itself, use an integration test with a real managed dependency when practical.

### Clock

Do not use the real clock in unit tests. Pass an explicit date/time, use `TimeProvider`, or use a fake clock.

### File system

A unit test should not touch the real file system. A focused integration test may use an isolated temporary directory.

### Message bus

If the message bus is external or shared, wrap it behind an adapter and mock/fake the adapter. Verify the published integration event only if publishing is an externally visible behavior.
