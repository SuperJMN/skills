# Navigation & Sections

Zafiro provides powerful abstractions for managing application-wide navigation and modular UI sections.

## Navigation with INavigator

The `INavigator` interface is used to switch between different views or viewmodels.

```csharp
public class MyViewModel(INavigator navigator)
{
    public async Task GoToDetails()
    {
        await navigator.Navigate(() => new DetailsViewModel());
    }
}
```

## ViewModel Lifecycle — CRITICAL RULE

**`INavigator` always disposes `IDisposable` content when navigating away.** This is a deliberate design decision in Zafiro.Avalonia.

### Principles

- **VMs are born and die with navigation**: a VM is created when navigated to and disposed when the user navigates away. There is no `OnNavigatedBack` / `OnNavigatedFrom` / mutation-on-return pattern.
- **Never implement `IDisposable` on a VM that must survive back-navigation.** If the navigator disposes the VM on forward navigation, any subscriptions, commands or state inside it are dead when the user returns — even if the same instance is reused via a `() => vm` factory closure.
- **State hoisting**: if state must persist across navigation (e.g. a counter, a loaded list), lift it out of the VM into a service, controller, or parent VM that outlives the navigation. The child VM reads from that state on construction.
- `ReactiveCommand` instances bound via `WhenAnyValue` do **not** need a `CompositeDisposable` — they are self-referential and collected with the VM. Only add explicit disposal for external subscriptions (timers, event handlers, etc.).

### Correct pattern — stateless VM (most common)

```csharp
// ✅ No IDisposable. State lives in AdventureController (injected service).
public class AdventureModeViewModel : ReactiveObject
{
    public AdventureModeViewModel(AdventureController controller, INavigator navigator)
    {
        EnterStepCommand = ReactiveCommand.CreateFromTask(
            () => navigator.Go(() => new BattleViewModel(controller)),
            this.WhenAnyValue(x => x.CanEnter));
    }
}
```

### Correct pattern — persisting state across navigation

```csharp
// ✅ State lives in a controller/service. VM reads it on construction.
public class HomeViewModel : ReactiveObject
{
    public async Task GoToAdventure()
    {
        // Do NOT capture 'vm' and reuse it — it will be disposed on forward nav.
        await navigator.Go(() => new AdventureModeViewModel(adventureController, navigator));
    }
}
```

### Anti-pattern — DO NOT DO THIS

```csharp
// ❌ VM implements IDisposable AND is reused after forward navigation
public class MyViewModel : ReactiveObject, IDisposable
{
    private readonly CompositeDisposable disposables = new();

    public MyViewModel(INavigator navigator)
    {
        var cmd = ReactiveCommand.CreateFromTask(DoWork,
            this.WhenAnyValue(x => x.CanDo));
        disposables.Add(cmd);  // ❌ will be disposed on forward nav; cmd dead on return
        MyCommand = cmd;
    }

    public void Dispose() => disposables.Dispose();
}

// In parent VM:
var vm = new MyViewModel(navigator);
await navigator.Go(() => vm);  // ❌ vm is disposed here; reuse on GoBack is broken
```

## UI Sections

Sections are modular parts of the UI (like tabs or sidebar items) that can be automatically registered.

### The [Section] Attribute

ViewModels intended to be sections should be marked with the `[Section]` attribute.

```csharp
[Section("Wallet", icon: "fa-wallet")]
public class WalletSectionViewModel : IWalletSectionViewModel
{
    // ...
}
```

### Automatic Registration

In the `CompositionRoot`, sections can be automatically registered:

```csharp
services.AddAnnotatedSections(logger);
services.AddSectionsFromAttributes(logger);
```

### Switching Sections

You can switch the current active section via the `IShellViewModel`:

```csharp
shellViewModel.SetSection("Browse");
```

> [!IMPORTANT]
> The `icon` parameter in the `[Section]` attribute supports FontAwesome icons (e.g., `fa-home`) when configured with `ProjektankerIconControlProvider`.
