---
name: eas
description: Build, submit, and update React Native/Expo apps using EAS (Expo Application Services). Use when working with EAS Build, EAS Submit, EAS Update, managing app store deployments, configuring eas.json, setting up CI/CD for mobile apps, handling iOS/Android credentials, or automating mobile app releases. Covers both iOS and Android platforms with comprehensive CI/CD integration patterns.
---

<objective>
Master Expo Application Services (EAS) for professional mobile CI/CD pipelines. Build app binaries, submit to app stores, deploy over-the-air updates, and automate the entire mobile release workflow for both iOS and Android platforms.
</objective>

<quick_start>
<installation>
```bash
# Install EAS CLI globally
npm install -g eas-cli

# Login to Expo account
eas login

# Verify authentication
eas whoami
```
</installation>

<first_build>
```bash
# Configure project for EAS Build
eas build:configure

# Build for specific platform
eas build --platform ios
eas build --platform android
eas build --platform all

# Build with custom profile and message
eas build --platform ios --profile production --message "Release v1.2.0"
```
</first_build>

<common_commands>
```bash
# Submit to app stores
eas submit --platform ios
eas submit --platform android

# Build and auto-submit
eas build --platform ios --auto-submit

# Publish OTA update
eas update --channel production --message "Bug fixes"

# Check build status
eas build:list

# View credentials
eas credentials
```
</common_commands>
</quick_start>

<context>
<what_is_eas>
Expo Application Services (EAS) provides a professional mobile CI/CD pipeline with three integrated services:

- **EAS Build**: Hosted service for building iOS and Android app binaries with automatic credential management
- **EAS Submit**: Streamlined app store submission to Apple App Store and Google Play Store
- **EAS Update**: Over-the-air (OTA) updates for JavaScript, styling, and assets without app store review

These services work together to manage the entire app lifecycle from development through production.
</what_is_eas>

<when_to_use>
Use EAS when you need to:

- Build native app binaries without local Xcode/Android Studio setup
- Automate app store submissions as part of CI/CD
- Deploy quick fixes and updates without waiting for app store review
- Manage multiple build variants (development, preview, production)
- Share preview builds with internal testers via URLs
- Handle iOS provisioning profiles and Android keystores automatically
- Coordinate team deployments with centralized credential management
</when_to_use>

<key_concepts>
**Build Profiles**: Named configurations in `eas.json` defining build settings (development, preview, production)

**Channels**: Update distribution paths that connect builds to specific update streams (like Git branches)

**Credentials**: Automatically managed signing certificates (iOS) and keystores (Android) stored securely in EAS

**Runtime Version**: Version identifier determining update compatibility with specific builds

**Development Client**: Custom development build with `expo-dev-client` for testing native code changes

**Internal Distribution**: Share builds via URL without app store submission for internal testing
</key_concepts>
</context>

<workflow>
<typical_development_flow>
**Phase 1: Initial Setup**
1. Install EAS CLI: `npm install -g eas-cli`
2. Authenticate: `eas login`
3. Configure project: `eas build:configure`
4. Set up EAS Update: `eas update:configure`

**Phase 2: Development Builds**
1. Create development build: `eas build --profile development --platform ios`
2. Install on device/simulator from build dashboard
3. Make code changes locally
4. Test with `npx expo start --dev-client`
5. Publish updates: `eas update --channel development`

**Phase 3: Preview/Staging**
1. Build preview: `eas build --profile preview --platform all`
2. Share with testers via internal distribution URL
3. Collect feedback and iterate
4. Publish preview updates: `eas update --channel preview`

**Phase 4: Production Release**
1. Build production: `eas build --profile production --platform all`
2. Submit to stores: `eas submit --platform all --profile production`
3. For iOS: Build goes to TestFlight automatically
4. For Android: Build uploads to specified track (internal/alpha/beta/production)
5. Monitor adoption via deployment dashboard

**Phase 5: Post-Release Updates**
1. Fix bugs or add minor features
2. Publish OTA update: `eas update --channel production --message "Bug fixes"`
3. Updates download automatically on next app launch
4. Roll back if needed by republishing previous update
</typical_development_flow>

<app_store_first_submission>
**Critical: Manual first upload required for Android**

Google Play Store API requires the first APK/AAB to be uploaded manually through the Google Play Console. After the initial manual upload, EAS Submit can handle all subsequent updates.

**iOS**: No manual upload required. EAS Submit works from the first submission.

**Steps for Android first upload**:
1. Build APK: `eas build --platform android --profile production`
2. Download APK from build dashboard
3. Go to Google Play Console → Create app
4. Navigate to Production → Create new release
5. Upload APK manually
6. Complete store listing information
7. Submit for review
8. After approval, use `eas submit` for all future updates
</app_store_first_submission>
</workflow>

