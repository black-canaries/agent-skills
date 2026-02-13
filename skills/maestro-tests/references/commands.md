# Maestro Command Reference

## App Lifecycle

### launchApp
```yaml
- launchApp                          # Simple launch
- launchApp:
    appId: "com.example.app"         # Override appId
    clearState: true                 # Clear app data before launch
    clearKeychain: true              # Clear iOS keychain
    stopApp: false                   # Don't stop if already running
    permissions:                     # Set permissions
      all: deny                      # deny all, then allow specific
      camera: allow
      location: allow
    arguments:                       # Launch arguments
      isTestMode: true
      apiUrl: "https://staging.api.com"
```

### stopApp / killApp / clearState / clearKeychain
```yaml
- stopApp                            # Stop app (iOS/Web)
- killApp                            # Kill app (Android)
- clearState                         # Clear current app data
- clearState: com.other.app          # Clear specific app
- clearKeychain                      # Clear iOS keychain
```

## Interactions

### tapOn
```yaml
- tapOn: "Button Text"               # By text
- tapOn:
    id: "testID"                     # By testID (preferred)
- tapOn:
    text: "Submit.*"                 # Regex text match
    enabled: true                    # Only enabled elements
    index: 0                         # First match (0-based)
- tapOn:
    point: "50%, 50%"               # Screen percentage
- tapOn:
    point: "100, 200"               # Pixel coordinates
```

### doubleTapOn / longPressOn
```yaml
- doubleTapOn: "Element"
- doubleTapOn:
    id: "element-id"

- longPressOn: "Element"
- longPressOn:
    id: "element-id"
```

### swipe
```yaml
- swipe:
    direction: UP                    # UP, DOWN, LEFT, RIGHT
    duration: 500                    # Duration in ms
```

## Text Input

### inputText
Must tap field first to focus:
```yaml
- tapOn:
    id: "email-input"
- inputText: "user@example.com"

# Built-in random generators
- inputText: "{{EMAIL}}"            # Random email
- inputText: "{{NAME}}"             # Random name
- inputText: "{{RANDOM_NUMBER}}"    # Random number
```

### eraseText / copyTextFrom / pasteText / setClipboard
```yaml
- eraseText: 10                      # Erase 10 characters
- copyTextFrom:
    id: "text-element"               # Copy text to maestro.copiedText
- pasteText                          # Paste into focused field
- setClipboard: "Text to copy"      # Set clipboard directly
```

## Scrolling

### scroll
```yaml
- scroll                             # Default scroll down
- scroll:
    direction: UP                    # UP or DOWN
```

### scrollUntilVisible
```yaml
- scrollUntilVisible:
    element:
      id: "target-element"          # Or text: "Target"
    direction: DOWN                  # DOWN, UP, LEFT, RIGHT
    timeout: 20000                   # Max wait (ms), default 20000
    speed: 40                        # 0-100, default 40
    visibilityPercentage: 100        # 0-100, default 100
    centerElement: false             # Center element after finding
```

## Assertions

### assertVisible / assertNotVisible
```yaml
- assertVisible: "Welcome"          # By text
- assertVisible:
    id: "home-screen"               # By testID
    enabled: true                    # Check enabled state
    index: 0                         # Which match

- assertNotVisible: "Loading..."
- assertNotVisible:
    id: "error-message"
```

### assertTrue
```yaml
- assertTrue: ${output.counter > 0}
- assertTrue: ${output.loggedIn == true}
```

### assertWithAI (requires login)
```yaml
- assertWithAI: "The shopping cart shows 3 items"
```

## Navigation & Device

### back / openLink / hideKeyboard / pressKey
```yaml
- back                               # Android back button
- openLink: https://example.com      # Open URL
- openLink: myapp://screen/123       # Deep link
- hideKeyboard                       # Dismiss keyboard
- pressKey: home                     # Device keys: home, back, enter
```

### setLocation / setOrientation / setAirplaneMode
```yaml
- setLocation:
    latitude: 37.7749
    longitude: -122.4194

- setOrientation: landscape          # portrait or landscape

- setAirplaneMode: true
- toggleAirplaneMode
```

### setPermissions
```yaml
- setPermissions:
    camera: allow
    location: deny
    notifications: allow
    photos: allow
```

## Flow Control

### runFlow
```yaml
- runFlow: shared/login.yaml         # External flow

- runFlow:                           # With parameters
    file: shared/login.yaml
    env:
      EMAIL: user@test.com

- runFlow:                           # Conditional
    when:
      visible: "Login Screen"
    file: shared/login.yaml

- runFlow:                           # Inline commands
    commands:
      - tapOn: "OK"
      - assertVisible: "Done"

- runFlow:                           # Platform-specific
    when:
      platform: iOS
    commands:
      - tapOn: "iOS Settings"
```

### repeat
```yaml
- repeat:
    times: 5                         # Fixed count
    commands:
      - tapOn: "Add"

- repeat:
    while:                           # Condition-based
      notVisible: "Complete"
    commands:
      - tapOn: "Next"
      - scroll

- repeat:                            # Count + condition (stops at either)
    times: 10
    while:
      notVisible: "Target"
    commands:
      - scroll
```

### retry
```yaml
- retry:
    commands:
      - tapOn: "Flaky Button"
      - assertVisible: "Result"
```

## Timing

### extendedWaitUntil
```yaml
- extendedWaitUntil:
    visible: "Content Loaded"
    timeout: 10000                   # ms

- extendedWaitUntil:
    notVisible: "Loading Spinner"
    timeout: 15000
```

### waitForAnimationToEnd
```yaml
- waitForAnimationToEnd
- waitForAnimationToEnd:
    timeout: 5000                    # Continue after timeout
```

## JavaScript

### evalScript / runScript
```yaml
- evalScript: ${output.myVar = "hello"}
- evalScript: ${output.count = output.count + 1}
- evalScript: ${console.log("Debug: " + output.myVar)}

- runScript: scripts/setup.js
- runScript:
    file: scripts/api-call.js
    env:
      API_KEY: ${API_KEY}
```

## Recording & Debug

```yaml
- startRecording
- stopRecording
- takeScreenshot: "descriptive-name"
- addMedia: path/to/image.png        # Add to device gallery
```
