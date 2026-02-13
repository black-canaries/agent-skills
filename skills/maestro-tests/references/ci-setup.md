# Maestro CI/CD Setup

## Prerequisites

- Java 17+ on CI runner
- iOS Simulator (macOS runner) or Android Emulator
- App built and installed on simulator/emulator before tests run

## Installation in CI

```bash
curl -fsSL "https://get.maestro.mobile.dev" | bash
export PATH="$PATH":"$HOME/.maestro/bin"
```

Pin a specific version:
```bash
export MAESTRO_VERSION=1.38.1
curl -fsSL "https://get.maestro.mobile.dev" | bash
```

## GitHub Actions

### Basic Workflow (iOS)

```yaml
name: Maestro E2E Tests
on:
  pull_request:
    branches: [main]

jobs:
  e2e-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm install

      - name: Install Maestro
        run: |
          curl -fsSL "https://get.maestro.mobile.dev" | bash
          echo "$HOME/.maestro/bin" >> $GITHUB_PATH

      - name: Build iOS app
        run: npx expo run:ios --configuration Release

      - name: Run Maestro tests
        run: maestro test --format junit --output report.xml maestro/

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: maestro-report
          path: report.xml
```

### Basic Workflow (Android)

```yaml
  e2e-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm install

      - name: Install Maestro
        run: |
          curl -fsSL "https://get.maestro.mobile.dev" | bash
          echo "$HOME/.maestro/bin" >> $GITHUB_PATH

      - name: Setup Android Emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          target: google_apis
          arch: x86_64
          script: |
            npx expo run:android --variant release
            maestro test --format junit --output report.xml maestro/

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: maestro-report
          path: report.xml
```

## Maestro Cloud

For running tests without managing infrastructure:

```bash
# Login (one-time)
maestro login

# Run in cloud
maestro cloud --app-file app.apk maestro/
maestro cloud --app-file app.app maestro/

# With JUnit report
maestro cloud --format junit --app-file app.apk maestro/
```

## EAS Build + Maestro

For Expo apps using EAS Build, run Maestro tests after building:

```yaml
# In GitHub Actions after EAS build
- name: Download build
  run: eas build:list --json --limit 1 --platform ios | jq -r '.[0].artifacts.buildUrl'

- name: Install on simulator
  run: |
    xcrun simctl install booted path/to/app.app
    maestro test maestro/
```

## Tips

- **Tag flows for CI**: Use `tags: [smoke]` on critical flows, run only smoke tests on PRs
- **Full suite on merge**: Run all flows on merge to main
- **Parallel execution**: Maestro Cloud supports parallel flow execution
- **Retry flaky tests**: Use `maestro test --retries 2` for CI stability
- **Environment variables**: Pass secrets via CI env vars with `-e` flag