<eas_json_configuration>
<basic_structure>
The `eas.json` file lives in your project root and configures build and submit profiles:

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development"
    },
    "preview": {
      "distribution": "internal",
      "channel": "preview"
    },
    "production": {
      "channel": "production"
    }
  },
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890"
      },
      "android": {
        "track": "production",
        "releaseStatus": "completed"
      }
    }
  }
}
```
</basic_structure>

<common_build_properties>
**All platforms**:
- `channel`: EAS Update channel for this build profile
- `distribution`: "store" or "internal"
- `developmentClient`: true for development builds
- `env`: Environment variables for build process
- `node`: Node.js version
- `resourceClass`: "default", "medium", or "large" (build machine size)

**iOS-specific**:
- `simulator`: true for iOS Simulator builds
- `bundleIdentifier`: Override bundle ID
- `buildConfiguration`: "Release" or "Debug"

**Android-specific**:
- `buildType`: "app-bundle" (default) or "apk"
- `gradleCommand`: Custom Gradle build command

See [references/eas-json-schema.md](references/eas-json-schema.md) for complete configuration reference.
</common_build_properties>
</eas_json_configuration>

<security>
<credential_management>
**Never commit credentials to version control**

EAS handles credentials securely:
- iOS provisioning profiles and distribution certificates
- Android keystores and upload keys
- App Store Connect API keys
- Google Play service account keys

View credentials: `eas credentials`
Configure manually: `eas credentials --platform ios`
</credential_management>

<ci_cd_authentication>
For CI/CD pipelines, use personal access tokens instead of username/password:

**Generate token**:
1. Visit https://expo.dev/accounts/[account]/settings/access-tokens
2. Create new token with appropriate scope
3. Store as `EXPO_TOKEN` environment variable in CI platform

**GitHub Actions example**:
```yaml
- name: Setup Expo
  uses: expo/expo-github-action@v8
  with:
    token: ${{ secrets.EXPO_TOKEN }}

- name: Build
  run: eas build --platform all --non-interactive
```

**Never hardcode tokens in workflows or commit them to repositories.**
</ci_cd_authentication>

<environment_variables>
Use `env` in build profiles for sensitive configuration:

```json
{
  "build": {
    "production": {
      "env": {
        "API_URL": "https://api.production.com",
        "SENTRY_DSN": "$SENTRY_DSN"
      }
    }
  }
}
```

Reference environment variables from CI platform with `$VAR_NAME` syntax. EAS substitutes values at build time.
</environment_variables>
</security>

<common_patterns>
<multi_environment_setup>
```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development",
      "env": {
        "APP_ENV": "development",
        "API_URL": "http://localhost:3000"
      }
    },
    "staging": {
      "distribution": "internal",
      "channel": "staging",
      "env": {
        "APP_ENV": "staging",
        "API_URL": "https://staging-api.example.com"
      }
    },
    "production": {
      "channel": "production",
      "env": {
        "APP_ENV": "production",
        "API_URL": "https://api.example.com"
      }
    }
  }
}
```
</multi_environment_setup>

<auto_version_increment>
```json
{
  "build": {
    "production": {
      "autoIncrement": true,
      "ios": {
        "buildConfiguration": "Release"
      }
    }
  }
}
```

Auto-increment bumps version numbers automatically on each build, preventing app store rejections due to duplicate version numbers.
</auto_version_increment>

<github_actions_workflow>
```yaml
name: EAS Build and Submit

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - uses: expo/expo-github-action@v8
        with:
          token: ${{ secrets.EXPO_TOKEN }}

      - run: npm ci

      - name: Build and Submit iOS
        run: |
          eas build --platform ios --profile production --non-interactive --auto-submit

      - name: Build and Submit Android
        run: |
          eas build --platform android --profile production --non-interactive --auto-submit
```

Use `--non-interactive` for CI environments to prevent interactive prompts. Use `--no-wait` to avoid blocking CI while builds run on EAS infrastructure.
</github_actions_workflow>
</common_patterns>

<eas_update_patterns>
<publishing_updates>
```bash
# Publish to specific channel
eas update --channel production --message "Fixed login bug"

# Publish to branch (advanced)
eas update --branch main --message "Feature update"

# Publish with specific runtime version
eas update --channel production --runtime-version 1.0.0
```
</publishing_updates>

<rollback_procedure>
```bash
# List all updates for a branch
eas update:list --branch main

