# SwiftUI Modifiers API Reference

All modifiers are imported from `@expo/ui/swift-ui/modifiers` and applied via the `modifiers` prop as an array.

```tsx
import {
  font,
  foregroundStyle,
  padding,
  frame,
} from '@expo/ui/swift-ui/modifiers';

<Text
  modifiers={[
    font({ size: 18, weight: 'bold' }),
    foregroundStyle({ color: '#333' }),
    padding({ all: 8 }),
  ]}
>
  Styled Text
</Text>;
```

---

## Text & Font

| Modifier                        | Parameters                                    | Description                                         |
| ------------------------------- | --------------------------------------------- | --------------------------------------------------- |
| `bold()`                        | none                                          | Makes text bold (iOS 16+ for non-Text views)        |
| `italic()`                      | none                                          | Applies italic styling (iOS 16+ for non-Text views) |
| `font(params)`                  | `{ size?, weight?, design?, family? }`        | Set font properties                                 |
| `foregroundStyle(style)`        | color string, hierarchical style, or gradient | Set text/foreground color                           |
| `foregroundColor(color)`        | hex string                                    | **Deprecated** -- use `foregroundStyle`             |
| `textCase(value)`               | `'lowercase' \| 'uppercase'`                  | Transform text case                                 |
| `kerning(value)`                | `number`                                      | Character spacing                                   |
| `lineSpacing(value)`            | `number`                                      | Line spacing                                        |
| `lineLimit(limit)`              | `number`                                      | Max number of lines                                 |
| `multilineTextAlignment(align)` | `'center' \| 'leading' \| 'trailing'`         | Multi-line text alignment                           |
| `strikethrough(params)`         | `{ color?, isActive?, pattern? }`             | Strikethrough decoration                            |
| `underline(params)`             | `{ color?, isActive?, pattern? }`             | Underline decoration                                |
| `allowsTightening(value)`       | `boolean`                                     | Allow compressed character spacing                  |
| `truncationMode(mode)`          | `'head' \| 'middle' \| 'tail'`                | Truncation position                                 |
| `textSelection(value)`          | `boolean`                                     | Enable/disable text selection                       |

### Font Weight Values

`ultraLight`, `light`, `regular`, `medium`, `semibold`, `bold`, `heavy`, `black`

### Font Design Values

`default`, `rounded`, `serif`, `monospaced`

### Foreground Style Variants

```tsx
// Simple color
foregroundStyle({ color: '#FF0000' });
foregroundStyle({ color: 'red' });

// Hierarchical
foregroundStyle({ type: 'hierarchical', style: 'primary' });
// styles: 'primary', 'secondary', 'tertiary', 'quaternary', 'quinary'

// Linear gradient
foregroundStyle({
  type: 'linearGradient',
  colors: ['#FF0000', '#0000FF'],
  startPoint: { x: 0, y: 0 },
  endPoint: { x: 1, y: 1 },
});

// Radial gradient
foregroundStyle({
  type: 'radialGradient',
  colors: ['#FF0000', '#0000FF'],
  center: { x: 0.5, y: 0.5 },
  startRadius: 0,
  endRadius: 100,
});

// Angular gradient
foregroundStyle({
  type: 'angularGradient',
  colors: ['#FF0000', '#00FF00', '#0000FF'],
  center: { x: 0.5, y: 0.5 },
});
```

---

## Layout & Sizing

| Modifier                         | Parameters                                                                                                 | Description                        |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `frame(params)`                  | `{ width?, height?, minWidth?, maxWidth?, minHeight?, maxHeight?, idealWidth?, idealHeight?, alignment? }` | Set size constraints               |
| `padding(params)`                | `{ all?, top?, bottom?, leading?, trailing?, horizontal?, vertical? }`                                     | Add padding                        |
| `offset(params)`                 | `{ x?, y? }`                                                                                               | Translate view position            |
| `aspectRatio(params)`            | `{ ratio?, contentMode? }`                                                                                 | Aspect ratio constraint            |
| `fixedSize(params)`              | `{ horizontal?, vertical? }`                                                                               | Prevent view from being compressed |
| `containerRelativeFrame(params)` | `{ alignment?, axes?, count?, spacing?, span? }`                                                           | iOS 17+ container-relative sizing  |
| `layoutPriority(priority)`       | `number`                                                                                                   | Layout priority                    |
| `zIndex(index)`                  | `number`                                                                                                   | Z-order                            |
| `ignoreSafeArea(params)`         | `{ edges?, regions? }`                                                                                     | Extend into safe areas             |

### Frame Alignment Values

`'center'`, `'leading'`, `'trailing'`, `'top'`, `'bottom'`, `'topLeading'`, `'topTrailing'`, `'bottomLeading'`, `'bottomTrailing'`

```tsx
// Fixed size
frame({ width: 200, height: 100 });

// Flexible with constraints
frame({ minWidth: 100, maxWidth: 300, idealHeight: 200 });

// Padding
padding({ horizontal: 16, vertical: 8 });
padding({ all: 12 });
padding({ top: 20, bottom: 10, leading: 16, trailing: 16 });
```

---

## Visual Effects

