# CI/CD Setup Guide

## Overview

Automate EAS builds and submissions using CI/CD platforms. EAS integrates with GitHub Actions, GitLab CI, and other services.

**Key concept**: CI/CD doesn't execute the build—it orchestrates EAS, which builds on cloud infrastructure.

## GitHub Actions Integration

### Prerequisites

1. Repository on GitHub
2. Expo account with personal access token
3. EAS project configured locally (run `eas build:configure`)
4. eas.json in repository root

### Creating Personal Access Token

Generate token for CI authentication:

1. Visit https://expo.dev/accounts/[your-account]/settings/access-tokens
2. Click "Create new token"
3. Name: "CI Token"
4. Scope: "Select All"
5. Copy token
6. Add to GitHub repository secrets

### Setting Up GitHub Actions

Add token to repository secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `EXPO_TOKEN`
4. Value: Personal access token
5. Click "Add secret"

### Basic Workflow

Create `.github/workflows/eas-build.yml`:

```yaml
name: EAS Build

on:
  push:
    branches:
      - main

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
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - run: npm ci

      - name: Build iOS
        run: eas build --platform ios --non-interactive --no-wait

      - name: Build Android
        run: eas build --platform android --non-interactive --no-wait
```

**Key flags**:
- `--non-interactive`: No prompts, use defaults
- `--no-wait`: Don't block workflow while building (builds happen on EAS infrastructure)

### Build and Submit Workflow

```yaml
name: EAS Build and Submit

on:
  push:
    branches:
      - main
    paths:
      - 'app/**'
      - 'package.json'

jobs:
  build-and-submit:
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
        run: |
          eas build --platform ios --profile production \
            --auto-submit --non-interactive --no-wait
          eas build --platform android --profile production \
            --auto-submit --non-interactive --no-wait
        env:
          EXPO_ASC_API_KEY_PATH: ${{ runner.temp }}/asc-api-key.p8
          EXPO_ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          EXPO_ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
```

### Release Workflow (On Tags)

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
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

      - name: Build for iOS
        run: eas build --platform ios --profile production --non-interactive --no-wait

      - name: Build for Android
        run: eas build --platform android --profile production --non-interactive --no-wait
```

Trigger with:
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Conditional Workflows

```yaml
name: Build

on:
  push:
    branches:
      - main
      - develop

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

      - name: Determine Profile
        id: profile
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "name=production" >> $GITHUB_OUTPUT
          else
            echo "name=staging" >> $GITHUB_OUTPUT
          fi

      - name: Build
        run: eas build --platform all --profile ${{ steps.profile.outputs.name }} --non-interactive --no-wait
```

### Caching Dependencies

```yaml
name: Build with Cache

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: npm

      - uses: expo/expo-github-action@v8
        with:
          token: ${{ secrets.EXPO_TOKEN }}

      - run: npm ci

      - name: Build
        run: eas build --platform all --non-interactive --no-wait
```

The `cache: npm` directive caches node_modules between workflows.

### Secrets Management for CI/CD

Store sensitive values in GitHub secrets:

```yaml
env:
  EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
  API_URL: ${{ secrets.API_URL }}
  SENTRY_DSN: ${{ secrets.SENTRY_DSN }}
```

In eas.json:
```json
{
  "build": {
    "production": {
      "env": {
        "API_URL": "$API_URL",
        "SENTRY_DSN": "$SENTRY_DSN"
      }
    }
  }
}
```

EAS substitutes variables at build time.

### iOS-Specific Secrets

For iOS App Store submissions:

1. Create App Store Connect API Key
2. Download `.p8` file
3. Add to GitHub secrets as `ASC_API_KEY` (base64 encoded file contents)
4. In workflow, decode and use:

```yaml
- name: Setup iOS Credentials
  run: |
    mkdir -p ${{ runner.temp }}
    echo "${{ secrets.ASC_API_KEY }}" | base64 -d > ${{ runner.temp }}/asc-api-key.p8

- name: Build and Submit
  run: eas build --platform ios --profile production --auto-submit --non-interactive
  env:
    EXPO_ASC_API_KEY_PATH: ${{ runner.temp }}/asc-api-key.p8
    EXPO_ASC_KEY_ID: ${{ secrets.ASC_KEY_ID }}
    EXPO_ASC_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
```

### Android-Specific Secrets

For Google Play submissions:

1. Generate service account JSON
2. Add to GitHub secrets as `GOOGLE_PLAY_KEY` (base64 encoded)
3. Store path in eas.json

EAS handles service account authentication automatically if configured in eas.json.

## Generic CI/CD Patterns

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - build

build_app:
  stage: build
  image: node:18
  before_script:
    - npm install -g eas-cli
    - npm ci
  script:
    - eas build --platform ios --profile production --non-interactive --no-wait
    - eas build --platform android --profile production --non-interactive --no-wait
  only:
    - main
  environment:
    EXPO_TOKEN: $EXPO_TOKEN
```

### CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  build:
    docker:
      - image: node:18
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: npm ci
      - run:
          name: Install EAS CLI
          command: npm install -g eas-cli
      - run:
          name: Build
          command: |
            eas build --platform ios --profile production --non-interactive --no-wait
            eas build --platform android --profile production --non-interactive --no-wait

workflows:
  build_and_test:
    jobs:
      - build:
          filters:
            branches:
              only: main
          context: expo
```

### Bitbucket Pipelines

Create `bitbucket-pipelines.yml`:

```yaml
image: node:18

pipelines:
  branches:
    main:
      - step:
          name: Build
          script:
            - npm install -g eas-cli
            - npm ci
            - eas build --platform ios --profile production --non-interactive --no-wait
            - eas build --platform android --profile production --non-interactive --no-wait
```

## Environment Setup

### Required Environment Variables

**Global**:
```
EXPO_TOKEN=<your-personal-access-token>
```

**iOS Submissions**:
```
EXPO_ASC_API_KEY_PATH=<path-to-api-key.p8>
EXPO_ASC_KEY_ID=<api-key-id>
EXPO_ASC_ISSUER_ID=<api-key-issuer-id>
```

**Android Submissions**:
Service account JSON configured in eas.json

### Node.js and Package Manager Versions

Specify in workflow:

```yaml
- uses: actions/setup-node@v3
  with:
    node-version: 18
```

Match local development environment version to prevent surprises.

## Workflow Best Practices

### Use Specific Versions

```yaml
- uses: expo/expo-github-action@v8
- uses: actions/setup-node@v3
  with:
    node-version: 18
- run: npm install -g eas-cli@5.2.0
```

Pinning versions ensures reproducibility.

### Separate Build from Submit

```yaml
- name: Build
  run: eas build --platform all --non-interactive --no-wait

- name: Submit
  run: eas submit --platform all --profile production --non-interactive
```

Decoupling allows independent control over each step.

### Run Tests Before Build

```yaml
- run: npm ci
- run: npm test
- run: npm run lint
- name: Build
  run: eas build --platform all --non-interactive --no-wait
```

Catch issues before spending build time.

### Skip Builds Selectively

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'app/**'
      - 'package.json'
      - 'eas.json'
```

Only build when relevant files change.

### Notify on Failures

```yaml
- name: Notify Slack on Failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"EAS build failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}'
```

Get alerts for build failures.

## Common Configuration Issues

### EXPO_TOKEN Not Found

**Error**: "EXPO_TOKEN environment variable not set"

**Solution**:
1. Verify token added to repository secrets
2. Check secret name exactly matches `EXPO_TOKEN`
3. Ensure `token: ${{ secrets.EXPO_TOKEN }}` in workflow

### Node Modules Cache Issues

**Error**: "Module not found after successful npm ci"

**Solution**:
1. Clear cache: Settings → Actions → Clear cache
2. Or use `npm cache clean --force`
3. Re-run workflow

### Credentials Not Found During Build

**Error**: "Credentials not available during EAS build"

**Solution**:
1. Ensure credentials configured in EAS (run `eas credentials` locally first)
2. For iOS: Add ASC API key environment variables
3. For Android: Verify service account JSON is accessible

### Non-Interactive Mode Prompts

**Error**: "Interactive prompt in non-interactive build"

**Solution**:
1. Add `--non-interactive` flag
2. Ensure all required eas.json configuration is complete
3. Set default profile with matching name in eas.json

## Monitoring and Debugging

### View Logs

GitHub Actions workflow logs show:
- EAS CLI output
- Build command output
- Build queue status
- Submission status

Click "Build" step to see full logs.

### Check Build Status

```bash
# List builds
eas build:list

# View specific build
eas build:view <build-id>
```

Or check dashboard at https://expo.dev

### Debug Environment Variables

```yaml
- name: Debug
  run: |
    echo "EXPO_TOKEN is set: ${{ secrets.EXPO_TOKEN != '' }}"
    echo "Branch: ${{ github.ref }}"
    node --version
    npm --version
    eas --version
```

Add debug steps to understand workflow state.

## Cost and Limits

**GitHub Actions**:
- Free tier: 2,000 minutes/month
- EAS builds: Takes 10-30 minutes each
- Plan accordingly (e.g., only build on tags, not every push)

**EAS Build limits**:
- Free tier: Up to 30 builds/month
- Paid plans: More builds included
- No additional charge for CI/CD usage

**Best practice**: Limit triggers to main branch and/or tags to avoid wasting free minutes.
