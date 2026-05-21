# Test Doubles Decision Table

Use this file only when the main skill does not provide enough detail.

## Quick Rule

A test double is justified when using the real dependency would make the test slow, flaky, externally coupled, or focused on the wrong behavior. It is not justified just because the dependency is another class.

| Dependency kind | Example | Preferred test choice | Assert interaction? |
|---|---|---|---|
| Pure value object | Money, Email, DateRange | Real implementation | No |
| Domain entity | Order, Customer, Subscription | Real implementation | No |
| Pure domain service | TaxPolicy, DiscountPolicy | Real implementation | No |
| In-memory app collaborator | PricingService, RuleEvaluator | Real implementation | No |
| Volatile input | Time, random, GUID | Explicit value, fake, or provider | Usually no |
| Managed dependency | App database, owned file store | Real dependency in integration test | Usually state/output |
| Unmanaged dependency | SMTP, Stripe, third-party API | Adapter plus mock/fake | Yes, if communication is behavior |
| Technical logging | ILogger | Usually ignore | No, unless required |
| Business audit | Audit trail required by domain | Adapter plus mock/fake or integration test | Yes, if audit is behavior |

## Dummy

Use a dummy only to satisfy a signature when the dependency is irrelevant.

```csharp
var sut = new ReportFormatter(dummyClock);
```

Do not assert anything about a dummy.

## Stub

A stub returns indirect input to the system under test.

```csharp
var rates = new StubExchangeRateProvider(rate: 1.10m);
var converter = new CurrencyConverter(rates);
```

Do not verify that a stub was called. If you assert calls on a stub, it has become a mock, and the test is likely coupled to implementation details.

## Fake

A fake is a small working implementation.

Good fake examples:

- Fake clock.
- Fake ID generator.
- In-memory email gateway that records messages.
- In-memory repository for simple application-service behavior.

Use fakes when they keep the test behavior-focused and readable.

## Mock

A mock verifies communication. Use it only when the communication itself is an observable outcome.

Good:

```csharp
emailGateway.Verify(x => x.Send(to, subject, body), Times.Once);
```

Suspicious:

```csharp
validator.Verify(x => x.Validate(order), Times.Once);
repository.Verify(x => x.GetById(id), Times.Once);
calculator.Verify(x => x.Calculate(order), Times.Once);
```

The suspicious examples usually verify internal collaboration rather than externally visible behavior.
