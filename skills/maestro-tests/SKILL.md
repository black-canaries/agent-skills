---
name: maestro-tests
description: Write and run Maestro E2E tests for React Native Expo apps. Reads the user's app code to generate tailored YAML test flows with proper testID selectors, project structure, and CI setup. Use when writing E2E tests, creating Maestro flows, adding testIDs, or setting up mobile test automation.
---

<objective>
Generate Maestro E2E test flows tailored to the user's React Native Expo app. Analyze their screens, components, and navigation to produce reliable YAML flows with proper testID selectors, reusable subflows, and a scalable test directory structure.
</objective>

<context>
Maestro is a YAML-based mobile UI testing framework with built-in tolerance for timing and UI instability. It requires no compilation, supports React Native natively, and uses `testID` props as the primary element selector strategy.

Key characteristics:
- Flows are YAML files representing user journeys
- Automatic waiting for elements (no manual sleep/delays)
- `testID` maps to Maestro's `id` selector
- Supports iOS simulators, Android emulators, and cloud execution
- JavaScript engine available for advanced logic
</context>

<quick_start>
<workflow>
1. **Analyze the app**: Read route files, screens, and components to understand user journeys
2. **Add testIDs**: Ensure interactive elements have `testID` props (see [references/react-native-testid.md](references/react-native-testid.md))
3. **Create directory structure**: Set up `maestro/` at the project root
4. **Write flows**: Generate YAML flows for each user journey
5. **Run tests**: Execute with `maestro test`
</workflow>

<directory_structure>
```
maestro/
  config.yaml              # Test suite configuration
  flows/
    auth/
      login.yaml           # Login flow
      signup.yaml          # Signup flow
      logout.yaml          # Logout flow
    navigation/
      tab-navigation.yaml  # Tab bar navigation
      drawer-menu.yaml     # Drawer/sidebar navigation
    features/
      create-item.yaml     # Feature-specific flows
      search.yaml
    shared/
      login-helper.yaml    # Reusable subflows
      setup.yaml           # Common setup steps
```
</directory_structure>

<basic_flow_example>
```yaml
appId: com.example.myapp
name: User Login
tags:
  - smoke
  - auth
env:
  EMAIL: ${EMAIL || "test@example.com"}
  PASSWORD: ${PASSWORD || "testpass123"}
onFlowStart:
  - launchApp:
      clearState: true
---
# Navigate to login
- assertVisible: "Welcome"
- tapOn:
    id: "login-button"

# Enter credentials
- tapOn:
    id: "email-input"
- inputText: ${EMAIL}
- tapOn:
    id: "password-input"
- inputText: ${PASSWORD}
- hideKeyboard
- tapOn:
    id: "submit-button"

# Verify success
- assertVisible: "Home"
```
</basic_flow_example>
</quick_start>

<app_analysis_process>
Before writing any flows, analyze the user's app:

1. **Find route/screen files**: Glob for route files in `app/` or `src/app/` (Expo Router) or `screens/` directories
2. **Identify interactive elements**: Read screen components, find buttons, inputs, links, tabs
3. **Map navigation structure**: Understand tab bars, drawers, stacks, and deep links
4. **Check existing testIDs**: Grep for `testID` to see what's already instrumented
5. **Identify the appId**: Check `app.json` or `app.config.ts` for the bundle identifier

When generating flows:
- Use the actual `testID` values found in the codebase
- Match flow names to actual screen/feature names
- Reference real navigation paths the user's app uses
- Flag components missing `testID` and suggest additions
</app_analysis_process>

<flow_syntax>
<flow_configuration>
All config goes above the `---` separator:

```yaml
appId: com.example.app          # Required - bundle identifier
name: Descriptive Flow Name     # Optional - defaults to filename
tags:                           # Optional - for filtering
  - smoke
  - regression
env:                            # Optional - variables
  API_URL: https://api.example.com
onFlowStart:                    # Optional - runs before flow
  - clearState
  - launchApp:
      clearState: true
onFlowComplete:                 # Optional - runs after (success or fail)
  - stopApp
---
# Commands below
```
</flow_configuration>

<essential_commands>
**Tap**: `- tapOn:` with `id`, `text`, or `point` selector
**Input**: `- inputText: "value"` (tap field first to focus)
**Assert visible**: `- assertVisible:` with `id` or `text`
**Assert not visible**: `- assertNotVisible:` with `id` or `text`
**Scroll**: `- scrollUntilVisible:` with element + direction
**Wait**: `- extendedWaitUntil:` with visible/notVisible + timeout
**Navigate back**: `- back` (Android) or `- tapOn:` back button
**Deep link**: `- openLink: myapp://path`
**Hide keyboard**: `- hideKeyboard`
**Subflow**: `- runFlow: shared/login-helper.yaml`

Full command reference: [references/commands.md](references/commands.md)
</essential_commands>

<selectors>
**Preferred (most reliable)**:
```yaml
- tapOn:
    id: "testID-value"        # Maps to React Native testID
```

