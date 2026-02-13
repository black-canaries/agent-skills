# eas.json Configuration Schema

## File Structure

The `eas.json` file lives in your project root and configures EAS services.

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "profileName": { /* build configuration */ }
  },
  "submit": {
    "profileName": { /* submit configuration */ }
  },
  "updates": {
    "autoConfigure": true
  }
}
```

## CLI Configuration

```json
{
  "cli": {
    "version": ">= 5.2.0",
    "requireCommitMessage": false,
    "requireCommitMessageForAutoPush": false
  }
}
```

- `version`: Minimum EAS CLI version required
- `requireCommitMessage`: Require commit message before building
- `requireCommitMessageForAutoPush`: Require message for git pushes

## Build Configuration

### Top-Level Build Properties

```json
{
  "build": {
    "production": {
      "node": "18.x",
      "npm": "9.x",
      "yarn": "3.x",
      "pnpm": "8.x",
      "bun": "1.x",
      "prebuildCommand": "./prebuild.sh",
      "buildArtifactPaths": ["app-*.apk", "app-*.aab"],
      "resourceClass": "default",
      "cache": {
        "key": "v1",
        "paths": ["node_modules/**"]
      },
      "env": {
        "API_URL": "https://api.example.com"
      },
      "secrets": {
        "SECRET_KEY": "@SECRET_KEY"
      },
      "channel": "production",
      "distribution": "store",
      "developmentClient": false,
      "credentialsSource": "remote",
      "withoutCredentials": false,
      "extends": "production"
    }
  }
}
```

### Common Build Properties

**Node.js/Package Managers**:
- `node`: Node.js version (default: latest LTS)
- `npm`: npm version
- `yarn`: Yarn version
- `pnpm`: pnpm version
- `bun`: Bun version

**Build Process**:
- `prebuildCommand`: Custom script to run before build
- `buildArtifactPaths`: Glob patterns for artifact location
- `cache`: Cache configuration (key and paths)
- `env`: Environment variables for build process
- `secrets`: Reference CI secrets

**EAS Configuration**:
- `channel`: EAS Update channel
- `distribution`: "store" or "internal"
- `developmentClient`: true for development builds
- `credentialsSource`: "local" or "remote"
- `withoutCredentials`: Skip credential requirements
- `extends`: Inherit from another profile
- `resourceClass`: "default", "medium", or "large"

### iOS-Specific Build Properties

```json
{
  "build": {
    "production": {
      "ios": {
        "bundleIdentifier": "com.example.app",
        "buildConfiguration": "Release",
        "scheme": "MyApp",
        "simulator": false,
        "enterpriseProvisioning": "universal",
        "fastlane": "2.210.0",
        "cocoapods": "1.13.0",
        "bundler": "2.4.12",
        "buildArtifactPath": "ios/build/MyApp.ipa"
      }
    }
  }
}
```

**iOS configuration**:
- `bundleIdentifier`: Override bundle ID
- `buildConfiguration`: "Release" or "Debug"
- `scheme`: Xcode scheme name
- `simulator`: true for Simulator, false for device
- `enterpriseProvisioning`: "universal" or "adhoc"
- `fastlane`: Version to use
- `cocoapods`: CocoaPods version
- `bundler`: Bundler version
- `buildArtifactPath`: Custom artifact path
- `autoIncrement`: true to auto-bump build number

### Android-Specific Build Properties

```json
{
  "build": {
    "production": {
      "android": {
        "ndk": "23.1.7779620",
        "buildType": "app-bundle",
        "gradleCommand": "assembleRelease",
        "image": "ubuntu-22.04",
        "applicationArchivePath": "app/build/outputs/bundle/release/app-release.aab"
      }
    }
  }
}
```

**Android configuration**:
- `ndk`: Android NDK version
- `buildType`: "app-bundle" or "apk"
- `gradleCommand`: Custom Gradle command
- `image`: Build environment image
- `applicationArchivePath`: Custom artifact path
- `autoIncrement`: true to auto-bump version code

### Auto-Increment Configuration

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

- `autoIncrement`: true bumps version automatically
- Works with iOS build number and Android version code
- Does NOT commit changes (manual or use git hooks)

## Submit Configuration

### Top-Level Submit Properties

```json
{
  "submit": {
    "production": {
      "ios": { /* iOS submit config */ },
      "android": { /* Android submit config */ }
    }
  }
}
```

### iOS Submit Configuration

```json
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "user@example.com",
        "appleTeamId": "ABC123XYZ",
        "ascAppId": "1234567890",
        "appName": "My App",
        "bundleIdentifier": "com.example.myapp",
        "sku": "com.example.myapp",
        "language": "en-US",
        "iosDisplayVersion": "1.0.0",
        "iosBuildVersion": "1",
        "ascApiKeyPath": "./asc-api-key.p8",
        "ascApiKeyId": "ABC123",
        "ascApiIssuerId": "xyz-123",
        "appCategory": "GAMES",
        "metadataPath": "./fastlane/metadata/ios"
      }
    }
  }
}
```

**iOS submit fields**:
- `appleId`: Apple ID email (for credentials)
- `appleTeamId`: Apple Developer Team ID
- `ascAppId`: App Store Connect App ID (numeric)
- `appName`: Display name in App Store
- `bundleIdentifier`: Must match app.json
- `sku`: Unique identifier (auto-generated if omitted)
- `language`: Submission language (default: en-US)
- `iosDisplayVersion`: Version number (auto-detected)
- `iosBuildVersion`: Build number (auto-detected)
- `ascApiKeyPath`: Path to API key file (for CI/CD)
- `ascApiKeyId`: API Key ID
- `ascApiIssuerId`: API Key Issuer ID
- `appCategory`: App Store category code
- `metadataPath`: Path to Fastlane metadata files

### Android Submit Configuration

```json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./google-play-key.json",
        "track": "production",
        "releaseStatus": "completed",
        "changesNotSentForReview": false,
        "rollout": 1.0,
        "inAppPriority": 5
      }
    }
  }
}
```

**Android submit fields**:
- `serviceAccountKeyPath`: Path to Google Play service account JSON
- `track`: "production", "beta", "alpha", or "internal"
- `releaseStatus`: "completed", "draft", "inProgress", or "halted"
- `changesNotSentForReview`: true to skip automatic review
- `rollout`: User fraction (0-1) for staged rollout
- `inAppPriority`: Priority level for in-app updates (1-5)
- `changesNotSentForReviewInNewLocales`: Skip review for new locales

## Complete Example

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development",
      "env": {
        "APP_ENV": "development",
        "API_URL": "http://localhost:3000"
      },
      "node": "18.x",
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "apk"
      }
    },
    "staging": {
      "distribution": "internal",
      "channel": "staging",
      "env": {
        "APP_ENV": "staging",
        "API_URL": "https://staging-api.example.com"
      },
      "autoIncrement": false
    },
    "production": {
      "distribution": "store",
      "channel": "production",
      "env": {
        "APP_ENV": "production",
        "API_URL": "https://api.example.com"
      },
      "autoIncrement": true,
      "resourceClass": "medium",
      "cache": {
        "key": "v1",
        "paths": ["node_modules/**"]
      },
      "ios": {
        "buildConfiguration": "Release"
      },
      "android": {
        "buildType": "app-bundle"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "developer@example.com",
        "appleTeamId": "ABC123XYZ",
        "ascAppId": "1234567890",
        "appName": "My App",
        "bundleIdentifier": "com.example.myapp"
      },
      "android": {
        "serviceAccountKeyPath": "./google-play-key.json",
        "track": "production",
        "releaseStatus": "completed"
      }
    }
  }
}
```

