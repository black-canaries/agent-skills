# Tauri v2 Official Plugins

Complete catalog of official Tauri plugins. Official docs: https://v2.tauri.app/plugin/

## Installation Pattern

<install_pattern>
All official plugins follow the same installation pattern:

```bash
# 1. Add Rust crate
cargo add tauri-plugin-{name}

# 2. Add JavaScript bindings (if available)
pnpm add @tauri-apps/plugin-{name}

# 3. Register plugin in src-tauri/src/lib.rs
tauri::Builder::default()
    .plugin(tauri_plugin_{name}::init())
    ...

# 4. Add capabilities in src-tauri/capabilities/default.json
{
  "permissions": ["{name}:default"]
}
```
</install_pattern>

## Core Plugins

<shell_plugin>
**Shell** - Execute commands, open URLs
```bash
cargo add tauri-plugin-shell
pnpm add @tauri-apps/plugin-shell
```

```rust
.plugin(tauri_plugin_shell::init())
```

```typescript
import { open } from '@tauri-apps/plugin-shell';
await open('https://tauri.app');
```

Permissions: `shell:allow-open`, `shell:allow-execute`, `shell:allow-spawn`
</shell_plugin>

<dialog_plugin>
**Dialog** - Native file dialogs, message boxes
```bash
cargo add tauri-plugin-dialog
pnpm add @tauri-apps/plugin-dialog
```

```typescript
import { open, save, message, ask } from '@tauri-apps/plugin-dialog';

// Open file picker
const file = await open({
  multiple: false,
  filters: [{ name: 'Text', extensions: ['txt', 'md'] }]
});

// Save dialog
const path = await save({
  defaultPath: 'document.txt'
});

// Message box
await message('Operation completed!', { title: 'Success', kind: 'info' });

// Confirmation
const confirmed = await ask('Are you sure?', { title: 'Confirm', kind: 'warning' });
```

Permissions: `dialog:allow-open`, `dialog:allow-save`, `dialog:allow-message`, `dialog:allow-ask`
</dialog_plugin>

<fs_plugin>
**File System** - Read/write files and directories
```bash
cargo add tauri-plugin-fs
pnpm add @tauri-apps/plugin-fs
```

```typescript
import { readTextFile, writeTextFile, readDir, mkdir } from '@tauri-apps/plugin-fs';
import { appDataDir } from '@tauri-apps/api/path';

const dataDir = await appDataDir();

// Read file
const content = await readTextFile(`${dataDir}/config.json`);

// Write file
await writeTextFile(`${dataDir}/config.json`, JSON.stringify(config));

// List directory
const entries = await readDir(dataDir);

// Create directory
await mkdir(`${dataDir}/cache`, { recursive: true });
```

Permissions: `fs:default`, `fs:allow-read-text-file`, `fs:allow-write-text-file`
</fs_plugin>

<http_plugin>
**HTTP** - Make HTTP requests
```bash
cargo add tauri-plugin-http
pnpm add @tauri-apps/plugin-http
```

```typescript
import { fetch } from '@tauri-apps/plugin-http';

const response = await fetch('https://api.example.com/data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: 'value' })
});

const data = await response.json();
```

Permissions: `http:default` (with URL scope)
</http_plugin>

<store_plugin>
**Store** - Persistent key-value storage
```bash
cargo add tauri-plugin-store
pnpm add @tauri-apps/plugin-store
```

```typescript
import { Store } from '@tauri-apps/plugin-store';

const store = new Store('settings.json');

await store.set('theme', 'dark');
await store.set('fontSize', 14);

const theme = await store.get('theme');
await store.save(); // Persist to disk
```

Permissions: `store:default`
</store_plugin>

<notification_plugin>
**Notification** - System notifications
```bash
cargo add tauri-plugin-notification
pnpm add @tauri-apps/plugin-notification
```

```typescript
import { sendNotification, requestPermission, isPermissionGranted } from '@tauri-apps/plugin-notification';

// Check/request permission
if (!(await isPermissionGranted())) {
  await requestPermission();
}

// Send notification
sendNotification({
  title: 'Download Complete',
  body: 'Your file has been downloaded successfully.'
});
```

Permissions: `notification:default`
</notification_plugin>

<clipboard_plugin>
**Clipboard** - System clipboard access
```bash
cargo add tauri-plugin-clipboard-manager
pnpm add @tauri-apps/plugin-clipboard-manager
```