| Modifier                    | Parameters                   | Description                               |
| --------------------------- | ---------------------------- | ----------------------------------------- |
| `background(color, shape?)` | hex string, optional shape   | Background color with optional shape clip |
| `backgroundOverlay(params)` | `{ alignment?, color }`      | Background layer behind view              |
| `overlay(params)`           | `{ alignment?, color }`      | Overlay layer on top of view              |
| `cornerRadius(radius)`      | `number`                     | Round corners                             |
| `border(params)`            | `{ color, width }`           | Border stroke                             |
| `shadow(params)`            | `{ color?, radius, x?, y? }` | Drop shadow                               |
| `opacity(value)`            | `number` (0-1)               | Transparency                              |
| `blur(radius)`              | `number`                     | Gaussian blur                             |
| `brightness(amount)`        | `number` (-1 to 1)           | Brightness adjustment                     |
| `contrast(amount)`          | `number`                     | Contrast multiplier                       |
| `saturation(amount)`        | `number`                     | Saturation multiplier                     |
| `grayscale(amount)`         | `number` (0-1)               | Desaturate                                |
| `hueRotation(angle)`        | `number` (degrees)           | Rotate hue                                |
| `colorInvert(inverted?)`    | `boolean` (default: true)    | Invert colors                             |
| `tint(color)`               | hex string                   | Tint color for controls                   |
| `hidden(hidden?)`           | `boolean` (default: true)    | Hide view                                 |

### Glass Effects

```tsx
import { glassEffect, glassEffectId } from '@expo/ui/swift-ui/modifiers';

glassEffect({
  cornerRadius: 16,
  glass: { interactive: true, tint: '#007AFF', variant: 'regular' },
  shape: shapes.roundedRectangle({ cornerRadius: 16 }),
});

// Associate with namespace for coordinated effects
glassEffectId('myView', namespaceId);
```

---

## Shape & Clipping

| Modifier                          | Parameters                                                       | Description         |
| --------------------------------- | ---------------------------------------------------------------- | ------------------- |
| `clipShape(shape, cornerRadius?)` | `'circle' \| 'rectangle' \| 'roundedRectangle'`, optional radius | Clip to shape       |
| `clipped(clipped?)`               | `boolean` (default: true)                                        | Clip to bounds      |
| `mask(shape, cornerRadius?)`      | shape, optional radius                                           | Mask view           |
| `containerShape(shape)`           | shape config                                                     | Set container shape |

### Shape Builders

```tsx
import { shapes } from '@expo/ui/swift-ui/modifiers';

shapes.roundedRectangle({ cornerRadius: 12 });
shapes.capsule();
shapes.rectangle();
shapes.ellipse();
shapes.circle();
```

---

## Transforms & Animation

| Modifier                          | Parameters                       | Description                |
| --------------------------------- | -------------------------------- | -------------------------- |
| `scaleEffect(scale)`              | `number`                         | Scale factor               |
| `rotationEffect(angle)`           | `number` (degrees)               | Rotation                   |
| `animation(anim, value)`          | Animation object, animated value | Animate state changes      |
| `matchedGeometryEffect(id, nsId)` | string id, namespace id          | Shared element transitions |

### Animation Constants

```tsx
import { Animation } from '@expo/ui/swift-ui/modifiers';

Animation.easeInOut({ duration: 0.3 });
Animation.easeIn({ duration: 0.3 });
Animation.easeOut({ duration: 0.3 });
Animation.linear({ duration: 0.3 });
Animation.spring({ duration: 0.8 });
Animation.interpolatingSpring({ duration: 0.8 });
```

---

## Gestures & Interaction

| Modifier                                 | Parameters                      | Description               |
| ---------------------------------------- | ------------------------------- | ------------------------- |
| `onTapGesture(handler)`                  | `() => void`                    | Tap callback              |
| `onLongPressGesture(handler, duration?)` | callback, optional min duration | Long press callback       |
| `onAppear(handler)`                      | `() => void`                    | View appeared callback    |
| `onDisappear(handler)`                   | `() => void`                    | View disappeared callback |
| `disabled(disabled?)`                    | `boolean` (default: true)       | Disable interaction       |
| `deleteDisabled(disabled?)`              | `boolean`                       | Prevent list deletion     |
| `moveDisabled(disabled?)`                | `boolean`                       | Prevent list reordering   |
| `interactiveDismissDisabled(disabled?)`  | `boolean`                       | Prevent sheet dismissal   |

---

## Control Styling

