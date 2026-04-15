---
name: avalonia-mcp-setup
description: Install and configure Zafiro.Avalonia.Mcp for Avalonia apps. Covers the dotnet tool installation, NuGet package for the app, AppBuilder integration, and MCP client configuration (VS Code, Claude Desktop, etc). Use when user says "set up MCP", "configure MCP", "install MCP", "add MCP diagnostics", "Avalonia MCP", or wants AI-driven UI inspection/interaction for their Avalonia app.
---

# Zafiro.Avalonia.Mcp — Setup Skill

Set up the Zafiro.Avalonia.Mcp system so an AI agent can inspect, interact with, and capture screenshots/recordings of a running Avalonia UI application via the Model Context Protocol (MCP).

## Architecture Overview

The system has two components:

1. **`Zafiro.Avalonia.Mcp.AppHost`** — A NuGet library added to the Avalonia app. It starts a named-pipe server inside the app process, enabling external inspection.
2. **`Zafiro.Avalonia.Mcp.Tool`** — A .NET global tool that acts as an MCP server (stdio transport). It discovers running Avalonia apps via discovery files, connects over named pipes, and exposes 30+ MCP tools.

```
┌─────────────────┐       named pipe        ┌──────────────────────┐
│  Avalonia App    │◄──────────────────────►│  zafiro-avalonia-mcp │
│  (AppHost inside)│  zafiro-avalonia-mcp-  │  (.NET global tool)  │
│                  │  {PID}                 │                      │
└─────────────────┘                         └──────────┬───────────┘
                                                       │ stdio (JSON-RPC)
                                                       ▼
                                              ┌─────────────────┐
                                              │   MCP Client    │
                                              │ (VS Code, Claude│
                                              │  Desktop, etc.) │
                                              └─────────────────┘
```

## When to Use

Activate when the user:
- Wants to add MCP diagnostics to an Avalonia app
- Asks to "set up MCP", "install MCP", "configure MCP for Avalonia"
- Wants AI-driven UI testing, inspection, or interaction with their Avalonia app
- Mentions `Zafiro.Avalonia.Mcp` or `zafiro-avalonia-mcp`

## Prerequisites

- .NET 8.0 SDK or later (net8.0 and net10.0 are supported)
- An Avalonia 12.x application
- An MCP-capable client (VS Code with GitHub Copilot, Claude Desktop, etc.)

## Step 1 — Add AppHost to the Avalonia App

### 1.1 Install the NuGet package

In the Avalonia app's **Desktop project** (or the project containing `Program.cs` with the `AppBuilder`):

```bash
dotnet add <ProjectPath> package Zafiro.Avalonia.Mcp.AppHost
```

### 1.2 Add the `UseMcpDiagnostics()` call

In the file that builds the `AppBuilder` (typically `Program.cs`), add a single line:

```csharp
using Zafiro.Avalonia.Mcp.AppHost;

public static AppBuilder BuildAvaloniaApp()
    => AppBuilder.Configure<App>()
        .UsePlatformDetect()
        .UseMcpDiagnostics()   // ← Add this line
        .WithInterFont()
        .LogToTrace();
```

**That's all.** No other changes to the app are needed. The `UseMcpDiagnostics()` extension method hooks into `AppBuilder.AfterSetup` and starts a named-pipe diagnostic server automatically.

### 1.3 How it works internally

- On startup, the app creates a discovery file at `{TEMP}/zafiro-avalonia-mcp/{PID}.json` containing:
  ```json
  {
    "pid": 12345,
    "pipeName": "zafiro-avalonia-mcp-12345",
    "processName": "MyApp",
    "startTime": "2026-01-01T00:00:00+00:00",
    "protocolVersion": "1.0.0"
  }
  ```
- A named-pipe server listens on `zafiro-avalonia-mcp-{PID}` for incoming connections.
- The discovery file is cleaned up when the app exits.

### 1.4 Stopping diagnostics (optional)

To explicitly stop the diagnostic server (e.g., before app shutdown):

```csharp
DiagnosticExtensions.StopMcpDiagnostics();
```

## Step 2 — Install the MCP Tool

Install the .NET global tool:

```bash
dotnet tool install -g Zafiro.Avalonia.Mcp.Tool
```

To update an existing installation:

```bash
dotnet tool update -g Zafiro.Avalonia.Mcp.Tool
```

Verify it's installed:

```bash
dotnet tool list -g | grep zafiro-avalonia-mcp
```

The tool command name is **`zafiro-avalonia-mcp`**.

## Step 3 — Configure the MCP Client

The tool uses **stdio transport** (reads JSON-RPC from stdin, writes to stdout). Configure your MCP client as follows:

### VS Code (GitHub Copilot) — `.vscode/mcp.json`

Create or update `.vscode/mcp.json` in the workspace root:

```json
{
  "servers": {
    "zafiro-avalonia-mcp": {
      "command": "zafiro-avalonia-mcp",
      "args": []
    }
  }
}
```

### Claude Desktop — `claude_desktop_config.json`

