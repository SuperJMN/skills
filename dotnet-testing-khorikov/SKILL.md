---
name: dotnet-testing-khorikov
description: Use when writing or reviewing .NET/C# tests, especially unit vs integration scope, whether to mock/stub/fake/use real dependencies, or how to keep tests focused on observable behavior using Khorikov-style principles. Do not use for generic test framework syntax only.
---

# .NET Testing, Khorikov Style

## Purpose

Use this skill to write, review, or refactor .NET tests according to Vladimir Khorikov's testing principles: high regression protection, resistance to refactoring, fast feedback, and maintainability.

This skill is not about maximizing coverage or isolating every class. It is about testing meaningful observable behavior with the least brittle test that gives confidence.

Default stack, unless the repository already differs: xUnit, FluentAssertions, and Moq only when a mock is justified.

## Use When

- Adding, fixing, or reviewing .NET/C# tests.
- Choosing unit vs integration vs end-to-end scope.
- Deciding whether to use a mock, stub, fake, dummy, or real implementation.
- Testing code that touches database, file system, network, queues, clock, randomness, APIs, or framework infrastructure.
- Refactoring production code just enough to make behavior testable.

## Do Not Use When

- The task is only about test framework syntax or package installation.
- The user explicitly asks for another testing philosophy.
- The change is purely non-.NET.
- Existing repository instructions conflict with this skill. In that case, follow repository instructions and apply these principles only where compatible.

## Agent Workflow

1. Inspect existing test projects, naming, fixtures, builders, assertions, and packages.
2. Identify the behavior under test in domain terms.
3. Classify the test: unit, integration, or end-to-end.
4. Classify dependencies: in-memory, managed, unmanaged, or volatile.
5. Prefer real in-memory collaborators owned by the codebase.
6. Use mocks only for unmanaged external boundaries or externally visible side effects.
7. Write the smallest valuable test that protects meaningful behavior.
8. Run the narrowest relevant `dotnet test` command first.
9. If tests fail, fix the production code or the test according to the intended behavior.
10. Report what was tested, which scope was chosen, and why mocks were or were not used.

## Repository Awareness

- Reuse existing test style when it is reasonable.
- Do not introduce new test packages if the repo already has an established alternative.
- Do not rewrite a test suite just because it is not ideal.
- Do not redesign production code just to fit this skill.
- Prefer focused local improvements over broad architecture changes.
- If legacy design prevents ideal tests, add the best incremental test that improves confidence without making the design worse.

## Core Principles

- Test observable behavior, not implementation details.
- A unit is a unit of behavior, not necessarily a single class.
- Unit tests must be fast, deterministic, and isolated from other tests.
- Unit tests must not touch shared mutable state or out-of-process dependencies.
- Prefer output-based tests when possible.
- State-based tests are valid when they verify observable state.
- Communication-based tests are rare and should verify true boundary interactions.
- Prefer real deterministic in-memory collaborators owned by the codebase.
- Do not mock domain objects, value objects, entities, pure services, or internal collaborators just to isolate a class.
- Avoid mocking third-party types directly. Wrap them behind adapters owned by the application.
- Keep domain logic pure when practical. Push I/O, frameworks, persistence, time, and networking to edges.
- Control volatile inputs such as time, randomness, GUIDs, current user, environment variables, and machine-specific paths.

## Decision Rules

### Unit test

Use a unit test when the behavior is deterministic and entirely in-memory.

Allowed in unit tests:

- Domain entities and value objects.
- Pure domain services.
- In-memory collaborators owned by the codebase.
- Stubs or fakes that provide indirect input or control volatility.

Avoid in unit tests:

- Database.
- File system.
- Network.
- Message queues.
- Real clock.
- Uncontrolled randomness.
- Framework infrastructure.
- Shared mutable state.

### Integration test

Use an integration test when behavior crosses a process boundary or depends on infrastructure.

Good integration test targets:

- Database mapping and queries.
- Repository persistence behavior.
- File system interaction.
- HTTP adapters.
- Serialization.
- Dependency injection wiring.
- Authentication or authorization infrastructure.
- Message publishing adapters.
- Framework integration.

