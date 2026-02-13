# Tauri v2 Building and Distribution

Build, sign, and distribute Tauri applications. Official docs: https://v2.tauri.app/distribute/

## Build Commands

<basic_build>
```bash
# Build for current platform (creates installer)
pnpm tauri build

# Alternative package managers
npm run tauri build
yarn tauri build
cargo tauri build

# Mobile builds
pnpm tauri android build
pnpm tauri ios build
```
</basic_build>

<build_options>
```bash
# Build without bundling (compile only)
pnpm tauri build --no-bundle

# Debug build (faster, larger)
pnpm tauri build --debug

# Specific bundle type
pnpm tauri build --bundles deb,appimage

# Specific target
pnpm tauri build --target x86_64-apple-darwin
pnpm tauri build --target aarch64-apple-darwin
pnpm tauri build --target universal-apple-darwin  # Universal macOS

# Custom config
pnpm tauri build --config src-tauri/tauri.prod.conf.json
```
</build_options>

## Bundle Formats by Platform

<bundle_formats>
| Platform | Formats | Notes |
|----------|---------|-------|
| **Windows** | `.msi`, `.exe` (NSIS) | MSI for enterprise, NSIS for consumer |
| **macOS** | `.app`, `.dmg` | DMG contains .app bundle |
| **Linux** | `.deb`, `.rpm`, `.AppImage` | AppImage is portable |
| **Android** | `.apk`, `.aab` | AAB required for Play Store |
| **iOS** | `.ipa` | Requires Apple Developer account |
</bundle_formats>

## Bundle Configuration

<bundle_config>
In `tauri.conf.json`:

```json
{
  "bundle": {
    "active": true,
    "targets": "all",
    "identifier": "com.mycompany.myapp",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "resources": ["assets/*"],
    "copyright": "Copyright 2024 My Company",
    "category": "Utility",
    "shortDescription": "My awesome app",
    "longDescription": "A longer description of my app.",
    "linux": {
      "deb": {
        "depends": ["libssl3"]
      },
      "appimage": {
        "bundleMediaFramework": true
      }
    },
    "macOS": {
      "minimumSystemVersion": "10.15",
      "exceptionDomain": null,
      "signingIdentity": null,
      "entitlements": null
    },
    "windows": {
      "certificateThumbprint": null,
      "timestampUrl": "http://timestamp.digicert.com",
      "wix": null,
      "nsis": {
        "installerIcon": "icons/icon.ico"
      }
    }
  }
}
```
</bundle_config>

## Version Management

<versioning>
Version is read from (in order):
1. `tauri.conf.json` → `version`
2. `src-tauri/Cargo.toml` → `[package] version`

```json
{
  "productName": "my-app",
  "version": "1.2.3"
}
```

**Version format**: `major.minor.patch` (semver)
</versioning>

## Windows Signing

<windows_signing>
**Requirements:**
- Code signing certificate (.pfx or from Windows Certificate Store)
- Optional: EV certificate for SmartScreen reputation

**Configuration:**

```json
{
  "bundle": {
    "windows": {
      "certificateThumbprint": "YOUR_CERT_THUMBPRINT",
      "timestampUrl": "http://timestamp.digicert.com"
    }
  }
}
```

**Using PFX file:**
```bash
# Set environment variables
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="your-password"

# Sign during build
pnpm tauri build
```

**Using Azure SignTool (cloud signing):**
```bash
cargo install AzureSignTool
# Configure in CI/CD with Azure Key Vault
```
</windows_signing>

## macOS Signing and Notarization

<macos_signing>
**Requirements:**
- Apple Developer account ($99/year)
- Developer ID Application certificate
- App-specific password for notarization

**Step 1: Certificate setup**
```bash
# List available identities
security find-identity -v -p codesigning

# Export certificate (if needed)
# Use Keychain Access to export .p12 file
```

**Step 2: Configuration**
```json
{
  "bundle": {
    "macOS": {
      "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)",
      "entitlements": "./entitlements.plist"
    }
  }
}
```

**Step 3: Notarization (for distribution outside App Store)**
```bash
# Set environment variables
export APPLE_ID="your@email.com"
export APPLE_PASSWORD="app-specific-password"
export APPLE_TEAM_ID="YOUR_TEAM_ID"

# Build (notarization happens automatically)
pnpm tauri build
```

