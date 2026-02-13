# EAS Submit Guide

## iOS App Store Submission

### Requirements

Before submitting to Apple App Store:

1. **Apple Developer Account**
   - Enroll at https://developer.apple.com/account/
   - Annual membership fee: $99 USD
   - Create your app in App Store Connect

2. **Bundle Identifier**
   - Must match bundle ID in app.json
   - Must be unique across App Store
   - Format: `com.company.appname`

3. **App Store Connect API Key**
   - Recommended for CI/CD (vs. app-specific password)
   - Generate at https://appstoreconnect.apple.com/access/api
   - Create role with "Developer" or "Admin" access
   - Download API key file and store securely

4. **Required Credentials**
   - App Store Connect App ID (found in App Store Connect)
   - Apple Team ID (found in Apple Developer account)
   - Distribution certificate (auto-managed by EAS)
   - Provisioning profile (auto-managed by EAS)

### Configuration in eas.json

```json
{
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890",
        "appleTeamId": "ABC123XYZ",
        "appleId": "your-email@example.com",
        "appName": "My Cool App",
        "bundleIdentifier": "com.example.mycoolapp",
        "sku": "com.example.mycoolapp"
      }
    }
  }
}
```

**Configuration fields**:
- `ascAppId`: App Store Connect App ID (numeric ID)
- `appleTeamId`: Your Apple Developer Team ID
- `appleId`: Apple ID email (for credentials)
- `appName`: Display name in App Store
- `bundleIdentifier`: Must match app.json
- `sku`: Unique product identifier (auto-generated if omitted)
- `iosDisplayVersion`: Version number (auto-detected if omitted)
- `iosBuildVersion`: Build number (auto-detected if omitted)

### Finding Your App ID in App Store Connect

1. Log in to https://appstoreconnect.apple.com
2. Navigate to "Apps" section
3. Select your app
4. Go to "App Information"
5. Look for "Apple ID" under General Information
6. This is your `ascAppId`

### Submission Process

```bash
# Interactive submission (EAS asks for credentials)
eas submit --platform ios

# Specify profile and auto-submit
eas submit --platform ios --profile production

# With API key authentication (CI/CD)
export EXPO_ASC_API_KEY_PATH="/path/to/api-key.p8"
export EXPO_ASC_KEY_ID="ABC123"
export EXPO_ASC_ISSUER_ID="xyz-123"
eas submit --platform ios --non-interactive
```

### What Happens During Submission

1. Uploads `.ipa` file to App Store Connect
2. Build appears in TestFlight automatically
3. Build available for internal testing immediately
4. Processing takes 5-30 minutes
5. You receive notification when processing complete

### TestFlight Distribution

After EAS Submit completes, build is available in TestFlight:

1. Log in to App Store Connect
2. Select your app → TestFlight
3. Select "Builds" tab
4. Build appears under "Available iOS Builds"
5. Add testers or invite via public link
6. Testers receive notification to test via TestFlight app

**TestFlight options**:
- **Internal Testing**: Up to 25 users (team members)
- **External Testing**: Up to 10,000 beta testers
- **Public Link**: Share one-time download link without adding testers

### App Store Review Submission

**Important**: EAS Submit uploads to TestFlight, but does NOT submit to App Store Review.

To submit for production release:

1. Log in to App Store Connect
2. Select your app → TestFlight
3. Select the build
4. Click "Submit for Review"
5. Complete compliance information (IDFA, encryption, etc.)
6. Submit for review

Review takes 24-48 hours (sometimes longer during holidays).

## Android Google Play Submission

### Requirements

Before submitting to Google Play Store:

1. **Google Play Developer Account**
   - Register at https://play.google.com/apps/publish/signup/
   - One-time fee: $25 USD
   - Valid payment method required

2. **Package Name**
   - Must match package name in app.json
   - Must be unique across Google Play
   - Format: `com.company.appname`

3. **Google Play Service Account**
   - Create at Google Cloud Console
   - Grant "Basic" access to Play Console
   - Download JSON key file
   - Required for EAS Submit automation

4. **App Entry in Google Play Console**
   - Create app and fill basic information
   - Upload privacy policy URL
   - Complete store listing

5. **Manual First Upload Required**
   - Google Play API limitation
   - First APK/AAB must be uploaded manually
   - All subsequent updates use EAS Submit

### Configuration in eas.json

```json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./google-play-service-account.json",
        "track": "production",
        "releaseStatus": "completed",
        "rollout": 1.0
      }
    }
  }
}
```

**Configuration fields**:
- `serviceAccountKeyPath`: Path to Google Play service account JSON
- `track`: "internal", "alpha", "beta", or "production"
- `releaseStatus`: "completed", "draft", "inProgress", "halted"
- `rollout`: User fraction (0-1) for staged rollout (e.g., 0.1 for 10%)
- `changesNotSentForReview`: Skip automatic review submission if true

### Creating Google Play Service Account

1. Go to https://play.google.com/apps/publish
2. Settings → Your Profile or API access → Create service account
3. Follow Google Cloud Console link
4. Create new service account
5. Grant "Basic" access to Play Console
6. Create JSON key
7. Download and save securely