| Modifier                   | Values                                                                                                       | Description              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------ |
| `buttonStyle(style)`       | `'bordered'`, `'borderless'`, `'borderedProminent'`, `'plain'`, `'glass'`, `'glassProminent'`, `'automatic'` | Button appearance        |
| `textFieldStyle(style)`    | `'automatic'`, `'plain'`, `'roundedBorder'`                                                                  | Text field appearance    |
| `toggleStyle(style)`       | `'switch'`, `'button'`, `'automatic'`                                                                        | Toggle appearance        |
| `controlSize(size)`        | `'mini'`, `'small'`, `'regular'`, `'large'`, `'extraLarge'`                                                  | Control size             |
| `datePickerStyle(style)`   | `'automatic'`, `'compact'`, `'graphical'`, `'wheel'`                                                         | Date picker appearance   |
| `pickerStyle(style)`       | `'automatic'`, `'inline'`, `'menu'`, `'navigationLink'`, `'palette'`, `'segmented'`, `'wheel'`               | Picker appearance        |
| `gaugeStyle(style)`        | `'automatic'`, `'circular'`, `'circularCapacity'`, `'linear'`, `'linearCapacity'`                            | Gauge appearance         |
| `progressViewStyle(style)` | `'automatic'`, `'linear'`, `'circular'`                                                                      | Progress view appearance |
| `labelStyle(style)`        | `'automatic'`, `'iconOnly'`, `'titleAndIcon'`, `'titleOnly'`                                                 | Label appearance         |
| `labelsHidden()`           | none                                                                                                         | Hide control labels      |

---

## List & Table Styling

| Modifier                               | Parameters                                                                      | Description                  |
| -------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------- |
| `listStyle(style)`                     | `'automatic' \| 'plain' \| 'inset' \| 'insetGrouped' \| 'grouped' \| 'sidebar'` | List appearance              |
| `listRowBackground(color)`             | hex string                                                                      | Row background color         |
| `listRowInsets(params)`                | `{ top?, bottom?, leading?, trailing? }`                                        | Row insets                   |
| `listRowSeparator(visibility, edges?)` | visibility string, optional edges                                               | Row separator visibility     |
| `listSectionSpacing(spacing)`          | `number \| 'default' \| 'compact'`                                              | Section spacing (iOS 17+)    |
| `listSectionMargins(params)`           | `{ edges?, length? }`                                                           | Section margins (iOS 26+)    |
| `headerProminence(prominence)`         | `'standard' \| 'increased'`                                                     | Section header weight        |
| `scrollContentBackground(visible)`     | `'automatic' \| 'visible' \| 'hidden'`                                          | Scroll background visibility |

---

## Presentation & Modal

| Modifier                                  | Parameters                             | Description                        |
| ----------------------------------------- | -------------------------------------- | ---------------------------------- |
| `presentationDetents(detents)`            | array of detent values                 | Sheet snap heights (iOS 16+)       |
| `presentationDragIndicator(vis)`          | `'automatic' \| 'visible' \| 'hidden'` | Drag indicator (iOS 16+)           |
| `presentationBackgroundInteraction(type)` | interaction type                       | Background interaction (iOS 16.4+) |

### Presentation Detent Values

- `'medium'` -- Half screen
- `'large'` -- Full screen
- `{ fraction: 0.3 }` -- Custom fraction (0-1)
- `{ height: 200 }` -- Fixed height in points

---

## Scrolling & Keyboard

| Modifier                        | Parameters                                                   | Description                         |
| ------------------------------- | ------------------------------------------------------------ | ----------------------------------- |
| `scrollDisabled(disabled?)`     | `boolean` (default: true)                                    | Disable scrolling (iOS 16+)         |
| `scrollDismissesKeyboard(mode)` | `'automatic' \| 'never' \| 'interactively' \| 'immediately'` | Keyboard dismissal (iOS 16+)        |
| `refreshable(handler)`          | `() => Promise<void>`                                        | Pull-to-refresh                     |
| `submitLabel(label)`            | submit label string                                          | Keyboard return key label (iOS 15+) |

---

## Accessibility

| Modifier                    | Parameters | Description         |
| --------------------------- | ---------- | ------------------- |
| `accessibilityLabel(label)` | `string`   | Screen reader label |
| `accessibilityHint(hint)`   | `string`   | Screen reader hint  |
| `accessibilityValue(value)` | `string`   | Screen reader value |

---

## Other

| Modifier                              | Parameters                                 | Description                        |
| ------------------------------------- | ------------------------------------------ | ---------------------------------- |
| `tag(tag)`                            | `string \| number`                         | Identify view for selection/picker |
| `badge(value?)`                       | `string`                                   | Display badge                      |
| `badgeProminence(type)`               | `'standard' \| 'increased' \| 'decreased'` | Badge prominence                   |
| `environment(key, value)`             | key string, value                          | Set SwiftUI environment value      |
| `menuActionDismissBehavior(behavior)` | `'disabled' \| 'automatic' \| 'enabled'`   | Menu dismiss behavior (iOS 16.4+)  |

### Common Environment Keys

```tsx
// Enable edit mode for lists
environment('editMode', 'active');
```

---

## Grid Layout Modifiers

| Modifier                         | Parameters                            | Description                   |
| -------------------------------- | ------------------------------------- | ----------------------------- |
| `gridCellColumns(count)`         | `number`                              | Span columns in grid          |
| `gridCellUnsizedAxes(axes)`      | `'horizontal' \| 'vertical'`          | Prevent grid sizing on axis   |
| `gridCellAnchor(anchor)`         | anchor config                         | Grid cell alignment (iOS 16+) |
| `gridColumnAlignment(alignment)` | `'center' \| 'leading' \| 'trailing'` | Column alignment (iOS 16+)    |
