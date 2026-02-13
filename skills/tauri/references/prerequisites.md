# Tauri v2 Prerequisites

Complete setup guide for all platforms. Official docs: https://v2.tauri.app/start/prerequisites/

## All Platforms

<rust_installation>
**Rust is required on all platforms.**

```bash
# macOS/Linux
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh

# Windows (PowerShell)
winget install --id Rustlang.Rustup

# Verify installation
rustc --version
cargo --version
```
</rust_installation>

<nodejs_optional>
**Node.js is only required if using JavaScript frontend frameworks.**

Download LTS from https://nodejs.org or use a version manager:

```bash
# Verify
node -v
npm -v
```
</nodejs_optional>

## Windows

<windows_requirements>
1. **Microsoft C++ Build Tools**
   - Download from https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select "Desktop development with C++" workload
   - Ensure MSVC toolchain is default: `rustup default stable-msvc`

2. **WebView2 Runtime**
   - Required on Windows 10 (pre-1803) and Windows Server
   - Download "Evergreen Bootstrapper" from https://developer.microsoft.com/microsoft-edge/webview2/
   - Windows 10 1803+ and Windows 11 include it by default

3. **VBScript (for MSI installers only)**
   - Enable in Settings → Apps → Optional features → Add a feature → VBSCRIPT
</windows_requirements>

## macOS

<macos_requirements>
1. **Xcode**
   - Download from Mac App Store or https://developer.apple.com/xcode/
   - **Launch Xcode after installation** to complete setup
   - Accept license: `sudo xcodebuild -license accept`

2. **Alternative: Command Line Tools Only**
   ```bash
   xcode-select --install
   ```
</macos_requirements>

## Linux

<linux_debian>
**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```
</linux_debian>

<linux_arch>
**Arch Linux:**
```bash
sudo pacman -Syu
sudo pacman -S --needed \
  webkit2gtk-4.1 \
  base-devel \
  curl \
  wget \
  file \
  openssl \
  appmenu-gtk-module \
  libappindicator-gtk3 \
  librsvg \
  xdotool
```
</linux_arch>

<linux_fedora>
**Fedora:**
```bash
sudo dnf check-update
sudo dnf install webkit2gtk4.1-devel \
  openssl-devel \
  curl \
  wget \
  file \
  libappindicator-gtk3-devel \
  librsvg2-devel \
  libxdo-devel
sudo dnf group install "C Development Tools and Libraries"
```
</linux_fedora>

## Android Development

<android_setup>
1. **Install Android Studio**
   - Download from https://developer.android.com/studio

2. **Configure SDK via Android Studio SDK Manager:**
   - Android SDK Platform (API level 33+)
   - Android SDK Platform-Tools
   - NDK (Side by side)
   - Android SDK Build-Tools
   - Android SDK Command-line Tools

3. **Set environment variables:**
   ```bash
   # Add to ~/.bashrc, ~/.zshrc, or equivalent
   export JAVA_HOME=/path/to/android-studio/jbr
   export ANDROID_HOME=$HOME/Android/Sdk   # or ~/Library/Android/sdk on macOS
   export NDK_HOME=$ANDROID_HOME/ndk/$(ls -1 $ANDROID_HOME/ndk)
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   ```

4. **Add Rust targets:**
   ```bash
   rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android
   ```
</android_setup>

## iOS Development (macOS Only)

<ios_setup>
1. **Install Xcode** (see macOS section)

2. **Add Rust targets:**
   ```bash
   rustup target add aarch64-apple-ios x86_64-apple-ios aarch64-apple-ios-sim
   ```

3. **Install Homebrew** (if not installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

4. **Install CocoaPods:**
   ```bash
   brew install cocoapods
   ```
</ios_setup>

## Verify Installation

<verification>
```bash
# Check Rust
rustc --version
cargo --version

# Check Tauri CLI
pnpm tauri --version

# Check Android (if configured)
adb --version

# Check iOS targets (macOS)
rustup target list --installed | grep apple-ios
```
</verification>
