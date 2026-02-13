# EAS Update Reference

## Overview

EAS Update enables over-the-air (OTA) updates for JavaScript, styling, and asset changes without requiring app store submission. Updates automatically download on app launch and apply the next time the user restarts the app.

**What can be updated**: JavaScript code, stylesheets, images, fonts, and other assets

**What cannot be updated**: Native code changes require new builds

## Initial Setup

### Installation

```bash
# Install required dependency
npx expo install expo-updates

# Configure EAS Update
eas update:configure

# Login to ensure authentication
eas login
eas whoami
```

### Configuration in app.json

The `eas update:configure` command adds:

```json
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/[projectId]"
    },
    "runtimeVersion": {
      "policy": "appVersion"
    }
  }
}
```

**Important fields**:
- `updates.url`: EAS Update service endpoint (auto-configured)
- `runtimeVersion`: Determines update compatibility

### Runtime Version Management

Runtime version controls which app binaries can receive which updates.

**Policy options**:

```json
{
  "runtimeVersion": {
    "policy": "appVersion"
  }
}
```

Uses app version from app.json. Update app version when making native changes.

```json
{
  "runtimeVersion": {
    "policy": "nativeVersion"
  }
}
```

Uses native build number. More granular control.

```json
{
  "runtimeVersion": "1.0.0"
}
```

Explicit version string. Prevents updates to incompatible binaries.

## Publishing Updates

### Basic Update Publishing

```bash
# Publish to default channel
eas update

# Publish to specific channel
eas update --channel production --message "Bug fixes"

# Publish to branch
eas update --branch main --message "Feature update"

# List available channels
eas update:list
```

### Update Channels

Channels connect builds to update streams. Use channels to control which users receive which updates:

```json
{
  "build": {
    "development": {
      "channel": "development"
    },
    "staging": {
      "channel": "staging"
    },
    "production": {
      "channel": "production"
    }
  }
}
```

**Best practices**:
- Development build on `development` channel
- Staging build on `staging` channel
- Production build on `production` channel
- Only publish to matching channel
- Never publish updates to `production` channel unless tested

### Branches vs Channels

**Channels**: Named distribution paths (development, staging, production)

**Branches**: Advanced feature for managing update history (main, feature-x, etc.)

For most use cases, use channels. Branches are for advanced workflows.

## Update Process and Timeline

### What Happens When App Launches

1. App starts
2. Checks EAS Update service for new update on channel
3. If new update found:
   - Downloads update bundle
   - Extracts and validates
   - Stores for next app start
4. On next app start, launches new update

### Update Timeline

**User perspective**:
```
Build 1 (v1.0) installed
↓
Publish update → User sees v1.0 (update downloading)
↓
User force-closes app
↓
App restarts → Launches v1.1 (new update applied)
```

**Key point**: Updates apply on next app restart, not immediately.

### Instant Updates with Updates API

For immediate update application:

```jsx
import * as Updates from 'expo-updates';
import { useEffect } from 'react';

export function App() {
  useEffect(() => {
    const checkForUpdates = async () => {
      try {
        const update = await Updates.checkForUpdateAsync();
        if (update.isAvailable) {
          await Updates.fetchUpdateAsync();
          // Prompt user to restart
          // Then call await Updates.reloadAsync()
        }
      } catch (error) {
        console.error('Error checking for updates:', error);
      }
    };

    checkForUpdates();
  }, []);

  return {/* your app */};
}
```

**Use cases**:
- Critical security fixes
- Major feature releases
- Breaking changes

## Testing Updates Locally

### Development Client Testing

```bash
# Build development client with specific channel
eas build --platform ios --profile development --channel development

# Publish update to that channel
eas update --channel development --message "Test update"

# Install development build on simulator/device

# Force-close app (don't just exit)
# Reopen app → new update applies
```

### Expo Orbit Testing

Easier way to test updates:

1. Install Expo Orbit from App Store
2. Build development client: `eas build --platform ios --profile development`
3. Publish update: `eas update --channel development`
4. Orbit app shows available builds
5. Install and test

## Rollback and Rollout Control

### List Available Updates

```bash
# List updates for specific branch
eas update:list --branch main

# Output shows update group ID, timestamp, message
```

### Rollback to Previous Update

```bash
# Get update group ID from eas update:list output
eas update:republish --group [group-id]
```

Republishing previous update effectively rolls back to that version.

### Staged Rollout

```bash
# Publish with limited rollout (10% of users)
eas update --channel production

# Then in deployment dashboard:
# 1. View update details
# 2. Adjust rollout percentage
# 3. Gradually increase from 10% → 50% → 100%
```

**Dashboard location**: https://expo.dev → Your app → Updates

## Update Channels Strategy

### Single Channel (Simple)

```bash
# All environments use same channel
eas update --channel default
```

Good for small teams or simple workflows.

### Multi-Channel (Recommended)

```bash
# Development
eas update --channel development --message "WIP: new feature"

# Staging (before production)
eas update --channel staging --message "Release candidate"

# Production
eas update --channel production --message "v1.5.0 release"
```

