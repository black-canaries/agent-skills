# Troubleshooting Guide

## Build Issues

### Build Stuck in Queue

**Symptom**: Build shows "QUEUED" status for long time

**Causes**:
- Many builds ahead in queue
- Resource capacity limits
- Account limits

**Solutions**:
```bash
# Check build status
eas build:view <build-id>

# Try with smaller resource class
eas build --platform ios --resourceClass default

# Or use larger class for priority
eas build --platform ios --resourceClass large
```

**Prevention**: Limit builds to important commits (main branch, tags only).

### Out of Memory Error

**Symptom**: Build fails with "OutOfMemory" or "Killed"

**Error message**: "JavaScript heap out of memory" or "Process was killed"

**Solutions**:
1. Use larger resource class:
   ```json
   {
     "build": {
       "production": {
         "resourceClass": "large"
       }
     }
   }
   ```

2. Increase Node memory in build:
   ```bash
   export NODE_OPTIONS="--max-old-space-size=4096"
   eas build --platform ios
   ```

3. Optimize bundle size:
   - Remove unused dependencies
   - Split large bundles
   - Use production build flag

### Dependency Resolution Failed

**Symptom**: "npm ERR!" or dependency installation fails

**Common causes**:
- Incompatible package versions
- Missing peer dependencies
- Corrupted package cache

**Solutions**:
```bash
# Try removing lock file and reinstalling
rm package-lock.json
rm node_modules -rf
npm install
eas build --platform ios

# Or use npm ci (cleaner)
npm ci
eas build --platform ios
```

**In eas.json**:
```json
{
  "build": {
    "production": {
      "cache": {
        "key": "v2",
        "paths": ["node_modules/**"]
      }
    }
  }
}
```

Clear cache by changing key: `"v1"` → `"v2"`

### Prebuild Script Failed

**Symptom**: "Prebuild script exited with code 1"

**Causes**:
- Custom prebuild script error
- Native code generation failed
- Platform-specific issues

**Solutions**:
```bash
# Test prebuild locally first
npx expo prebuild --platform ios

# Check prebuild script in eas.json
eas build --platform ios --message "debug"

# View detailed build logs
eas build:view <build-id>
```

**Common prebuild issues**:
- Missing native dependencies
- Incompatible Xcode/Android SDK version
- Custom native code errors

### Xcode/Android SDK Version Mismatch

**Symptom**: "Xcode version incompatible" or "SDK not found"

**Solutions**:
```bash
# Specify compatible versions in eas.json
{
  "build": {
    "production": {
      "ios": {
        "buildConfiguration": "Release",
        "image": "macos-13-xcode-14"
      }
    }
  }
}
```

Check available images: https://docs.expo.dev/build-reference/infrastructure/

## Submission Issues

### App Already Submitted for Review (iOS)

**Symptom**: TestFlight build in "Under Review" state

**Cause**: Cannot submit new build while review in progress

**Solutions**:
```bash
# Option 1: Wait for review decision
# Usually 24-48 hours

# Option 2: Build new version with bumped number
eas build --platform ios --profile production
# Then EAS Submit when ready

# Option 3: Cancel review (if needed)
# Go to App Store Connect → TestFlight → Build
# Click "Cancel Submission" if available
```

### Service Account Insufficient Permissions

**Symptom**: "403 Forbidden" during Android submission

**Causes**:
- Service account lacks Play Console access
- Service account revoked or disabled
- Wrong project selected

**Solutions**:
1. Verify Google Play service account:
   ```bash
   # Check service account in eas.json
   cat eas.json | grep serviceAccountKeyPath
   ```

2. Go to Google Play Console:
   - Settings → User and permissions
   - Find service account in list
   - Verify "Admin" or required role assigned

3. Regenerate if needed:
   - Delete existing service account
   - Create new one with full access
   - Download JSON key
   - Update eas.json path

### Manual First Upload Not Done (Android)

**Symptom**: "App does not exist in Play Console" when submitting

**Cause**: Google Play API requires first upload to be manual

**Solution**:
```bash
# 1. Build production APK
eas build --platform android --profile production

# 2. Go to Google Play Console
# 3. Create app or select existing
# 4. Navigate to: Release → Production
# 5. Create new release
# 6. Upload APK/AAB manually
# 7. Fill required info (content rating, pricing, etc.)
# 8. Save as draft or submit for review

# 9. After first upload, EAS Submit works
eas submit --platform android --profile production
```