**By text (fallback)**:
```yaml
- tapOn: "Button Label"       # Exact match
- tapOn:
    text: "Submit.*"          # Regex pattern
```

**By position**:
```yaml
- tapOn:
    point: "50%, 90%"         # Screen percentage
```

**Relative**:
```yaml
- tapOn:
    id: "edit-button"
    below: "Section Header"   # Also: above, leftOf, rightOf
```

**By index (when multiple match)**:
```yaml
- tapOn:
    text: "Delete"
    index: 2                  # Third match (0-based)
```

Full selector reference: [references/selectors.md](references/selectors.md)
</selectors>
</flow_syntax>

<reusable_subflows>
Extract repeated sequences into shared flows:

**shared/login-helper.yaml:**
```yaml
appId: com.example.app
---
- tapOn:
    id: "email-input"
- inputText: ${EMAIL}
- tapOn:
    id: "password-input"
- inputText: ${PASSWORD}
- hideKeyboard
- tapOn:
    id: "submit-button"
- assertVisible: "Home"
```

**Usage in other flows:**
```yaml
- runFlow:
    file: shared/login-helper.yaml
    env:
      EMAIL: test@example.com
      PASSWORD: password123
```

**Conditional subflow:**
```yaml
- runFlow:
    when:
      visible: "Login"
    file: shared/login-helper.yaml
    env:
      EMAIL: test@example.com
      PASSWORD: password123
```
</reusable_subflows>

<config_yaml>
**maestro/config.yaml:**
```yaml
flows:
  - "flows/**"
executionOrder:
  continueOnFailure: false
  flowsOrder:
    - flows/auth/login.yaml
    - flows/navigation/tab-navigation.yaml
    - flows/features/**
```

Run the suite: `maestro test maestro/`
</config_yaml>

<advanced_features>
**Repeat**:
```yaml
- repeat:
    times: 3
    commands:
      - tapOn: "Add Item"
      - scroll
```

**Retry flaky steps**:
```yaml
- retry:
    commands:
      - tapOn: "Submit"
      - assertVisible: "Success"
```

**JavaScript**:
```yaml
- evalScript: ${output.itemCount = 0}
- repeat:
    while:
      true: ${output.itemCount < 5}
    commands:
      - tapOn: "Add"
      - evalScript: ${output.itemCount = output.itemCount + 1}
```

**Random test data**:
```yaml
- inputText: "{{EMAIL}}"           # Random email
- inputText: "{{NAME}}"            # Random name
- inputText: "{{RANDOM_NUMBER}}"   # Random number
```

**Screenshots**:
```yaml
- takeScreenshot: "after-login"
```

**HTTP from JavaScript** (for API setup/teardown):
```yaml
- runScript: scripts/seed-data.js
```

For more: [references/commands.md](references/commands.md)
</advanced_features>

<testing_commands>
**Run single flow:**
```bash
maestro test maestro/flows/auth/login.yaml
```

**Run all flows:**
```bash
maestro test maestro/
```

**With parameters:**
```bash
maestro test -e EMAIL=user@test.com -e PASSWORD=secret maestro/flows/auth/login.yaml
```

**Continuous mode (re-runs on file change):**
```bash
maestro test --continuous maestro/flows/auth/login.yaml
```

**Interactive studio (visual element picker):**
```bash
maestro studio
```

**Generate report:**
```bash
maestro test --format junit --output report.xml maestro/
maestro test --format html maestro/
```

**View hierarchy (debug selectors):**
```bash
maestro hierarchy
```
</testing_commands>

<ci_setup>
For CI integration patterns (GitHub Actions, EAS), see [references/ci-setup.md](references/ci-setup.md).
</ci_setup>

<testid_patterns>
For React Native testID conventions and patterns, see [references/react-native-testid.md](references/react-native-testid.md).
</testid_patterns>

<anti_patterns>
- **Never use fixed sleeps/waits** - Maestro handles timing automatically. Use `assertVisible` or `extendedWaitUntil` instead.
- **Don't write monolithic flows** - One flow per user journey. Small, focused flows enable parallel execution.
- **Don't rely solely on text selectors** - Text changes break tests. Always prefer `testID` via `id` selector.
- **Don't hardcode credentials** - Use `env` block or CLI `-e` parameters.
- **Don't skip `clearState`** - Start flows with `clearState: true` for consistent state.
- **Don't overuse conditionals** - Complex branching makes tests hard to debug. Write separate flows instead.
- **Don't nest tappable elements without accessibility config** - On iOS, set `accessible={false}` on parent, `accessible={true}` on target child.
</anti_patterns>

<success_criteria>
- Flows use `testID`-based `id` selectors as primary selection strategy
- All interactive components in tested screens have `testID` props
- testID naming follows `kebab-case` convention matching the component's purpose
- Flows are organized by feature in `maestro/flows/` with reusable subflows in `shared/`
- `config.yaml` defines execution order and flow inclusion
- Each flow has `appId`, descriptive `name`, relevant `tags`, and `clearState` on launch
- Flows run successfully: `maestro test maestro/`
- No hardcoded credentials - all secrets via env parameters
</success_criteria>