**Workflow**:
1. Publish to `development` channel for internal testing
2. After testing, republish same update to `staging`
3. Monitor staging briefly
4. Republish to `production` for all users

## Advanced Patterns

### Conditional Updates

```jsx
import * as Updates from 'expo-updates';

export async function checkForUpdates() {
  const update = await Updates.checkForUpdateAsync();

  if (update.isAvailable) {
    // Custom logic: ask user, check network, etc.
    const shouldUpdate = await promptUserForUpdate();

    if (shouldUpdate) {
      await Updates.fetchUpdateAsync();
      await Updates.reloadAsync();
    }
  }
}
```

### Version Comparison

```jsx
import Constants from 'expo-constants';
import * as Updates from 'expo-updates';

export async function checkUpdate() {
  const currentVersion = Constants.expoConfig.version;
  const update = await Updates.checkForUpdateAsync();

  if (update.isAvailable) {
    console.log('Current:', currentVersion);
    console.log('Available:', update.manifest.version);
    // Custom comparison logic
  }
}
```

### Using Multiple Branches

```bash
# Main branch (production)
eas update --branch main --message "Release"

# Feature branch (testing)
eas update --branch feature-dark-mode --message "Dark mode beta"

# Users on feature build receive feature updates
# Users on main build receive main updates
```

## Common Patterns

### Hot Fix Workflow

```bash
# Production app has bug
# Quickly publish fix without rebuilding

eas update --channel production --message "Hotfix: login crash"

# Users receive update on next app launch
```

### A/B Testing

```bash
# Create two updates
eas update --branch a --message "Version A"
eas update --branch b --message "Version B"

# Build two production builds pointing to different branches
# Track metrics per branch in analytics
```

### Gradual Rollout

```bash
# Publish update
eas update --channel production --message "v2.0"

# Dashboard shows "Rollout controls"
# Start at 10% of users
# Monitor crash reports
# Increase to 50%
# If stable, increase to 100%
```

## Update Manifestation

### What's in an Update

```
update-bundle/
├── metadata.json        # Update metadata
├── index.js.bundle      # JavaScript code
├── assets/
│   ├── images/
│   ├── fonts/
│   └── other files
└── html/                # Web assets (if applicable)
```

Update size typically 1-5 MB depending on app complexity.

### Update Manifest Fields

```json
{
  "version": "1.0.0",
  "createdAt": "2024-01-15T10:30:00Z",
  "runtimeVersion": "1.0.0",
  "launchAsset": {
    "url": "...",
    "contentType": "application/javascript"
  },
  "assets": [
    {
      "url": "...",
      "path": "assets/image.png",
      "contentType": "image/png"
    }
  ]
}
```

## Limitations and Considerations

### Update Scope

Updates can only modify:
- JavaScript code
- Styling
- Images and assets
- Configuration (if using dynamic config)

Updates **cannot** modify:
- Native modules
- Native code
- Xcode/Android Studio projects
- App.json native configuration (requires rebuild)

Native changes require new build via `eas build`.

### Runtime Compatibility

Updates only work on compatible app binaries.

If you make native changes:
1. Update `runtimeVersion`
2. Build new binary: `eas build`
3. Then publish updates

Old builds won't receive updates for new runtime version.

### Update Staleness

Rollback only works for recent updates (typically 30 days). For very old updates, rebuild app binary.

### No Partial Updates

EAS Update is all-or-nothing. You can't update one part of app while skipping another.

## Debugging Updates

### Check Current Update

```jsx
import Constants from 'expo-constants';

console.log('Current update ID:', Constants.expoConfig.runtimeVersion);
console.log('Update URL:', Constants.expoConfig.updates?.url);
```

### Enable Verbose Logging

```bash
# When building
eas build --platform ios --message "debug build" 2>&1 | tee build.log

# Check for update errors in logs
```

### Manual Update Check

```jsx
import * as Updates from 'expo-updates';

async function forceCheckUpdate() {
  try {
    const update = await Updates.checkForUpdateAsync();
    console.log('Update available:', update.isAvailable);
    if (update.isAvailable) {
      console.log('Downloading...');
      await Updates.fetchUpdateAsync();
      console.log('Downloaded. Will apply on next restart');
    }
  } catch (error) {
    console.error('Update error:', error);
  }
}
```

### Dashboard Monitoring

Monitor updates at https://expo.dev:
1. Select your app
2. Go to "Updates" tab
3. View:
   - All published updates
   - Rollout progress
   - Deployment status
   - Update adoption rates

## Integration with Sentry/Analytics

Track update adoption:

```jsx
import * as Updates from 'expo-updates';
import * as Sentry from '@sentry/react-native';

useEffect(() => {
  const trackUpdate = async () => {
    const update = await Updates.checkForUpdateAsync();
    Sentry.captureMessage('Update check', {
      level: 'info',
      extra: {
        updateAvailable: update.isAvailable,
        currentRuntime: Constants.expoConfig.runtimeVersion
      }
    });
  };

  trackUpdate();
}, []);
```

Monitor update metrics to:
- Track adoption rates
- Detect update failures
- Identify problematic versions
