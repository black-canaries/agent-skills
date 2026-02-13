# Credentials Management Guide

## Overview

EAS securely manages signing credentials for iOS and Android apps. You don't need to manage certificates, provisioning profiles, or keystores manually—EAS handles this automatically.

## iOS Credentials

### What EAS Manages

- **Distribution Certificates**: Sign app for App Store submission
- **Provisioning Profiles**: Authorize app to run on devices
- **App IDs**: Unique identifiers in Apple Developer account
- **Ad Hoc Certificates**: For internal distribution

EAS creates and renews these automatically. You provide:
1. Apple Developer account access
2. App Store Connect credentials
3. Apple Team ID

### Initial iOS Setup

```bash
# First-time iOS build configuration
eas build:configure --platform ios

# This will:
# 1. Ask for Apple Developer credentials
# 2. Create/use existing provisioning profiles
# 3. Set up distribution certificates
```

**What you need**:
1. Apple Developer account
2. Apple ID email
3. App Store Connect API key (recommended for automation)

### Viewing iOS Credentials

```bash
# View all credentials
eas credentials

# View iOS credentials only
eas credentials --platform ios

# Output shows:
# - Distribution certificate expiration
# - Provisioning profile status
# - Last updated timestamp
```

### Renewing iOS Certificates

Certificates expire after 1-3 years. Renew before expiration:

```bash
# Regenerate certificates and profiles
eas credentials --platform ios
```

**Options**:
1. Keep existing (if still valid)
2. Revoke and generate new
3. Upload existing certificate from Apple Developer account

### Using Existing iOS Certificates

If you have existing distribution certificate and provisioning profile:

```bash
# During initial setup, choose "Use existing"
eas credentials --platform ios

# Upload:
# - Distribution certificate (.p12 or .cer file)
# - Provisioning profile (.mobileprovision file)
# - Certificate password
```

Get these from Apple Developer account:
1. Log in to https://developer.apple.com/account/resources/certificates
2. Find your distribution certificate
3. Download and save
4. Go to Profiles section
5. Download provisioning profile

### App Store Connect API Key Setup

For automation (CI/CD), use App Store Connect API key instead of password:

**Generate API key**:
1. Log in to https://appstoreconnect.apple.com/access/api
2. Click "Generate API Key"
3. Select role: "Developer" or "Admin"
4. Download `.p8` file (keep secure!)
5. Note down Key ID and Issuer ID

**Store securely**:
```bash
# Save to secure location (not in repo)
mv ~/Downloads/AuthKey_*.p8 ~/.eas/keys/
chmod 600 ~/.eas/keys/AuthKey_*.p8
```

**Use in CI/CD**:
```yaml
# GitHub Actions
env:
  EXPO_ASC_API_KEY_PATH: ${{ runner.temp }}/asc-api-key.p8
  EXPO_ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
  EXPO_ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
```

**Never commit `.p8` file to version control!**

## Android Credentials

### What EAS Manages

- **Keystore**: Signed keystore file for app signing
- **Upload Key**: For Play Store submissions
- **Key Aliases and Passwords**: Stored securely in EAS

EAS can generate these or you can provide existing ones.

### Initial Android Setup

```bash
# First-time Android build configuration
eas build:configure --platform android

# This will:
# 1. Generate or link existing keystore
# 2. Create upload key if needed
# 3. Store credentials securely
```

**What you need**:
1. Google Play Developer account
2. Service account with Play Console access

### Viewing Android Credentials

```bash
# View all credentials
eas credentials

# View Android credentials
eas credentials --platform android

# Output shows:
# - Keystore alias
# - Key password status
# - Last updated timestamp
```

### Using Existing Android Keystore

If you have existing keystore from previous builds:

```bash
# During setup, choose "Use existing keystore"
eas credentials --platform android

# Upload:
# - Keystore file (.jks or .keystore)
# - Keystore password
# - Key alias
# - Key password
```

**Find your existing keystore**:
1. Check `android/app/build.gradle` for `keyAlias` and password hints
2. Search home directory: `find ~ -name "*.jks" -o -name "*.keystore"`
3. If built locally before, check Android project directory

### Google Play Service Account

For Android app store submissions:

**Create service account**:
1. Go to https://play.google.com/apps/publish
2. Settings → Your profile → API access
3. Click "Create service account"
4. Follow Google Cloud Console link
5. Create new service account
6. Grant "Basic" access to Play Console
7. Create JSON key
8. Download and save securely

Or use Expo FYI guide: https://github.com/expo/fyi/blob/main/creating-google-service-account.md

**Store securely**:
```bash
# Save to secure location (not in repo)
mv ~/Downloads/google-play-key.json ~/.eas/keys/
chmod 600 ~/.eas/keys/google-play-key.json
```

**Reference in eas.json**:
```json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./keys/google-play-key.json"
      }
    }
  }
}
```

**For CI/CD**, commit path reference but NOT the key file:

```json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "${{ secrets.GOOGLE_PLAY_KEY_PATH }}"
      }
    }
  }
}
```

## Credential Security Best Practices

### Never Commit Credentials

Add to `.gitignore`:
```
# Credential files
*.p8
*.p12
*.jks
*.keystore
google-play-key.json
google-play-service-account.json
asc-api-key.p8
.eas/credentials.json
```

### Use CI/CD Secrets for Automation

Store credentials in CI platform secrets, not in code:

