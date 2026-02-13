# Tauri v2 Capabilities and Permissions

The capability system controls what APIs the frontend can access. Official docs: https://v2.tauri.app/security/capabilities/

## Core Concepts

<overview>
**Capabilities** = Sets of permissions applied to specific windows/webviews

**Permissions** = Individual API access grants (e.g., `fs:allow-read-text-file`)

**Security model**: Frontend code runs in a sandboxed WebView with no system access by default. Capabilities explicitly grant access through the IPC layer.
</overview>

## Capability Files

<file_location>
Capabilities are defined in `src-tauri/capabilities/` as JSON or TOML files.

All files in this directory are **automatically enabled** unless you explicitly list capabilities in `tauri.conf.json`.
</file_location>

<basic_example>
`src-tauri/capabilities/default.json`:

```json
{
  "$schema": "https://schemas.tauri.app/schemas/capabilities.json",
  "identifier": "default",
  "description": "Default application capabilities",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "dialog:allow-open",
    "dialog:allow-save"
  ]
}
```
</basic_example>

<toml_example>
`src-tauri/capabilities/default.toml`:

```toml
[[capability]]
identifier = "default"
description = "Default application capabilities"
windows = ["main"]
permissions = [
  "core:default",
  "shell:allow-open",
  "dialog:allow-open"
]
```
</toml_example>

## Permission Format

<permission_syntax>
Permissions follow the format: `plugin:scope`

**Examples:**
- `core:default` - Core Tauri functionality
- `fs:allow-read-text-file` - Read text files
- `fs:deny-write-file` - Explicitly deny file writing
- `shell:allow-open` - Open URLs/files with default app
- `dialog:allow-open` - Show open file dialog
- `http:default` - HTTP client access
</permission_syntax>

## Core Permissions

<core_permissions>
| Permission | Description |
|------------|-------------|
| `core:default` | Essential Tauri APIs (window, events) |
| `core:window:allow-close` | Close windows |
| `core:window:allow-minimize` | Minimize windows |
| `core:window:allow-maximize` | Maximize windows |
| `core:window:allow-set-title` | Change window title |
| `core:window:allow-set-size` | Resize windows |
| `core:event:default` | Event system access |
</core_permissions>

## Plugin Permissions

<fs_permissions>
**File System (tauri-plugin-fs):**
| Permission | Description |
|------------|-------------|
| `fs:default` | Safe read access to app directories |
| `fs:allow-read-text-file` | Read text files |
| `fs:allow-write-text-file` | Write text files |
| `fs:allow-read-file` | Read binary files |
| `fs:allow-write-file` | Write binary files |
| `fs:allow-mkdir` | Create directories |
| `fs:allow-remove` | Delete files/directories |
| `fs:allow-rename` | Rename files |
| `fs:allow-copy-file` | Copy files |
</fs_permissions>

<dialog_permissions>
**Dialog (tauri-plugin-dialog):**
| Permission | Description |
|------------|-------------|
| `dialog:default` | All dialog permissions |
| `dialog:allow-open` | Open file picker |
| `dialog:allow-save` | Save file picker |
| `dialog:allow-message` | Message dialog |
| `dialog:allow-ask` | Confirmation dialog |
</dialog_permissions>

<shell_permissions>
**Shell (tauri-plugin-shell):**
| Permission | Description |
|------------|-------------|
| `shell:allow-open` | Open URLs/files with default app |
| `shell:allow-execute` | Execute shell commands |
| `shell:allow-spawn` | Spawn child processes |
| `shell:allow-stdin-write` | Write to spawned process stdin |
| `shell:allow-kill` | Kill spawned processes |
</shell_permissions>

<http_permissions>
**HTTP (tauri-plugin-http):**
| Permission | Description |
|------------|-------------|
| `http:default` | HTTP client with scope restrictions |
| `http:allow-fetch` | Make HTTP requests |
</http_permissions>

## Scoped Permissions

<fs_scope>
Restrict file system access to specific paths:

```json
{
  "identifier": "main-capability",
  "windows": ["main"],
  "permissions": [
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [
        { "path": "$APPDATA/**" },
        { "path": "$RESOURCE/**" }
      ]
    }
  ]
}
```

**Path variables:**
- `$APPDATA` - App data directory
- `$APPCONFIG` - App config directory
- `$RESOURCE` - Resource directory
- `$HOME` - User home directory
- `$DESKTOP` - Desktop directory
- `$DOCUMENT` - Documents directory
- `$DOWNLOAD` - Downloads directory
</fs_scope>

<http_scope>
Restrict HTTP access to specific domains:

```json
{
  "identifier": "api-access",
  "permissions": [
    {
      "identifier": "http:default",
      "allow": [
        { "url": "https://api.example.com/**" }
      ],
      "deny": [
        { "url": "https://api.example.com/admin/**" }
      ]
    }
  ]
}
```
</http_scope>

## Platform-Specific Capabilities

<platform_targeting>
Apply capabilities only on specific platforms:

```json
{
  "identifier": "desktop-only",
  "windows": ["main"],
  "platforms": ["linux", "macOS", "windows"],
  "permissions": [
    "shell:allow-execute"
  ]
}
```

```json
{
  "identifier": "mobile-only",
  "windows": ["main"],
  "platforms": ["iOS", "android"],
  "permissions": [
    "haptics:default",
    "geolocation:default"
  ]
}
```
</platform_targeting>

## Window-Specific Capabilities

<multi_window>
Different capabilities for different windows:

```json
{
  "identifier": "editor-capability",
  "windows": ["editor"],
  "permissions": [
    "fs:allow-read-text-file",
    "fs:allow-write-text-file"
  ]
}
```

```json
{
  "identifier": "settings-capability",
  "windows": ["settings"],
  "permissions": [
    "store:default"
  ]
}
```
</multi_window>

## Explicit Capability Selection

<explicit_config>
To use only specific capabilities (not all in directory):

In `tauri.conf.json`:
```json
{
  "app": {
    "security": {
      "capabilities": ["default", "editor-capability"]
    }
  }
}
```
</explicit_config>

## Security Best Practices

<best_practices>
1. **Principle of least privilege** - Only grant permissions actually needed
2. **Use scopes** - Restrict file/HTTP access to specific paths/domains
3. **Separate capabilities** - Different windows should have different permissions
4. **Deny explicitly** - Use `deny` rules to block specific sub-paths
5. **Audit regularly** - Review capabilities when adding new features
</best_practices>

<security_notes>
**Important limitations:**
- On Linux and Android, Tauri cannot distinguish between requests from embedded `<iframe>` and the main window
- Remote URLs in webviews should have minimal capabilities
- CSP (Content Security Policy) provides additional frontend security
</security_notes>
