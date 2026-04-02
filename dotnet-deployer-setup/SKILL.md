---
name: dotnet-deployer-setup
description: Set up DotnetDeployer deployment files for .NET projects. Creates deployer.yaml, azure-pipelines.yml, and GitVersion.yml with sensible defaults for Desktop (Linux/Windows), Android (APK signed), NuGet, and GitHub Releases. Use when user says "set up deployment", "configure deployer", "create deployment files", "deploy this project", or mentions DotnetDeployer.
---

# DotnetDeployer Setup Skill

Automatically create the deployment configuration files for a .NET project using DotnetDeployer.

## When to Use

Activate when the user:
- Asks to set up deployment for a .NET project
- Says "create deployment files", "configure deployer", "set up CI/CD"
- Mentions DotnetDeployer in the context of a new project
- Wants to deploy a Desktop, Android, or NuGet project

## Required Information

Before generating files, gather from the user (or infer from the codebase):

1. **GitHub owner and repo name** — inspect git remote or ask
2. **Project type** — detect from .csproj (Desktop, Android, NuGet library, WebAssembly)
3. **Desktop project path** — e.g. `src/MyApp.Desktop/MyApp.Desktop.csproj`
4. **Android project path** — e.g. `src/MyApp.Android/MyApp.Android.csproj` (if applicable)
5. **Variable group name** — default: `api-keys` (ask if the user wants a different name)

## Detection Strategy

1. Find the solution file (.slnx or .sln) in the repo root
2. Scan .csproj files for target frameworks:
   - `net*-android` → Android project
   - `net*-browser` or references to `Microsoft.AspNetCore.Components.WebAssembly` → Wasm/Browser
   - Desktop project → typically the one with Avalonia or WPF references, or the main executable
3. Check if any project has `<IsPackable>true</IsPackable>` or is a class library → NuGet candidate
4. Get `owner` and `repo` from `git remote get-url origin`

## Files to Create

Always create these three files in the **repository root**:

### 1. `GitVersion.yml`

```yaml
mode: ContinuousDelivery
branches:
  master:
    regex: ^master$|^main$
    tag: ''
    increment: Patch
  feature:
    regex: ^feature[/-]
    tag: alpha
    increment: Minor
  hotfix:
    regex: ^hotfix[/-]
    tag: beta
    increment: Patch
  pull-request:
    regex: ^(pull|pr)[/-]
    tag: pr
    increment: Inherit
```

### 2. `deployer.yaml`

Build the config based on detected project types.

#### NuGet section (if packable projects exist)

```yaml
nuget:
  enabled: true
  source: https://api.nuget.org/v3/index.json
  apiKeyEnvVar: NUGET_API_KEY
```

#### GitHub Releases section (if desktop or android projects exist)

For **Desktop** projects, default formats are:
- Linux: `appimage` (x64, arm64) + `exe-sfx` (x64)
- Windows: `exe-setup` (x64)

For **Android** projects, default format is:
- `apk` (x64) with signing using the **expanded keystore source**

```yaml
github:
  enabled: true
  owner: {detected_owner}
  repo: {detected_repo}
  tokenEnvVar: GITHUB_TOKEN
  outputDir: artifacts
  packages:
    - project: {desktop_project_path}
      formats:
        - type: appimage
          arch: [x64, arm64]
        - type: exe-sfx
          arch: [x64]
        - type: exe-setup
          arch: [x64]
    - project: {android_project_path}
      formats:
        - type: apk
          arch: [x64]
          signing:
            keystore:
              from: env
              name: ANDROID_KEYSTORE_BASE64
              encoding: base64
            storePasswordEnvVar: ANDROID_STORE_PASS
            keyAlias: release-key
            keyPasswordEnvVar: ANDROID_KEY_PASS
```

#### Android top-level section (alternative to per-format signing)

If the user prefers the top-level android config:

```yaml
android:
  signing:
    keystore:
      from: env
      name: ANDROID_KEYSTORE_BASE64
      encoding: base64
    storePasswordEnvVar: ANDROID_STORE_PASS
    keyAlias: release-key
    keyPasswordEnvVar: ANDROID_KEY_PASS
```

#### GitHub Pages section (if browser/wasm project exists)