```typescript
import { writeText, readText } from '@tauri-apps/plugin-clipboard-manager';

await writeText('Hello, clipboard!');
const text = await readText();
```

Permissions: `clipboard-manager:allow-read-text`, `clipboard-manager:allow-write-text`
</clipboard_plugin>

## Desktop Plugins

<global_shortcut_plugin>
**Global Shortcut** - System-wide keyboard shortcuts
```bash
cargo add tauri-plugin-global-shortcut
pnpm add @tauri-apps/plugin-global-shortcut
```

```typescript
import { register, unregister } from '@tauri-apps/plugin-global-shortcut';

await register('CommandOrControl+Shift+C', () => {
  console.log('Shortcut triggered!');
});

await unregister('CommandOrControl+Shift+C');
```

Permissions: `global-shortcut:default`
</global_shortcut_plugin>

<updater_plugin>
**Updater** - In-app updates
```bash
cargo add tauri-plugin-updater
pnpm add @tauri-apps/plugin-updater
```

```typescript
import { check } from '@tauri-apps/plugin-updater';

const update = await check();
if (update) {
  console.log(`Update available: ${update.version}`);
  await update.downloadAndInstall();
}
```

Requires `tauri.conf.json` configuration for update endpoints.
</updater_plugin>

<window_state_plugin>
**Window State** - Persist window size/position
```bash
cargo add tauri-plugin-window-state
```

```rust
.plugin(tauri_plugin_window_state::Builder::default().build())
```

Automatically saves and restores window geometry.
</window_state_plugin>

<autostart_plugin>
**Autostart** - Launch at system startup
```bash
cargo add tauri-plugin-autostart
pnpm add @tauri-apps/plugin-autostart
```

```typescript
import { enable, disable, isEnabled } from '@tauri-apps/plugin-autostart';

await enable();
const enabled = await isEnabled(); // true
await disable();
```
</autostart_plugin>

<single_instance_plugin>
**Single Instance** - Prevent multiple app instances
```bash
cargo add tauri-plugin-single-instance
```

```rust
.plugin(tauri_plugin_single_instance::init(|app, argv, cwd| {
    // Handle second instance launch
    println!("Second instance with args: {:?}", argv);
}))
```
</single_instance_plugin>

<positioner_plugin>
**Positioner** - Move windows to predefined positions
```bash
cargo add tauri-plugin-positioner
pnpm add @tauri-apps/plugin-positioner
```

```typescript
import { moveWindow, Position } from '@tauri-apps/plugin-positioner';

await moveWindow(Position.TopRight);
await moveWindow(Position.Center);
```
</positioner_plugin>

## Mobile Plugins

<barcode_scanner_plugin>
**Barcode Scanner** - QR codes and barcodes (mobile only)
```bash
cargo add tauri-plugin-barcode-scanner
pnpm add @tauri-apps/plugin-barcode-scanner
```

```typescript
import { scan } from '@tauri-apps/plugin-barcode-scanner';

const result = await scan();
console.log(result.content); // Scanned data
```
</barcode_scanner_plugin>

<biometric_plugin>
**Biometric** - Fingerprint/Face ID (mobile only)
```bash
cargo add tauri-plugin-biometric
pnpm add @tauri-apps/plugin-biometric
```

```typescript
import { authenticate } from '@tauri-apps/plugin-biometric';

try {
  await authenticate('Confirm your identity');
  // Authentication successful
} catch (e) {
  // Authentication failed
}
```
</biometric_plugin>

<geolocation_plugin>
**Geolocation** - Device location
```bash
cargo add tauri-plugin-geolocation
pnpm add @tauri-apps/plugin-geolocation
```

```typescript
import { getCurrentPosition, watchPosition } from '@tauri-apps/plugin-geolocation';

const pos = await getCurrentPosition();
console.log(pos.coords.latitude, pos.coords.longitude);

// Watch position changes
const watchId = await watchPosition(
  { enableHighAccuracy: true },
  (pos) => console.log(pos)
);
```
</geolocation_plugin>

<haptics_plugin>
**Haptics** - Vibration feedback (mobile only)
```bash
cargo add tauri-plugin-haptics
pnpm add @tauri-apps/plugin-haptics
```