**GitHub Actions**:
```yaml
env:
  EXPO_ASC_API_KEY_PATH: ${{ runner.temp }}/asc-api-key.p8
  EXPO_ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
  GOOGLE_PLAY_KEY: ${{ secrets.GOOGLE_PLAY_KEY }}
```

**GitLab CI**:
```yaml
env:
  EXPO_ASC_API_KEY_PATH: $CI_PROJECT_DIR/asc-api-key.p8
  ASC_KEY_ID: $ASC_KEY_ID
variables:
  ASC_KEY_ID:
    value: "ABC123"
    protected: true
```

Protected variables are masked in logs.

### Rotate Credentials Periodically

Best practice: Rotate credentials every 1-2 years

```bash
# Regenerate iOS certificates
eas credentials --platform ios

# Regenerate Android keystore
eas credentials --platform android
```

### Team Credential Management

For team projects:

1. **EAS Account Ownership**: One person manages credentials
2. **Team Access**: Add team members via EAS dashboard
3. **CI/CD Secrets**: Share EXPO_TOKEN with team
4. **Do NOT share**: API keys, keystore passwords

### Backup Credentials Safely

Keep backups of important credentials:

```bash
# Backup iOS provisioning profile and certificate
# Export from Apple Developer account, store securely

# Backup Android keystore
# Never store in cloud without encryption
# Keep locally or on encrypted drive
```

## Credential Expiration

### iOS Certificate Expiration

Distribution certificates expire after 1 year. EAS notifies you before expiration:

1. Check EAS dashboard for expiration warning
2. Regenerate when approaching expiration
3. Old apps can still be updated until 90 days after expiration

### Android Keystore Expiration

Upload key valid for 20+ years (typically no renewal needed).

Check expiration:
```bash
# Android keystore detail
keytool -list -v -keystore ./android/app/my-release-key.jks
```

## Credential Issues and Solutions

### Certificate Not Found During Build

**Error**: "No distribution certificate found"

**Solution**:
1. Run `eas credentials --platform ios`
2. Choose "Create new certificate"
3. Rebuild: `eas build --platform ios`

### Permission Denied (Service Account)

**Error**: "403 Forbidden - insufficient permission"

**Solution**:
1. Go to Google Play Console
2. Settings → User and permissions
3. Verify service account has "Admin" role
4. For first submission, upload first APK manually

### Keystore Password Incorrect

**Error**: "Keystore was tampered with, or password was incorrect"

**Solution**:
1. If you know password: `eas credentials --platform android`
2. Choose "Use existing keystore" and re-enter
3. If password lost:
   - Generate new keystore: `eas credentials --platform android`
   - Choose "Create new keystore"
   - Increment app version code
   - New builds will use new key

### API Key Expired or Revoked

**Error**: "ASC API authentication failed"

**Solution**:
1. Go to App Store Connect → Access → API Keys
2. Check if key is revoked
3. Revoke old key and create new one
4. Update `EXPO_ASC_KEY_ID` in CI/CD secrets

## Managing Credentials Across Environments

### Development vs Production

Keep separate credentials when possible:

**Development**:
```bash
# Create dev certificate (ad-hoc/simulator)
eas credentials --platform ios
```

**Production**:
```bash
# Create production certificate (App Store)
eas credentials --platform ios
```

### Multiple Apps

Each app has separate credentials:

```bash
# App 1 credentials
eas build:configure --platform ios

# Switch to App 2 project
cd ../app2

# App 2 credentials
eas build:configure --platform ios
```

Credentials are stored per project.

## Troubleshooting Credential Issues

### Verify Credentials Are Stored

```bash
# List stored credentials
eas credentials

# View details
eas credentials --platform ios
eas credentials --platform android
```

### Repair Credentials

If credentials become invalid:

```bash
# For iOS
eas credentials --platform ios
# Choose "Revoke and create new"

# For Android
eas credentials --platform android
# Choose "Create new keystore"
```

### Reset All Credentials

⚠️ Warning: This invalidates all stored credentials

```bash
eas credentials --clear-all
```

After clearing:
1. Reconfigure: `eas build:configure`
2. Rebuild: `eas build --platform all`
3. Test thoroughly before production

## Compliance and Audit

### Track Credential Changes

EAS dashboard shows:
- When certificates were created/updated
- Expiration dates
- Certificate status

### Audit Trail

For team projects:
1. Visit EAS dashboard
2. Go to Credentials section
3. View history of changes
4. See which team member made updates

### Export Credentials Securely

You cannot export credentials from EAS (by design).

To backup:
1. Securely store original certificate files
2. Keep backup of keystore file
3. Document passwords separately
4. Use encrypted storage

## Security Compliance

### HIPAA, SOC 2, Enterprise

If subject to compliance requirements:

1. **Credential Access**: Limit to necessary team members
2. **Audit Logging**: Track all credential access
3. **Encryption**: EAS encrypts credentials in transit and at rest
4. **Rotation**: Rotate credentials as required
5. **Documentation**: Keep records of credential management

For compliance guidance, contact Expo support.

## Advanced: Custom Credential Workflows

### Using Local Credentials (Advanced)

For special cases, use local build:

```bash
# Build locally with local credentials
eas build --platform android --local

# Requires local Android SDK setup
# Use EAS for signing/submission only
```

### Credential-Less Builds

For testing/development:

```bash
{
  "build": {
    "development": {
      "withoutCredentials": true
    }
  }
}
```

Builds without credentials for internal testing only (not for app stores).