Add to the `mcpServers` section:

```json
{
  "mcpServers": {
    "zafiro-avalonia-mcp": {
      "command": "zafiro-avalonia-mcp",
      "args": []
    }
  }
}
```

### Generic MCP Client

Any MCP client that supports stdio transport can use:
- **Command:** `zafiro-avalonia-mcp`
- **Arguments:** none
- **Transport:** stdio

## Step 4 — Verify the Setup

1. **Run the Avalonia app** with `UseMcpDiagnostics()` enabled.
2. **Check that the discovery file exists:**
   - Linux/macOS: `ls /tmp/zafiro-avalonia-mcp/`
   - Windows: `dir %TEMP%\zafiro-avalonia-mcp\`
3. **Open the MCP client** (VS Code, Claude Desktop, etc.)
4. **Use the `list_apps` tool** — it should discover the running app.
5. **Use `connect_to_app`** to connect, then start inspecting.

## Available MCP Tools

Once connected, the following tool categories are available:

| Category | Tools |
|---|---|
| **Connection** | `list_apps`, `connect_to_app` |
| **Tree inspection** | `get_tree`, `search`, `get_ancestors`, `get_screen_text`, `get_interactables` |
| **Properties** | `get_props`, `set_prop`, `get_styles` |
| **Input** | `click`, `click_by_query`, `click_and_wait`, `key_down`, `key_up`, `text_input` |
| **Interaction** | `select_item`, `toggle`, `set_value`, `scroll`, `action` |
| **Pseudo-classes** | `pseudo_class` (get/set) |
| **Capture** | `screenshot`, `start_recording`, `stop_recording`, `capture_animation` |
| **Resources** | `get_resources`, `list_assets`, `open_asset` |
| **Wait** | `wait_for` |
| **Windows** | `list_windows` |
| **Instructions** | `instructions` (usage guide) |

## Typical AI Agent Workflow

```
1. list_apps              → Discover running Avalonia apps
2. connect_to_app         → Connect to the target app (by PID or auto)
3. get_screen_text        → Read what's visible on screen
4. get_interactables      → List all clickable/editable controls
5. click / text_input     → Interact with controls
6. screenshot             → Capture current state as PNG
7. wait_for               → Wait for UI conditions before proceeding
```

## Detection Strategy (for the agent)

To determine if an Avalonia project already has MCP configured:

1. **Check if AppHost is referenced:** search `.csproj` files for `Zafiro.Avalonia.Mcp.AppHost`
2. **Check if `UseMcpDiagnostics()` is called:** search `Program.cs` or `App.axaml.cs` for `UseMcpDiagnostics`
3. **Check if the tool is installed:** run `dotnet tool list -g | grep zafiro-avalonia-mcp`
4. **Check if MCP client is configured:** look for `zafiro-avalonia-mcp` in `.vscode/mcp.json` or the client's config

## Conditional Installation (DEBUG only)

If the user wants MCP diagnostics only in Debug builds, wrap the call with a preprocessor directive:

```csharp
public static AppBuilder BuildAvaloniaApp()
{
    var builder = AppBuilder.Configure<App>()
        .UsePlatformDetect()
        .WithInterFont()
        .LogToTrace();

#if DEBUG
    builder = builder.UseMcpDiagnostics();
#endif

    return builder;
}
```

And conditionally include the package in the `.csproj`:

```xml
<ItemGroup Condition="'$(Configuration)' == 'Debug'">
  <PackageReference Include="Zafiro.Avalonia.Mcp.AppHost" Version="*" />
</ItemGroup>
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `list_apps` returns empty | Ensure the Avalonia app is running and has `UseMcpDiagnostics()` in the builder chain. Check that discovery files exist in `{TEMP}/zafiro-avalonia-mcp/`. |
| Tool not found after install | Ensure `~/.dotnet/tools` is in your PATH. Run `export PATH="$HOME/.dotnet/tools:$PATH"` or restart your terminal. |
| Connection drops | The app may have exited. Discovery files from crashed apps may linger — delete stale `.json` files from the discovery directory. |
| TypeLoadException | Version mismatch — `Zafiro.Avalonia.Mcp.AppHost` targets Avalonia 12.x. It is not compatible with Avalonia 11.x apps. |
| Logging corrupts stdio | The MCP tool redirects all logging to stderr. If you see JSON parse errors, ensure nothing else writes to stdout. |

## Rules

1. **Always add the NuGet package first**, then the `UseMcpDiagnostics()` call. Never just one without the other.
2. **Always install the global tool** — the MCP system won't work without it.
3. **Always configure the MCP client** — the tool does nothing on its own; it needs an MCP client to invoke it.
4. **Don't add `UseMcpDiagnostics()` to library projects** — only add it to the executable Desktop project that contains the `AppBuilder`.
5. **Verify the setup works** by running the app and checking `list_apps` returns it.
6. **If the project already has the AppHost package and `UseMcpDiagnostics()` call**, skip Steps 1. Only install the tool and configure the client.
