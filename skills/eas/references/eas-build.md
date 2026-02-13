# EAS Build Deep Dive

## Platform-Specific Build Configurations

### iOS Build Configuration

```json
{
  "build": {
    "production": {
      "ios": {
        "buildConfiguration": "Release",
        "scheme": "MyApp",
        "bundleIdentifier": "com.example.myapp",
        "enterpriseProvisioning": "universal",
        "simulator": false
      }
    }
  }
}
```

**iOS-specific properties**:
- `buildConfiguration`: "Release" or "Debug" (use Release for App Store)
- `scheme`: Xcode project scheme name (auto-detected if not specified)
- `bundleIdentifier`: Override app bundle ID
- `simulator`: true to build for iOS Simulator instead of device
- `enterpriseProvisioning`: "universal" or "adhoc" for enterprise accounts
- `fastlane`: Version to use (default handles most cases)
- `cocoapods`: Version to use
- `bundler`: Bundler version for Ruby dependency management

**iOS build process**:
1. Clones your repository on EAS infrastructure
2. Installs dependencies (npm/yarn/pnpm, CocoaPods)
3. Runs prebuild (if native code needs generation)
4. Builds with Xcode
5. Signs with provisioning profiles and certificates (auto-managed by EAS)
6. Produces `.ipa` file for device or `.zip` for simulator

### Android Build Configuration

```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "app-bundle",
        "gradleCommand": "assembleRelease",
        "ndk": "23.1.7779620"
      }
    }
  }
}
```

**Android-specific properties**:
- `buildType`: "app-bundle" (AAB for Play Store) or "apk" (for direct installation)
- `gradleCommand`: Custom Gradle task (default: "assembleRelease" or "bundleRelease")
- `ndk`: Android NDK version
- `image`: Build environment image (managed by EAS, rarely needs override)

**Android build process**:
1. Clones repository on EAS infrastructure
2. Installs dependencies and Android SDK
3. Runs prebuild if needed
4. Executes Gradle build command
5. Signs APK/AAB with upload key (auto-managed by EAS)
6. Produces AAB file for Play Store or APK for direct installation

## Development Builds

Development builds allow testing native code changes without rebuilding the entire app.

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "apk"
      }
    }
  }
}
```

**Installing development builds**:
```bash
# Build development
eas build --platform ios --profile development

# Install on device
# Option 1: Via QR code from build dashboard
# Option 2: Via Expo Orbit tool
# Option 3: Download IPA and use Xcode/TestFlight

# With development build installed, use dev client
npx expo start --dev-client
```

**Benefits of development builds**:
- Test native module changes instantly
- Run TypeScript in strict mode
- Use custom native code
- Faster iteration than rebuilding app binary

## Distribution Methods

### Internal Distribution

Share preview builds with internal testers via URL:

```json
{
  "build": {
    "preview": {
      "distribution": "internal",
      "channel": "preview"
    }
  }
}
```

After build completes:
1. View build dashboard → "Install" button
2. Open URL on device to install
3. Share URL with testers
4. Build remains available for 30 days

### App Store Distribution

Build artifacts stored for submission to app stores:

```json
{
  "build": {
    "production": {
      "distribution": "store",
      "channel": "production"
    }
  }
}
```

After build completes:
1. Use `eas submit` to upload to stores
2. Or download artifact manually from dashboard
3. Artifact available indefinitely on dashboard

## Build Artifacts and Storage

**Accessing build artifacts**:
```bash
# List builds
eas build:list

# Download build
eas build:view <build-id>
```

**Artifact retention**:
- iOS: `.ipa` files available indefinitely on dashboard
- Android: `.aab` and `.apk` files available indefinitely
- Source code: Not stored after build completes

**Using artifacts locally**:

iOS device:
```bash
# Download IPA from dashboard
# Install via Xcode or Apple Configurator 2
# Or use Expo CLI on device with QR code
```

Android:
```bash
# Download APK from dashboard
adb install app.apk
```

## Build Profiles and Variants

Create multiple profiles for different release stages:

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development",
      "env": {
        "APP_ENV": "development",
        "DEBUG": "true"
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
      "distribution": "store",
      "channel": "production",
      "env": {
        "APP_ENV": "production",
        "API_URL": "https://api.example.com"
      },
      "autoIncrement": true
    }
  }
}
```

**Using profiles**:
```bash
# Build specific profile
eas build --platform ios --profile staging

# Default uses profile matching platform
# Custom profile names available in eas.json
```

## Automated Version Management

Use `autoIncrement` to automatically bump version numbers:

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

**How it works**:
1. Reads current version from app.json
2. Increments patch version (1.0.0 → 1.0.1)
3. Updates app.json
4. Builds with new version
5. Does NOT commit changes (you must commit manually or use git hooks)

**Manual version management**:
```json
{
  "app": {
    "version": "1.0.0"
  }
}
```

Update in app.json before building for manual control.

## Build Caching and Performance

Speed up builds with caching:

```json
{
  "build": {
    "production": {
      "cache": {
        "key": "my-app-v1",
        "paths": ["node_modules/**", ".gradle/**"]
      }
    }
  }
}
```

**Cache behavior**:
- Same cache key = reuses previous build artifacts
- Different key = fresh build
- Use cache for stable builds, skip for troubleshooting
- Cache is per-profile and per-platform

## Resource Classes

Choose build machine size based on project complexity:

```json
{
  "build": {
    "production": {
      "resourceClass": "large"
    }
  }
}
```

**Options**:
- `"default"`: Suitable for most projects (2 vCPUs, 4 GB RAM)
- `"medium"`: Larger projects (4 vCPUs, 8 GB RAM)
- `"large"`: Very large projects or monorepos (8 vCPUs, 16 GB RAM)

Use default unless build times exceed 30 minutes or memory errors occur.

## Custom Build Workflows

Override default build process:

```bash
# Configure custom workflow
eas build:configure --workflow generic
```

Creates `.eas/workflows/build.yml` for declarative build orchestration:

```yaml
name: Custom Build
on:
  buildRequested: {}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Starting custom build"
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
```

**When to use custom workflows**:
- Complex multi-step builds
- Integration with external services
- Conditional build logic
- Build triggers beyond simple CLI commands

## Build Troubleshooting

**Common build failures**:

1. **Dependency installation fails**
   - Check package.json syntax
   - Verify all packages have compatible versions
   - Try building with `resourceClass: "medium"`

2. **Native build errors**
   - Run `eas build:view <build-id>` to see full logs
   - Check native code changes are compatible with target platform
   - Ensure all native dependencies are properly linked

3. **Signing/credential errors**
   - Run `eas credentials` to review credentials
   - For iOS: Check provisioning profile expiration
   - For Android: Verify service account has Play Console access

4. **Memory/timeout errors**
   - Increase `resourceClass` to "medium" or "large"
   - Reduce build artifact size
   - Split monorepo into smaller projects

## Monitoring Builds

Track build progress and status:

```bash
# List recent builds
eas build:list

# View specific build details
eas build:view <build-id>

# Follow build in real-time
eas build:list --latest
```

**Build status indicators**:
- `QUEUED`: Waiting for build machine
- `IN_PROGRESS`: Currently building
- `FINISHED`: Successfully completed
- `ERRORED`: Build failed (check logs)

Dashboard at https://expo.dev provides visual build history and logs.