## Environment Variables in eas.json

Reference CI environment variables with `$VAR_NAME`:

```json
{
  "build": {
    "production": {
      "env": {
        "SENTRY_DSN": "$SENTRY_DSN",
        "API_KEY": "$API_KEY"
      }
    }
  }
}
```

In CI platform (e.g., GitHub Actions):
```yaml
env:
  SENTRY_DSN: ${{ secrets.SENTRY_DSN }}
  API_KEY: ${{ secrets.API_KEY }}
```

EAS substitutes `$SENTRY_DSN` with actual value at build time.

## Extending Profiles

Reuse configuration with `extends`:

```json
{
  "build": {
    "base": {
      "node": "18.x",
      "resourceClass": "default"
    },
    "development": {
      "extends": "base",
      "developmentClient": true,
      "distribution": "internal"
    },
    "production": {
      "extends": "base",
      "distribution": "store",
      "resourceClass": "medium"
    }
  }
}
```

Child profile inherits all properties from parent, can override.

## Secrets Management

Store sensitive values using `@` syntax:

```json
{
  "build": {
    "production": {
      "secrets": {
        "API_KEY": "@API_KEY",
        "DATABASE_URL": "@DATABASE_URL"
      }
    }
  }
}
```

Configure secrets in CI platform:
- GitHub Actions: Secrets settings
- GitLab CI: Protected variables
- Etc.

EAS resolves `@VAR_NAME` to environment variable value at build time.

## Common Configuration Patterns

### Development + Production

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development"
    },
    "production": {
      "distribution": "store",
      "channel": "production",
      "autoIncrement": true
    }
  }
}
```

### Multi-Environment with CI

```json
{
  "build": {
    "staging": {
      "distribution": "internal",
      "channel": "staging",
      "env": {
        "ENVIRONMENT": "staging",
        "API_URL": "$STAGING_API_URL"
      }
    },
    "production": {
      "distribution": "store",
      "channel": "production",
      "env": {
        "ENVIRONMENT": "production",
        "API_URL": "$PROD_API_URL"
      }
    }
  }
}
```

### Platform-Specific Customization

```json
{
  "build": {
    "production": {
      "ios": {
        "bundleIdentifier": "com.example.app",
        "buildConfiguration": "Release"
      },
      "android": {
        "buildType": "app-bundle",
        "ndk": "23.1.7779620"
      }
    }
  }
}
```

## Validation and Testing

Validate eas.json syntax:

```bash
# EAS CLI validates on every command
eas build --platform ios

# If eas.json is invalid, you'll get clear error messages
```

Common errors:
- Invalid JSON syntax (missing commas, quotes)
- Unknown configuration keys
- Invalid property values
- Missing required fields

Fix by reviewing error message and updating eas.json accordingly.
