---
name: tauri
description: Build cross-platform desktop and mobile applications with Tauri v2. Use when creating desktop apps, configuring Tauri projects, writing Rust commands, setting up IPC communication, managing plugins, configuring capabilities and permissions, or building/distributing Tauri applications.
---

<objective>
Build cross-platform desktop and mobile applications using Tauri v2, which combines web frontend technologies (HTML, CSS, JavaScript) with a Rust backend for small, fast, and secure apps.
</objective>

<quick_start>
<create_new_project>
```bash
# Create new Tauri app (interactive)
pnpm create tauri-app

# Or with npm/yarn/bun
npm create tauri-app@latest
yarn create tauri-app
bun create tauri-app
```
</create_new_project>

<add_to_existing_project>
```bash
# Install Tauri CLI
pnpm add -D @tauri-apps/cli

# Initialize Tauri in existing project
pnpm tauri init
```

This creates the `src-tauri/` directory with:
- `Cargo.toml` - Rust dependencies
- `tauri.conf.json` - App configuration
- `src/lib.rs` - Rust backend code
- `capabilities/` - Permission definitions
</add_to_existing_project>

<run_development>
```bash
# Desktop development
pnpm tauri dev

# Mobile development
pnpm tauri android dev
pnpm tauri ios dev
```
</run_development>
</quick_start>

<project_structure>
```
my-app/
├── src/                    # Frontend source
├── package.json
├── src-tauri/
│   ├── Cargo.toml          # Rust dependencies
│   ├── tauri.conf.json     # Tauri configuration
│   ├── capabilities/       # Permission definitions
│   │   └── default.json
│   ├── src/
│   │   ├── lib.rs          # Commands and setup
│   │   └── main.rs         # Entry point
│   └── icons/              # App icons
└── dist/                   # Built frontend assets
```
</project_structure>

<core_configuration>
**tauri.conf.json** - Primary configuration file:

```json
{
  "productName": "my-app",
  "version": "0.1.0",
  "build": {
    "beforeDevCommand": "pnpm dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "pnpm build",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "My App",
        "width": 800,
        "height": 600,
        "resizable": true
      }
    ],
    "security": {
      "csp": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "identifier": "com.example.myapp"
  }
}
```
</core_configuration>

<commands_ipc>
<define_command>
In `src-tauri/src/lib.rs`:

```rust
#[tauri::command]
fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```
</define_command>

<call_from_frontend>
```typescript
import { invoke } from '@tauri-apps/api/core';

// Call Rust command
const greeting = await invoke<string>('greet', { name: 'World' });
console.log(greeting); // "Hello, World!"
```
</call_from_frontend>

<async_commands>
```rust
#[tauri::command]
async fn fetch_data(url: String) -> Result<String, String> {
    // Async operations here
    Ok("data".to_string())
}
```
</async_commands>

<error_handling>
```rust
#[tauri::command]
fn risky_operation() -> Result<String, String> {
    if some_condition {
        Ok("success".to_string())
    } else {
        Err("operation failed".to_string())
    }
}
```

```typescript
try {
    const result = await invoke('risky_operation');
} catch (error) {
    console.error(error); // "operation failed"
}
```
</error_handling>
</commands_ipc>

<events>
<emit_from_frontend>
```typescript
import { emit, listen } from '@tauri-apps/api/event';

// Emit event to backend
await emit('file-selected', { path: '/path/to/file' });

// Listen for events from backend
const unlisten = await listen('download-progress', (event) => {
    console.log(event.payload);
});
```
</emit_from_frontend>

<emit_from_backend>
```rust
use tauri::Emitter;

#[tauri::command]
fn start_download(app: tauri::AppHandle) {
    // Emit to all windows
    app.emit("download-progress", 50).unwrap();
}
```
</emit_from_backend>
</events>

<capabilities_permissions>
Capabilities control what the frontend can access. Define in `src-tauri/capabilities/default.json`:

```json
{
  "identifier": "default",
  "description": "Default capabilities",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "dialog:allow-open",
    "fs:allow-read-text-file"
  ]
}
```

**Permission format**: `plugin:scope` (e.g., `fs:allow-read-text-file`)

See [references/capabilities.md](references/capabilities.md) for complete permissions guide.
</capabilities_permissions>

<plugins>
<install_plugin>
```bash
# Add Rust dependency
cargo add tauri-plugin-shell

# Add JS bindings (if available)
pnpm add @tauri-apps/plugin-shell
```
</install_plugin>

<register_plugin>
```rust
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```
</register_plugin>

<common_plugins>
| Plugin | Purpose |
|--------|---------|
| `shell` | Execute commands, open URLs |
| `dialog` | File dialogs, message boxes |
| `fs` | File system access |
| `http` | HTTP client requests |
| `store` | Persistent key-value storage |
| `notification` | System notifications |
| `clipboard` | Clipboard access |
| `updater` | In-app updates |
</common_plugins>

See [references/plugins.md](references/plugins.md) for complete plugin list and usage.
</plugins>

<building_distribution>
<build_commands>
```bash
# Build for current platform
pnpm tauri build

# Build for mobile
pnpm tauri android build
pnpm tauri ios build

# Build specific target
pnpm tauri build --target x86_64-apple-darwin
```
</build_commands>

<bundle_formats>
| Platform | Formats |
|----------|---------|
| Windows | .msi, .exe (NSIS) |
| macOS | .app, .dmg |
| Linux | .deb, .rpm, .AppImage |
| Android | .apk, .aab |
| iOS | .ipa |
</bundle_formats>

See [references/distribution.md](references/distribution.md) for signing and store submission.
</building_distribution>

<windows_management>
<config_windows>
```json
{
  "app": {
    "windows": [
      {
        "label": "main",
        "title": "Main Window",
        "width": 800,
        "height": 600,
        "resizable": true,
        "fullscreen": false,
        "decorations": true,
        "transparent": false
      }
    ]
  }
}
```
</config_windows>

<create_window_js>
```typescript
import { WebviewWindow } from '@tauri-apps/api/webviewWindow';

const webview = new WebviewWindow('settings', {
    url: '/settings',
    title: 'Settings',
    width: 400,
    height: 300
});

webview.once('tauri://created', () => {
    console.log('Window created');
});
```
</create_window_js>

<create_window_rust>
```rust
use tauri::WebviewWindowBuilder;

#[tauri::command]
async fn open_settings(app: tauri::AppHandle) -> Result<(), String> {
    WebviewWindowBuilder::new(&app, "settings", tauri::WebviewUrl::App("/settings".into()))
        .title("Settings")
        .inner_size(400.0, 300.0)
        .build()
        .map_err(|e| e.to_string())?;
    Ok(())
}
```
</create_window_rust>
</windows_management>

<detailed_references>
- **Prerequisites**: [references/prerequisites.md](references/prerequisites.md) - Platform-specific setup
- **Capabilities**: [references/capabilities.md](references/capabilities.md) - Permissions system
- **Plugins**: [references/plugins.md](references/plugins.md) - Official plugin catalog
- **Distribution**: [references/distribution.md](references/distribution.md) - Building and signing
- **Official docs**: https://v2.tauri.app/
</detailed_references>

<success_criteria>
- Tauri app runs in development mode with hot reload
- Rust commands are callable from frontend via `invoke`
- Required capabilities are configured for used APIs
- App builds successfully for target platforms
- Bundle size is optimized (typically under 10MB)
</success_criteria>