### Duplicate Version Number

**Symptom**: "App version already exists" or similar error

**Cause**: App Store/Play Store already has this version

**Solutions**:
1. Auto-increment versions:
   ```json
   {
     "build": {
       "production": {
         "autoIncrement": true
       }
     }
   }
   ```

2. Or manually bump:
   ```json
   {
     "version": "1.0.1"
   }
   ```

3. For Android, increment versionCode:
   ```json
   {
     "android": {
       "versionCode": 2
     }
   }
   ```

### Invalid Bundle ID

**Symptom**: "Bundle ID does not match" or submission fails

**Cause**: Bundle ID in app.json different from expected

**Solutions**:
1. Verify bundle ID matches:
   ```bash
   # Check app.json
   cat app.json | grep bundleIdentifier

   # Check eas.json
   cat eas.json | grep bundleIdentifier
   ```

2. Update app.json:
   ```json
   {
     "ios": {
       "bundleIdentifier": "com.company.app"
     },
     "android": {
       "package": "com.company.app"
     }
   }
   ```

3. Rebuild and resubmit:
   ```bash
   eas build --platform all
   eas submit --platform all
   ```

## Update Issues

### Update Not Downloaded

**Symptom**: Users don't receive published update

**Causes**:
- Runtime version mismatch
- Update published to wrong channel
- Build on different channel

**Solutions**:
1. Verify channel configuration:
   ```bash
   # Check build profile channel
   cat eas.json | grep -A 5 '"production"'

   # Check update channel
   eas update:list
   ```

2. Rebuild if native changes made:
   ```bash
   # Update runtime version
   # In app.json:
   {
     "runtimeVersion": "1.1.0"
   }

   # Rebuild
   eas build --platform all
   ```

3. Publish to correct channel:
   ```bash
   # Publish to channel matching build
   eas update --channel production --message "Update message"
   ```

### Update Fails to Download

**Symptom**: Users see download error, update fails to apply

**Causes**:
- Network connectivity issue
- Corrupted update bundle
- Bundle too large

**Solutions**:
1. Check update availability:
   ```bash
   eas update:list --branch main
   ```

2. Monitor update status:
   - Go to https://expo.dev
   - Select app → Updates
   - View deployment status

3. Rollback problematic update:
   ```bash
   # Get update group ID from list
   eas update:republish --group <group-id>
   ```

4. Reduce update size:
   - Remove unused assets
   - Compress images
   - Split large updates

### Runtime Version Mismatch

**Symptom**: "Update is not compatible with this build"

**Cause**: Update published for different runtime version

**Solutions**:
1. Verify runtime versions match:
   ```bash
   # In app.json, check runtimeVersion
   cat app.json | grep runtimeVersion

   # On deployed build, check same
   # Logs will show mismatch
   ```

2. Rebuild with new runtime:
   ```json
   {
     "runtimeVersion": "1.1.0"
   }
   ```
   ```bash
   eas build --platform all
   ```

3. Publish update with matching runtime:
   ```bash
   eas update --channel production --message "Update"
   ```

## Credential Issues

### Certificate Expired

**Symptom**: "Certificate is not valid yet" or similar error

**Causes**:
- Distribution certificate expired
- Provisioning profile expired
- Clock skew issue

**Solutions**:
```bash
# Check credential status
eas credentials --platform ios

# Regenerate if expired
eas credentials --platform ios
# Choose "Revoke and create new"

# Rebuild with new credentials
eas build --platform ios
```

### Keystore Password Incorrect

**Symptom**: "Keystore was tampered with, or password was incorrect"

**Causes**:
- Wrong password entered
- Corrupted keystore
- Wrong keystore file

**Solutions**:
```bash
# If you know password
eas credentials --platform android
# Enter correct password

# If password lost, create new keystore
eas credentials --platform android
# Choose "Create new keystore"

# This requires incrementing versionCode
# Then rebuild
eas build --platform android
```

### Missing API Key Credentials

**Symptom**: "ASC API key not found" or "API authentication failed"

**Causes**:
- `EXPO_ASC_API_KEY_PATH` not set
- Key file doesn't exist
- Key revoked or expired