**Entitlements file (entitlements.plist):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
</dict>
</plist>
```
</macos_signing>

## Linux Distribution

<linux_distribution>
**Debian (.deb):**
```json
{
  "bundle": {
    "linux": {
      "deb": {
        "depends": ["libssl3", "libwebkit2gtk-4.1-0"],
        "section": "utility",
        "priority": "optional"
      }
    }
  }
}
```

**RPM (.rpm):**
```json
{
  "bundle": {
    "linux": {
      "rpm": {
        "depends": ["openssl", "webkit2gtk4.1"]
      }
    }
  }
}
```

**AppImage:**
```json
{
  "bundle": {
    "linux": {
      "appimage": {
        "bundleMediaFramework": true
      }
    }
  }
}
```

AppImage is the most portable - single file, runs on most distros.
</linux_distribution>

## Android Distribution

<android_distribution>
**Build APK (direct distribution):**
```bash
pnpm tauri android build
# Output: src-tauri/gen/android/app/build/outputs/apk/
```

**Build AAB (Play Store):**
```bash
pnpm tauri android build --aab
# Output: src-tauri/gen/android/app/build/outputs/bundle/
```

**Signing:**
Create a keystore:
```bash
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

Configure in `src-tauri/gen/android/app/build.gradle.kts`:
```kotlin
signingConfigs {
    create("release") {
        storeFile = file("my-release-key.jks")
        storePassword = System.getenv("KEYSTORE_PASSWORD")
        keyAlias = "my-key-alias"
        keyPassword = System.getenv("KEY_PASSWORD")
    }
}
```
</android_distribution>

## iOS Distribution

<ios_distribution>
**Requirements:**
- macOS with Xcode
- Apple Developer account
- Provisioning profile

**Build:**
```bash
pnpm tauri ios build
```

**Xcode setup:**
1. Open `src-tauri/gen/apple/` in Xcode
2. Configure signing team
3. Select provisioning profile
4. Archive and upload to App Store Connect

**For TestFlight/App Store:**
- Use Xcode's Product → Archive
- Or configure Fastlane for CI/CD
</ios_distribution>

## Auto-Updates

<updater_setup>
**1. Install plugin:**
```bash
cargo add tauri-plugin-updater
pnpm add @tauri-apps/plugin-updater
```

**2. Configure endpoints:**
```json
{
  "plugins": {
    "updater": {
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"
      ],
      "pubkey": "YOUR_PUBLIC_KEY"
    }
  }
}
```

**3. Generate signing keys:**
```bash
pnpm tauri signer generate -w ~/.tauri/myapp.key
# Save the public key for config
```

**4. Check for updates:**
```typescript
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

const update = await check();
if (update) {
  await update.downloadAndInstall();
  await relaunch();
}
```

**5. Update server response format:**
```json
{
  "version": "1.2.3",
  "notes": "Bug fixes and improvements",
  "pub_date": "2024-01-15T00:00:00Z",
  "platforms": {
    "darwin-x86_64": {
      "signature": "SIGNATURE_HERE",
      "url": "https://releases.myapp.com/myapp-1.2.3-x86_64.app.tar.gz"
    },
    "darwin-aarch64": {
      "signature": "SIGNATURE_HERE",
      "url": "https://releases.myapp.com/myapp-1.2.3-aarch64.app.tar.gz"
    },
    "windows-x86_64": {
      "signature": "SIGNATURE_HERE",
      "url": "https://releases.myapp.com/myapp-1.2.3-x64-setup.nsis.zip"
    }
  }
}
```
</updater_setup>

## CI/CD Integration

<github_actions>
**.github/workflows/release.yml:**

```yaml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    permissions:
      contents: write
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: 'macos-latest'
            args: '--target aarch64-apple-darwin'
          - platform: 'macos-latest'
            args: '--target x86_64-apple-darwin'
          - platform: 'ubuntu-22.04'
            args: ''
          - platform: 'windows-latest'
            args: ''

    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install Rust stable
        uses: dtolnay/rust-action@stable

      - name: Install dependencies (Ubuntu)
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf

      - name: Install frontend dependencies
        run: pnpm install

      - name: Build Tauri app
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        with:
          tagName: v__VERSION__
          releaseName: 'App v__VERSION__'
          releaseBody: 'See the assets to download this version and install.'
          releaseDraft: true
          prerelease: false
          args: ${{ matrix.args }}
```
</github_actions>

## Optimization

<size_optimization>
**Reduce binary size:**

In `src-tauri/Cargo.toml`:
```toml
[profile.release]
panic = "abort"
codegen-units = 1
lto = true
opt-level = "s"  # or "z" for smallest size
strip = true
```

**Frontend optimization:**
- Enable minification in your bundler
- Tree-shake unused code
- Compress assets

**Typical sizes:**
- Minimal app: ~2-5 MB
- With plugins: ~5-10 MB
- Complex app: ~10-20 MB
</size_optimization>