# Republish a previous update
eas update:republish --group <update-group-id>
```

Republishing a previous update effectively rolls back to that version, similar to reverting a Git commit.
</rollback_procedure>

<channel_management>
Channels connect builds to update streams. Set channel in `eas.json` build profile:

```json
{
  "build": {
    "production": {
      "channel": "production"
    },
    "preview": {
      "channel": "preview"
    }
  }
}
```

Builds on the "production" channel only receive updates published to that channel. This prevents preview updates from reaching production users.
</channel_management>
</eas_update_patterns>

<validation>
<verify_build_success>
After running `eas build`:

1. Build starts and returns a dashboard URL
2. Monitor progress: Click URL or run `eas build:list`
3. Wait for "Finished" status (builds take 10-30 minutes)
4. Download artifact or proceed to submit
5. For development builds: Install on device via dashboard QR code

**Build failures**: Check build logs via dashboard for detailed error messages
</verify_build_success>

<verify_submission>
After running `eas submit`:

**iOS**:
1. Submission completes within minutes
2. Check TestFlight via App Store Connect
3. Build appears in TestFlight within 5-10 minutes after processing
4. For production: Manually submit for App Review from App Store Connect

**Android**:
1. Submission uploads to specified track
2. Verify in Google Play Console → Release dashboard
3. For internal/alpha/beta: Available immediately to testers
4. For production: Submit for review or configure staged rollout
</verify_submission>

<verify_updates>
After publishing `eas update`:

1. Command completes with update group ID
2. View deployment dashboard: https://expo.dev
3. Check "Deployments" tab for update status
4. Updates download on next app launch (cold start)
5. Use Updates API to test: `Updates.checkForUpdateAsync()`

**Testing updates locally**:
- Build development client with matching channel
- Publish update to that channel
- Force-close and reopen app to trigger update check
- Use Expo Orbit for easier testing
</verify_updates>
</validation>

<anti_patterns>
<common_mistakes>
**Don't mix development and production credentials**: Keep separate Apple Developer accounts or Google Play Console projects for testing vs production when possible.

**Don't skip runtime version management**: Failing to update `runtimeVersion` when making native changes breaks OTA updates. Updates require binary compatibility.

**Don't hardcode environment variables**: Use `env` in `eas.json` and reference CI secrets. Never commit API keys or tokens.

**Don't forget the manual Android first upload**: EAS Submit fails if no app exists in Google Play Console. Upload first APK manually.

**Don't use `--auto-submit` without configuring submit profiles**: Ensure `eas.json` has proper submit configuration before using auto-submit flags.

**Don't block CI waiting for builds**: Use `--no-wait` flag in CI to avoid consuming CI minutes while EAS builds run.

**Don't publish updates with breaking changes**: OTA updates can only modify JavaScript/assets. Native changes require new builds.
</common_mistakes>
</anti_patterns>

<reference_guides>
For comprehensive details, see:

**EAS Build deep dive**: [references/eas-build.md](references/eas-build.md)
- Platform-specific build configurations
- Custom build workflows
- Development client setup
- Build artifact management

**EAS Submit guide**: [references/eas-submit.md](references/eas-submit.md)
- iOS App Store submission process
- Android Google Play submission process
- Automated submission workflows
- TestFlight and track management

**EAS Update reference**: [references/eas-update.md](references/eas-update.md)
- Runtime version management
- Branch and channel strategies
- Update deployment patterns
- Rollback procedures

**eas.json schema**: [references/eas-json-schema.md](references/eas-json-schema.md)
- Complete configuration reference
- All build properties
- Submit profile options
- Platform-specific settings

**CI/CD setup**: [references/ci-cd-setup.md](references/ci-cd-setup.md)
- GitHub Actions integration
- GitLab CI patterns
- Generic CI/CD workflows
- Caching strategies

**Credentials management**: [references/credentials-management.md](references/credentials-management.md)
- iOS provisioning profiles and certificates
- Android keystores and service accounts
- App Store Connect API keys
- Secure credential storage

**Troubleshooting**: [references/troubleshooting.md](references/troubleshooting.md)
- Common build failures
- Credential issues
- Update problems
- Platform-specific errors
</reference_guides>

<success_criteria>
You've successfully mastered EAS when you can:

- Configure `eas.json` with multiple build and submit profiles
- Build iOS and Android apps using `eas build` commands
- Submit apps to Apple App Store and Google Play Store via `eas submit`
- Publish over-the-air updates with `eas update` to specific channels
- Set up CI/CD pipelines with `EXPO_TOKEN` authentication
- Manage credentials securely without committing to version control
- Configure multi-environment workflows (development, staging, production)
- Troubleshoot build failures using EAS dashboard logs
- Roll back problematic updates by republishing previous versions
- Share internal builds with testers via distribution URLs
</success_criteria>
