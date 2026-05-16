# ViewModels & Commands

In a Zafiro-based application, ViewModels should be functional, reactive, and resilient. This skill follows the [General C# Development Standards](../csharp-development-zafiro/SKILL.md) for naming and functional patterns.

## Reactive ViewModels

Use `ReactiveObject` as the base class. Properties should be defined using the `[Reactive]` attribute (from ReactiveUI.SourceGenerators) for brevity.

```csharp
public partial class MyViewModel : ReactiveObject
{
    [Reactive] private string name;
    [Reactive] private bool isBusy;
}
```

### Observation and Transformation

Use `WhenAnyValue` to react to property changes:

```csharp
this.WhenAnyValue(x => x.Name)
    .Select(name => !string.IsNullOrEmpty(name))
    .ToPropertyEx(this, x => x.CanSubmit);
```

For read-only state derived from other properties, prefer exposing `IObservable<T>` directly and project it with `Select`:

```csharp
public IObservable<IReadOnlyList<PeriodOption>> DurationPresets =>
    this.WhenAnyValue(x => x.DurationUnit)
        .Select(unit => unit == TimeSpan.FromDays(7)
            ? weeklyPresets
            : monthlyPresets);
```

Avoid mutating a derived property from `Subscribe` or `Update*` helper methods when the value can be expressed as a projection.

## Enhanced Commands

Zafiro uses `IEnhancedCommand`, which extends `ICommand` and `IReactiveCommand` with additional metadata like `Name` and `Text`.

### Creating a Command

Use `ReactiveCommand.Create` or `ReactiveCommand.CreateFromTask` and then `Enhance()` it.

```csharp
public IEnhancedCommand Submit { get; }

public MyViewModel()
{
    Submit = ReactiveCommand.CreateFromTask(OnSubmit, canSubmit)
        .Enhance(text: "Submit Data", name: "SubmitCommand");
}
```

### Error Handling

Use `HandleErrorsWith` to automatically channel command errors to the `NotificationService`.

```csharp
Submit.HandleErrorsWith(uiServices.NotificationService, "Submission Failed")
    .DisposeWith(disposable);
```

### Prerequisite-Gated Commands

When a command needs a UI/runtime prerequisite before it can work, do not let the command call the downstream service directly and hope the dependency is ready. Model the prerequisite as a small context service that returns the ready dependency:

```csharp
public interface IConnectedClientContext
{
    Task<Maybe<Result<ApiClient>>> Require();
}
```

Use this shape when the prerequisite can be missing, stale, or user-driven: wallet loaded, API client connected, authenticated session, selected workspace, etc.

- `Maybe.None`: the user cancelled the prerequisite flow. This is not an error and should not notify.
- `Result.Failure`: the prerequisite attempt failed. This should flow into `HandleErrorsWith`.
- `Result.Success<TReady>`: the command receives a ready-to-use dependency, not a boolean flag.

The context owns prerequisite orchestration. It should first reuse/validate stored state, then start the UI flow only if needed. For concurrent refreshes, guard the flow with a single gate so multiple commands do not open duplicate dialogs.

```csharp
private async Task<Maybe<Result>> Refresh()
{
    return await clientContext
        .Require()
        .Bind(async client =>
        {
            var items = await client.GetItems();
            Apply(items);
        });
}
```

For commands returning `Maybe<Result>` or `Maybe<Result<T>>`, expose a small adapter that drops cancellations before error handling:

```csharp
var refresh = ReactiveCommand.CreateFromTask(Refresh);
refresh.Results()
    .HandleErrorsWith(notificationService, Maybe.From("Cannot refresh"))
    .DisposeWith(disposables);
RefreshCommand = refresh.Enhance("Refresh");
```

Implementation checklist:

- Put UI prompting in a dedicated flow service (`IConnectionFlow`, `IWalletFlow`, etc.) injected into the context, not inside the data-loading ViewModel.
- Keep the ViewModel command body as a pure pipeline: `Require().Bind(...)`.
- Validate existing state before prompting. If a stored token/wallet/session is invalid, clear stale state and rerun the flow.
- Keep `None` silent; only failed `Result`s reach notifications.
- Add regression tests for already-satisfied prerequisite, cancellation, failed prerequisite, stale stored state, and command body not executing before success.

## Disposables

Always use a `CompositeDisposable` to manage subscriptions and command lifetimes.

```csharp
public class MyViewModel : ReactiveObject, IDisposable
{
    private readonly CompositeDisposable disposables = new();

    public void Dispose() => disposables.Dispose();
}
```

> [!TIP]
> Use `.DisposeWith(disposables)` on any observable subscription or command to ensure proper cleanup.