**Solutions**:
```bash
# Set environment variable
export EXPO_ASC_API_KEY_PATH="/path/to/api-key.p8"
export EXPO_ASC_KEY_ID="ABC123"
export EXPO_ASC_ISSUER_ID="xyz-123"

# Verify file exists
ls -la $EXPO_ASC_API_KEY_PATH

# Generate new key if needed
# In App Store Connect → API Keys → Create
```

## CLI Issues

### EAS CLI Not Found

**Symptom**: "eas: command not found"

**Solutions**:
```bash
# Install globally
npm install -g eas-cli

# Or use npx
npx eas build --platform ios

# Check version
eas --version
```

### EXPO_TOKEN Not Recognized

**Symptom**: "Invalid authentication token"

**Causes**:
- Token not set
- Token expired
- Token revoked

**Solutions**:
```bash
# Check if set
echo $EXPO_TOKEN

# Login with new token
eas login

# Or set manually
export EXPO_TOKEN=your-token-here

# Generate new token if needed
# https://expo.dev/accounts/[account]/settings/access-tokens
```

### Non-Interactive Mode Prompts

**Symptom**: Interactive prompt appears in CI/CD

**Causes**:
- Missing required eas.json configuration
- Profile missing or incorrectly named
- Credentials not set

**Solutions**:
1. Add `--non-interactive` flag
2. Ensure complete eas.json:
   ```json
   {
     "build": {
       "production": {
         "channel": "production",
         "distribution": "store"
       }
     }
   }
   ```

3. Set all credentials:
   ```bash
   eas credentials
   eas build --non-interactive
   ```

## Common Error Messages

### "No build profiles found in eas.json"

**Solution**:
```bash
eas build:configure
```

Generates initial eas.json with profiles.

### "Cannot read property 'id' of undefined"

**Solution**:
- Check project ID is set
- Run `eas build:configure` to fix
- Verify app.json has valid configuration

### "EACCES: permission denied"

**Solution**:
```bash
# Fix permissions
chmod -R u+w node_modules
npm ci
```

### "ENOENT: no such file or directory"

**Solution**:
- File referenced in eas.json doesn't exist
- Check serviceAccountKeyPath for Android
- Verify all paths in eas.json are correct

## Getting Help

### Check Build Logs

```bash
# View full build logs
eas build:view <build-id>

# Logs usually show exact error
# Copy error message for searching
```

### Search Documentation

https://docs.expo.dev/build/troubleshooting/
https://docs.expo.dev/submit/troubleshooting/
https://docs.expo.dev/eas-update/troubleshooting/

### Ask Expo Community

- Expo Forums: https://forums.expo.dev
- GitHub Issues: https://github.com/expo/expo/issues
- Discord: https://chat.expo.dev

### Report Bug

If you believe it's an EAS bug:
1. Collect error details and logs
2. Create minimal reproduction
3. Report at https://github.com/expo/eas-cli/issues

Include:
- EAS CLI version: `eas --version`
- Node version: `node --version`
- Error messages and logs
- Steps to reproduce
- eas.json (redact secrets)
- app.json (redact secrets)

## Performance Troubleshooting

### Build Takes Too Long

**Solutions**:
1. Skip unnecessary steps:
   ```bash
   eas build --platform ios --non-interactive --no-wait
   ```

2. Use caching:
   ```json
   {
     "cache": {
       "key": "v1",
       "paths": ["node_modules/**"]
     }
   }
   ```

3. Use larger resource class:
   ```json
   {
     "resourceClass": "large"
   }
   ```

### CI/CD Minutes Exceed Budget

**Solutions**:
1. Reduce build frequency:
   - Only build on main branch
   - Only build on tags
   - Use `paths` to skip irrelevant commits

2. Use `--no-wait`:
   ```bash
   eas build --no-wait
   ```
   Prevents CI from blocking (EAS builds in parallel)

3. Consolidate builds:
   - Batch updates
   - Release weekly instead of daily

## Network Issues

### Connection Timeout

**Symptom**: "ECONNREFUSED" or timeout error

**Causes**:
- Network connectivity issue
- EAS service temporarily down
- Firewall blocking connections

**Solutions**:
```bash
# Check network
ping google.com

# Try again
eas build --platform ios

# Check EAS status
# https://status.expo.dev
```

### DNS Resolution Failed

**Symptom**: "getaddrinfo ENOTFOUND"

**Solutions**:
```bash
# Check DNS
nslookup expo.dev

# Try different DNS
# Change system DNS to 8.8.8.8 or 1.1.1.1
```