```typescript
import { vibrate, impactFeedback } from '@tauri-apps/plugin-haptics';

await vibrate({ duration: 100 });
await impactFeedback('medium');
```
</haptics_plugin>

<nfc_plugin>
**NFC** - NFC tag reading/writing (mobile only)
```bash
cargo add tauri-plugin-nfc
pnpm add @tauri-apps/plugin-nfc
```

```typescript
import { scan } from '@tauri-apps/plugin-nfc';

const tag = await scan();
console.log(tag.records);
```
</nfc_plugin>

## Data & Security Plugins

<sql_plugin>
**SQL** - SQLite/MySQL/PostgreSQL via sqlx
```bash
cargo add tauri-plugin-sql
pnpm add @tauri-apps/plugin-sql
```

```typescript
import Database from '@tauri-apps/plugin-sql';

const db = await Database.load('sqlite:app.db');
await db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)');
await db.execute('INSERT INTO users (name) VALUES (?)', ['Alice']);
const users = await db.select('SELECT * FROM users');
```
</sql_plugin>

<stronghold_plugin>
**Stronghold** - Encrypted secure storage
```bash
cargo add tauri-plugin-stronghold
pnpm add @tauri-apps/plugin-stronghold
```

```typescript
import { Stronghold, Client } from '@tauri-apps/plugin-stronghold';
import { appDataDir } from '@tauri-apps/api/path';

const stronghold = await Stronghold.load(`${await appDataDir()}/vault.hold`, 'password');
const client = await stronghold.loadClient('main');
const store = client.getStore();

await store.insert('secret-key', Array.from(new TextEncoder().encode('secret-value')));
const value = await store.get('secret-key');
```
</stronghold_plugin>

## Utility Plugins

<os_plugin>
**OS Information** - Query OS details
```bash
cargo add tauri-plugin-os
pnpm add @tauri-apps/plugin-os
```

```typescript
import { platform, arch, version, type, locale } from '@tauri-apps/plugin-os';

console.log(await platform());  // 'darwin', 'windows', 'linux'
console.log(await arch());      // 'x86_64', 'aarch64'
console.log(await version());   // OS version
```
</os_plugin>

<process_plugin>
**Process** - Current process info
```bash
cargo add tauri-plugin-process
pnpm add @tauri-apps/plugin-process
```

```typescript
import { exit, relaunch } from '@tauri-apps/plugin-process';

await relaunch(); // Restart app
await exit(0);    // Exit with code
```
</process_plugin>

<opener_plugin>
**Opener** - Open files/URLs with default apps
```bash
cargo add tauri-plugin-opener
pnpm add @tauri-apps/plugin-opener
```

```typescript
import { openUrl, openPath, revealItemInDir } from '@tauri-apps/plugin-opener';

await openUrl('https://tauri.app');
await openPath('/path/to/document.pdf');
await revealItemInDir('/path/to/file'); // Show in file manager
```
</opener_plugin>

<deep_link_plugin>
**Deep Linking** - Handle custom URL schemes
```bash
cargo add tauri-plugin-deep-link
pnpm add @tauri-apps/plugin-deep-link
```

Register your app to handle `myapp://` URLs.
</deep_link_plugin>

<logging_plugin>
**Logging** - Configurable logging
```bash
cargo add tauri-plugin-log
pnpm add @tauri-apps/plugin-log
```

```rust
.plugin(tauri_plugin_log::Builder::default().build())
```

```typescript
import { info, error, debug, warn } from '@tauri-apps/plugin-log';

await info('Application started');
await error('Something went wrong');
```
</logging_plugin>

<websocket_plugin>
**Websocket** - WebSocket connections
```bash
cargo add tauri-plugin-websocket
pnpm add @tauri-apps/plugin-websocket
```

```typescript
import WebSocket from '@tauri-apps/plugin-websocket';

const ws = await WebSocket.connect('wss://example.com/socket');
ws.addListener((msg) => console.log(msg));
await ws.send('Hello');
await ws.disconnect();
```
</websocket_plugin>

<upload_plugin>
**Upload** - HTTP file uploads
```bash
cargo add tauri-plugin-upload
pnpm add @tauri-apps/plugin-upload
```

```typescript
import { upload } from '@tauri-apps/plugin-upload';

await upload('https://example.com/upload', '/path/to/file', (progress) => {
  console.log(`${progress.progress}%`);
});
```
</upload_plugin>