```yaml
githubPages:
  enabled: true
  owner: {detected_owner}
  repo: {detected_repo}-demo
  tokenEnvVar: GITHUB_TOKEN
  projects:
    - project: {browser_project_path}
```

### 3. `azure-pipelines.yml`

The env block must map ALL required variables from the variable group. Build the env block dynamically based on which sections are enabled in deployer.yaml.

```yaml
trigger:
  - master
  - main

variables:
  - group: {variable_group_name}
  - name: Agent.Source.Git.ShallowFetchDepth
    value: 0

pool:
  vmImage: 'ubuntu-latest'

steps:
  - checkout: self
    fetchDepth: 0

  - pwsh: |
      dotnet tool install -g DotnetDeployer.Tool
      dotnetdeployer --dry-run
    displayName: Dry run (PRs)
    condition: and(succeeded(), ne(variables['Build.SourceBranch'], 'refs/heads/master'))
    env:
      NUGET_API_KEY: $(NugetApiKey)
      GITHUB_TOKEN: $(GitHubToken)
      ANDROID_KEYSTORE_BASE64: $(AndroidKeystoreBase64)
      ANDROID_STORE_PASS: $(AndroidStorePass)
      ANDROID_KEY_PASS: $(AndroidKeyPass)

  - pwsh: |
      dotnet tool install -g DotnetDeployer.Tool
      dotnetdeployer
    displayName: Deploy
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/master'))
    env:
      NUGET_API_KEY: $(NugetApiKey)
      GITHUB_TOKEN: $(GitHubToken)
      ANDROID_KEYSTORE_BASE64: $(AndroidKeystoreBase64)
      ANDROID_STORE_PASS: $(AndroidStorePass)
      ANDROID_KEY_PASS: $(AndroidKeyPass)
```

**IMPORTANT**: Only include env vars that are actually needed. If no NuGet section → no `NUGET_API_KEY`. If no Android signing → no `ANDROID_*` vars. If no GitHub section → no `GITHUB_TOKEN`.

## Post-Creation Message

After creating the files, ALWAYS tell the user which variables must be defined in the Azure DevOps variable group. Format as a table:

```
✅ Files created:
  - GitVersion.yml
  - deployer.yaml
  - azure-pipelines.yml

⚠️  Required variables in Azure DevOps variable group '{group_name}':

| Variable               | Description                                    | Secret? |
|------------------------|------------------------------------------------|---------|
| NugetApiKey            | NuGet.org API key                              | Yes     |
| GitHubToken            | GitHub PAT with 'repo' scope                   | Yes     |
| AndroidKeystoreBase64  | Android keystore file encoded in base64        | Yes     |
| AndroidStorePass       | Android keystore store password                | Yes     |
| AndroidKeyPass         | Android signing key password                   | Yes     |

To encode your keystore as base64:
  base64 -w 0 < your-release.keystore

Then paste the output as the value of AndroidKeystoreBase64.
```

Only list variables that are actually referenced in the generated files.

## Keystore Source Options

When the user mentions wanting to use a **secrets file** instead of env vars for the keystore, use:

```yaml
android:
  signing:
    keystore:
      from: secret
      key: android_keystore_base64
      encoding: base64
```

And instruct them to create `deployer.secrets.yaml` (gitignored) with:

```yaml
android_keystore_base64: <base64-encoded-keystore>
```

When the user has a **physical keystore file**, use:

```yaml
android:
  signing:
    keystore:
      from: file
      path: ./android/release.keystore
```

## Variable Group Name

- Default: `api-keys`
- Ask the user: "What Azure DevOps variable group should I use? (default: api-keys)"
- If the user specifies a different name, use it in `azure-pipelines.yml`

## Rules

1. **Never create files that already exist** without asking the user first
2. **Always detect** project types from .csproj before generating config
3. **Always include only the relevant sections** — don't add NuGet if there are no packable projects
4. **Always report the required variables** after creating files
5. **Use the expanded keystore source** for Android signing (never the legacy `keystoreBase64EnvVar`)
6. **Variable names in env block** must match the env var names used in deployer.yaml
7. **Variable group references** use `$(PascalCaseVarName)` Azure DevOps syntax