Or use Expo documentation: https://github.com/expo/fyi/blob/main/creating-google-service-account.md

### Submission Process

```bash
# Interactive submission
eas submit --platform android

# Specify profile
eas submit --platform android --profile production

# Automated submission
eas build --platform android --auto-submit

# CI/CD with service account
eas submit --platform android --profile production --non-interactive
```

**Important**: Service account key must have access to your Google Play app.

### What Happens During Submission

1. Uploads AAB or APK to specified track
2. Verifies signature and manifest
3. Processing takes 5-30 minutes
4. Build available to testers on specified track

### Track Management

Android uses "tracks" to manage release stages:

- **Internal**: Internal testing (team members)
- **Alpha**: Limited external testing
- **Beta**: Broader testing
- **Production**: Public release

```json
{
  "submit": {
    "alpha": {
      "android": {
        "track": "alpha",
        "releaseStatus": "completed"
      }
    },
    "production": {
      "android": {
        "track": "production",
        "releaseStatus": "completed",
        "rollout": 0.5
      }
    }
  }
}
```

### Staged Rollout

Gradually roll out updates to users:

```json
{
  "submit": {
    "production": {
      "android": {
        "track": "production",
        "releaseStatus": "inProgress",
        "rollout": 0.1
      }
    }
  }
}
```

- `rollout: 0.1` = 10% of users
- `rollout: 0.5` = 50% of users
- `rollout: 1.0` = 100% of users (full release)

Update rollout percentage in Play Console after initial submission.

### Manual First Upload

The Android Play Store API requires first upload to be manual:

1. Go to Google Play Console
2. Select your app → Release → Production
3. Create new release
4. Upload APK/AAB manually
5. Fill required information (content rating, etc.)
6. Save as draft or submit for review
7. After first upload is in Play Console, `eas submit` works for future uploads

## Automated Submission in CI/CD

### EAS Auto-Submit

```bash
# After successful build, automatically submit
eas build --platform all --auto-submit

# With specific profile
eas build --platform ios --profile production --auto-submit --auto-submit-with-profile=production
```

**Behavior**:
- Builds then immediately submits with matching profile
- iOS: Submits to TestFlight
- Android: Submits to specified track
- Fails if submit profile not configured in eas.json

### GitHub Actions Workflow

```yaml
name: Build and Submit

on:
  push:
    tags:
      - 'v*'

jobs:
  submit:
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

      - name: Build and Submit
        run: eas build --platform all --auto-submit --non-interactive
        env:
          EXPO_ASC_API_KEY_PATH: ${{ secrets.ASC_API_KEY }}
          EXPO_ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          EXPO_ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
```

### Credential Management in CI/CD

**iOS credentials**:
- `EXPO_TOKEN`: Expo personal access token
- `EXPO_ASC_API_KEY_PATH`: Path to App Store Connect API key file
- `EXPO_ASC_KEY_ID`: API Key ID
- `EXPO_ASC_ISSUER_ID`: API Key Issuer ID
- `EXPO_APPLE_TEAM_ID`: Apple Team ID

**Android credentials**:
- `EXPO_TOKEN`: Expo personal access token
- Service account JSON stored in EAS (credentials command)

## Common Submission Issues

### App Already Submitted for Review (iOS)

If TestFlight build is already in review, you cannot submit again until review completes.

**Solution**:
1. Wait for App Review decision
2. Or build new version with bumped version number
3. Use `autoIncrement: true` to auto-bump

### Insufficient Permissions (Android)

Service account lacks Play Console access.

**Solution**:
1. Check Google Cloud service account has "Basic" access to Play Console
2. Verify Play Console settings granted access
3. Try removing and re-adding service account

### Manual First Upload Not Done (Android)

`eas submit` fails if app doesn't exist in Play Console.

**Solution**:
1. Log in to Google Play Console
2. Create app entry
3. Upload first APK/AAB manually
4. Then `eas submit` works for future uploads

### Build Not Found

Trying to submit when build doesn't exist.

**Solution**:
```bash
# Build first
eas build --platform ios

# Then submit after build completes
eas submit --platform ios
```

### Invalid Bundle ID

Bundle ID in app.json doesn't match configured bundle ID.

**Solution**:
1. Update app.json with correct bundle ID
2. Rebuild and re-submit

## Version Management

Version numbers must be unique per submission:

**iOS**:
- `iosDisplayVersion` (e.g., "1.2.3")
- `iosBuildVersion` (e.g., "42")

**Android**:
- `versionName` (e.g., "1.2.3")
- `versionCode` (e.g., "42")

Use `autoIncrement: true` in build profile to automatically increment build numbers.

Or manually update in app.json:

```json
{
  "version": "1.0.1",
  "ios": {
    "buildNumber": "5"
  },
  "android": {
    "versionCode": 5
  }
}
```

## Metadata Updates

For metadata changes (screenshots, description, etc.), use:

```bash
eas metadata:pull
# Edit files
eas metadata:push
```

Or update directly in App Store Connect and Google Play Console web interfaces.