### Managed dependency

A managed dependency is an out-of-process dependency controlled exclusively by this application, such as its own database or owned file store.

For managed dependencies, prefer real instances in integration tests. Isolate and reset state between tests.

### Unmanaged dependency

An unmanaged dependency is an external system whose interactions are visible outside the application boundary, such as SMTP, payment gateway, third-party API, external message bus, external notification service, or business audit sink.

For unmanaged dependencies, use an adapter/interface owned by the application. Mock or fake that adapter and verify only externally visible communication.

## Test Doubles

- Dummy: passed only because the signature requires it. Do not use it in assertions.
- Stub: provides indirect input. Do not verify calls against stubs.
- Fake: lightweight working implementation, often better than a mock when it keeps tests behavior-focused.
- Mock: use only when the interaction itself is the observable behavior.

Good mock candidates:

- Email sender.
- Notification gateway.
- Payment gateway adapter.
- External API adapter.
- Integration event publisher.
- Business audit writer, when audit is a requirement.

Poor mock candidates:

- Domain services.
- Value objects.
- Entities.
- In-memory calculators.
- Repositories used only to retrieve data.
- Technical logging, unless logs are a requirement.
- Internal orchestration.

## Naming and Structure

Name tests by observable behavior using domain language.

Prefer:

```csharp
[Fact]
public void Delivery_with_a_past_date_is_invalid()
```

Avoid rigid names coupled to method names unless the repository already uses them clearly:

```csharp
[Fact]
public void IsDeliveryValid_WhenDateIsInThePast_ShouldReturnFalse()
```

Use Arrange, Act, Assert. Prefer one Act section and one semantic assertion. Multiple physical assertions are acceptable when they verify one logical outcome.

## Examples

Output-based unit test:

```csharp
public sealed class DiscountPolicyTests
{
    [Fact]
    public void Loyal_customers_receive_a_ten_percent_discount()
    {
        var customer = Customer.WithLoyaltyPoints(1_000);
        var policy = new DiscountPolicy();

        var discount = policy.CalculateFor(customer);

        discount.Should().Be(Discount.Percent(10));
    }
}
```

Use real in-memory collaborators you own:

```csharp
public sealed class OrderPricingTests
{
    [Fact]
    public void Order_total_includes_item_prices_and_tax()
    {
        var taxPolicy = new TaxPolicy(ratePercent: 21);
        var pricingService = new OrderPricingService(taxPolicy);
        var order = new Order([
            new OrderLine("book", quantity: 2, unitPrice: 10m),
            new OrderLine("pen", quantity: 1, unitPrice: 5m)
        ]);

        var total = pricingService.CalculateTotal(order);

        total.Should().Be(30.25m);
    }
}
```

Communication test for an external boundary:

```csharp
public sealed class PaymentServiceTests
{
    [Fact]
    public void Confirmed_order_is_charged_once()
    {
        var paymentGateway = new Mock<IPaymentGateway>();
        var service = new PaymentService(paymentGateway.Object);
        var order = Order.Confirmed(CustomerId.New(), Money.Eur(100m));

        service.Charge(order);

        paymentGateway.Verify(
            x => x.Charge(order.CustomerId, Money.Eur(100m)),
            Times.Once);
    }
}
```

## Verification

Run the narrowest relevant command first:

```bash
dotnet test path/to/Project.Tests.csproj --filter FullyQualifiedName~TestClassName
```

Then run the affected test project:

```bash
dotnet test path/to/Project.Tests.csproj
```

For broad changes, run:

```bash
dotnet test
```

If verification cannot run because of missing SDKs, unavailable services, or environment limits, report the exact limitation and what was checked instead.

## Definition of Done

- The test verifies observable behavior.
- The scope is justified: unit, integration, or end-to-end.
- Mocks are used only for valid boundary interactions.
- Real in-memory collaborators are preferred where appropriate.
- Volatile inputs are controlled.
- The test would survive valid refactoring.
- The relevant `dotnet test` command was run or the limitation was reported.

## References

See `references/` for deeper decision tables and examples when needed. Keep this main skill operative and short.
