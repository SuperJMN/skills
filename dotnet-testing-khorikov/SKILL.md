---
name: dotnet-testing-khorikov
description: Use when writing or reviewing .NET tests and deciding between unit vs integration, handling shared dependencies, or choosing when to use test doubles
---

# .NET Testing (Khorikov Principles)

## Overview

Translate Khorikov's unit testing principles into a pragmatic .NET workflow that keeps tests stable, fast, and meaningful.

**Defaults for this repo:** xUnit + FluentAssertions, output-based tests, minimal mocks.

## When to Use

- Writing new tests in .NET (C#)
- Refactoring code for testability
- Debating unit vs integration scope
- Unsure whether to mock a dependency

**REQUIRED SUB-SKILL:** test-driven-development (use TDD whenever possible)

## Core Principles

- **Unit tests**: Verify business behavior, are fast, deterministic, and have no shared dependencies.
- **Integration tests**: Verify collaboration with shared dependencies (DB, file system, network, clock).
- **Prefer output-based tests**: Assert on outputs/state, not on internal calls.
- **Use interaction-based tests sparingly**: Only for side-effect-only collaborators (notifications, logging, message bus).
- **Avoid mocking types you don't own**: Use real implementations or thin adapters at boundaries.
- **Keep domain logic pure**: Push I/O and infrastructure to edges (Humble Object, Ports & Adapters).
- **Triangulate when needed**: If the first test feels too narrow or complex, add a second/third test with different inputs to force generalization.

## Decision Guide

- **Is there a shared dependency involved?** Use an integration test.
- **Is the dependency a pure in-memory collaborator you control?** Unit test with a fake or stub.
- **Is the collaborator only about side effects (no meaningful output)?** Mock and assert interaction.
- **Are you testing a UI class directly?** Move logic into a ViewModel or service and test that instead.

## Test Structure

- **AAA**: Arrange, Act, Assert.
- **Name tests by behavior**: `Method_WhenCondition_ShouldOutcome`.
- **One reason to fail**: Keep each test focused on a single behavior.
- **One semantic assert per test**: Prefer a single, expressive assertion (e.g., `result.Should().BeEquivalentTo(expected)`).

## TDD and Triangulation

- Use TDD whenever possible (see required sub-skill).
- If the first test is too narrow or complex, add 2-3 tests with different inputs to force generalization.
- Triangulation can be done with separate tests or a single `[Theory]` with multiple `[InlineData]`.

## Examples (xUnit + FluentAssertions)

Output-based unit test:

```csharp
public sealed class PriceCalculatorTests
{
    [Fact]
    public void Calculate_WhenNoDiscount_ShouldReturnSubtotal()
    {
        // Arrange
        var calc = new PriceCalculator();
        var order = new Order(subtotal: 100m, discountPercent: 0);

        // Act
        var result = calc.Calculate(order);

        // Assert
        result.Should().Be(100m);
    }
}
```

Triangulation example (three cases):

```csharp
public sealed class TaxCalculatorTests
{
    [Theory]
    [InlineData(100, 0, 100)]
    [InlineData(100, 10, 110)]
    [InlineData(200, 10, 220)]
    public void Calculate_ShouldApplyRate(decimal amount, decimal ratePercent, decimal expected)
    {
        // Arrange
        var calc = new TaxCalculator();

        // Act
        var result = calc.Calculate(amount, ratePercent);

        // Assert
        result.Should().Be(expected);
    }
}
```

Interaction-based test (rare, side-effect-only):

```csharp
public sealed class ReceiptSenderTests
{
    [Fact]
    public void Send_WhenReceiptGenerated_ShouldNotify()
    {
        // Arrange
        var notifier = new Moq.Mock<INotificationGateway>();
        var sender = new ReceiptSender(notifier.Object);

        // Act
        sender.Send("user@example.com", "receipt-123");

        // Assert
        notifier.Verify(x => x.Notify("user@example.com", "receipt-123"), Moq.Times.Once);
    }
}
```

## Minimal .NET Setup

- **Run tests**: `dotnet test`
- **Target a project**: `dotnet test path/to/Project.Tests.csproj`
- **Preferred frameworks**: xUnit + FluentAssertions.

## Anti-Patterns

- Verifying private methods or internal call sequences.
- Heavy mocking of infrastructure or third-party libraries.
- Unit tests that hit the database or file system.
- Tests that are slow or flaky due to time, randomness, or network.
- Multiple unrelated asserts in one test.

## Adoption Path (No Existing Tests)

- Start with 2-3 critical domain behaviors as unit tests.
- Add 1-2 integration tests covering key infrastructure interactions.
- Keep integration tests isolated and clearly labeled.
