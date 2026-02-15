---
name: expo-swift-ui
description: Build native iOS interfaces with SwiftUI components through Expo SDK 55's @expo/ui package. Use when creating native iOS controls, forms, lists, menus, pickers, toggles, sheets, or any SwiftUI-based UI in an Expo app.
license: MIT
---

# Expo SwiftUI Components (`@expo/ui`)

Build fully native iOS interfaces using SwiftUI components from React, via Expo SDK 55's `@expo/ui` package.

## References

Consult these resources as needed:

- ./references/components.md -- Complete API reference for all 30 SwiftUI components with props, types, and examples
- ./references/modifiers.md -- Full modifiers API: text, layout, visual effects, gestures, control styling, shapes, animations
- ./references/patterns.md -- Common patterns: settings forms, data lists, menus, sheets, complex layouts

## Installation

```bash
npx expo install @expo/ui
```

**Package:** `@expo/ui` (~55.0.0-preview.4)
**Platforms:** iOS (primary), tvOS (partial support)
**Requires:** Expo SDK 55, New Architecture enabled

## Core Concept: Host

Every SwiftUI component tree must be wrapped in a `<Host>` component. Host bridges React Native's layout system with SwiftUI's `UIHostingController`.

```tsx
import { Host, Text } from '@expo/ui/swift-ui';

export default function Example() {
  return (
    <Host matchContents>
      <Text>Hello from SwiftUI</Text>
    </Host>
  );
}
```

### Host Sizing

- `matchContents` -- Host shrinks to fit SwiftUI content (use for inline elements)
- `matchContents={{ horizontal: true, vertical: false }}` -- Match on one axis only
- `style={{ flex: 1 }}` -- Host expands to fill available space (use for full-screen layouts like Form, List)
- `useViewportSizeMeasurement` -- Use viewport size as proposed SwiftUI layout size

**Rule of thumb:** Use `matchContents` for buttons, labels, and inline components. Use `style={{ flex: 1 }}` for scrollable containers like Form and List.

## Core Concept: Modifiers

SwiftUI components are styled via the `modifiers` prop, not inline styles or StyleSheet. Import modifier functions from `@expo/ui/swift-ui/modifiers`.

```tsx
import { Button } from '@expo/ui/swift-ui';
import { buttonStyle, controlSize, tint } from '@expo/ui/swift-ui/modifiers';

<Button
  label="Delete"
  role="destructive"
  modifiers={[buttonStyle('bordered'), controlSize('large'), tint('#FF0000')]}
  onPress={handleDelete}
/>;
```

Modifiers compose as an array and apply in order, just like SwiftUI's modifier chain.

## All Components

### Bridge

| Component    | Purpose                                                             |
| ------------ | ------------------------------------------------------------------- |
| `Host`       | Root bridge between React Native and SwiftUI                        |
| `RNHostView` | Embed React Native views inside SwiftUI containers                  |
| `Namespace`  | Coordinate animations and matched geometry effects                  |
| `Group`      | Group views without adding layout structure; apply shared modifiers |

### Layout

| Component | Purpose                                            |
| --------- | -------------------------------------------------- |
| `VStack`  | Vertical stack with alignment and spacing          |
| `HStack`  | Horizontal stack with alignment and spacing        |
| `ZStack`  | Overlapping stack (z-axis) with 2D alignment       |
| `Spacer`  | Flexible space that expands to fill available room |
| `Divider` | Visual separator line                              |

### Text & Input

| Component   | Purpose                                             |
| ----------- | --------------------------------------------------- |
| `Text`      | Styled text with nested formatting support          |
| `TextField` | Text input (uncontrolled, single/multiline)         |
| `Image`     | SF Symbols display with color, size, variable value |
| `Label`     | Text + icon pair (SF Symbol or custom)              |

### Controls

| Component      | Purpose                                           |
| -------------- | ------------------------------------------------- |
| `Button`       | Tappable button with roles, icons, custom content |
| `Toggle`       | On/off switch with label and tint                 |
| `Slider`       | Continuous or stepped value selection             |
| `Picker`       | Option selection (segmented, menu, wheel)         |
| `DatePicker`   | Date/time selection (compact, graphical, wheel)   |
| `ColorPicker`  | Color selection with optional opacity             |
| `Gauge`        | Visual progress/value indicator                   |
| `ProgressView` | Determinate/indeterminate progress                |

### Containers & Structure

| Component         | Purpose                                             |
| ----------------- | --------------------------------------------------- |
| `Form`            | Settings-style grouped form container               |
| `List`            | Scrollable list with selection, delete, reorder     |
| `Section`         | Group content with headers/footers inside Form/List |
| `DisclosureGroup` | Expandable/collapsible content block                |

### Menus & Overlays

| Component     | Purpose                                     |
| ------------- | ------------------------------------------- |
| `Menu`        | Tap-triggered dropdown menu                 |
| `ContextMenu` | Long-press context menu with preview        |
| `Popover`     | Anchored floating overlay                   |
| `BottomSheet` | Modal sheet with detents and drag indicator |

## Import Pattern

All components come from `@expo/ui/swift-ui`. All modifiers come from `@expo/ui/swift-ui/modifiers`.

```tsx
// Components
import {
  Host,
  VStack,
  Text,
  Button,
  Form,
  Section,
  Toggle,
} from '@expo/ui/swift-ui';

// Modifiers
import {
  font,
  foregroundStyle,
  frame,
  padding,
  buttonStyle,
  tint,
} from '@expo/ui/swift-ui/modifiers';

// Shapes and animations
import { shapes, Animation } from '@expo/ui/swift-ui/modifiers';
```

## Key Rules

1. **Always wrap SwiftUI trees in `<Host>`** -- Nothing renders without it
2. **Use modifiers, not styles** -- SwiftUI components don't accept React Native style props
3. **Components are iOS-only** -- These are native SwiftUI; they won't render on Android or web
4. **TextField is uncontrolled** -- Use `defaultValue` and `onChangeText`, not `value`. Change `key` to reset
5. **Use `RNHostView` to embed React Native inside SwiftUI** -- For mixing RN views in sheets, popovers, etc.
6. **Modifier functions must be called** -- `buttonStyle('bordered')` not `buttonStyle`
7. **SF Symbols for icons** -- Use `systemImage` prop or `<Image systemName="..." />` with SF Symbol names
8. **Form/List need `flex: 1`** -- Use `<Host style={{ flex: 1 }}>` for scrollable containers
9. **Section goes inside Form or List** -- Section provides grouped styling only within these containers
10. **Picker options use `tag` modifier** -- Each option needs `modifiers={[tag(value)]}` to identify it
