# SwiftUI Component API Reference

Complete reference for all 30 components in `@expo/ui/swift-ui`.

---

## Bridge Components

### Host

Root container bridging React Native and SwiftUI. Uses `UIHostingController` under the hood.

```tsx
import { Host } from '@expo/ui/swift-ui';
```

| Prop                           | Type                                                    | Default        | Description                           |
| ------------------------------ | ------------------------------------------------------- | -------------- | ------------------------------------- |
| `children`                     | `ReactNode`                                             | --             | SwiftUI components to render          |
| `matchContents`                | `boolean \| { horizontal: boolean, vertical: boolean }` | `false`        | Sizes host to match SwiftUI content   |
| `style`                        | `StyleProp<ViewStyle>`                                  | --             | React Native view styles              |
| `colorScheme`                  | `'light' \| 'dark'`                                     | --             | Override color scheme                 |
| `layoutDirection`              | `'leftToRight' \| 'rightToLeft'`                        | locale default | Layout direction                      |
| `ignoreSafeAreaKeyboardInsets` | `boolean`                                               | `false`        | Disable keyboard avoidance            |
| `useViewportSizeMeasurement`   | `boolean`                                               | `false`        | Use viewport as proposed SwiftUI size |
| `onLayoutContent`              | `(event: { nativeEvent: { height, width } }) => void`   | --             | Layout callback                       |

```tsx
// Inline element: matchContents
<Host matchContents>
  <Button label="Tap me" onPress={() => {}} />
</Host>

// Full-screen: flex 1
<Host style={{ flex: 1 }}>
  <Form>
    <Section title="Settings">
      <Toggle label="Dark Mode" isOn={darkMode} onIsOnChange={setDarkMode} />
    </Section>
  </Form>
</Host>
```

### RNHostView

Embeds React Native views inside SwiftUI containers. Syncs layout from SwiftUI back to Yoga.

```tsx
import { RNHostView } from '@expo/ui/swift-ui';
```

| Prop            | Type           | Default  | Description                           |
| --------------- | -------------- | -------- | ------------------------------------- |
| `children`      | `ReactElement` | required | The RN view to host                   |
| `matchContents` | `boolean`      | `false`  | Size SwiftUI view to match RN content |

```tsx
// Inside a BottomSheet or Popover
<BottomSheet isPresented={show} onIsPresentedChange={setShow}>
  <RNHostView matchContents>
    <View style={{ padding: 20 }}>
      <RNText>React Native content inside SwiftUI sheet</RNText>
    </View>
  </RNHostView>
</BottomSheet>
```

### Namespace

Provides SwiftUI namespace for coordinating animations and matched geometry effects.

```tsx
import { Namespace } from '@expo/ui/swift-ui';
```

| Prop       | Type        | Description                              |
| ---------- | ----------- | ---------------------------------------- |
| `id`       | `string`    | Namespace ID (use `useId()` to generate) |
| `children` | `ReactNode` | Children that share this namespace       |

```tsx
import { useId } from 'react';
import { Namespace, Image } from '@expo/ui/swift-ui';
import {
  matchedGeometryEffect,
  glassEffectId,
} from '@expo/ui/swift-ui/modifiers';

function Example() {
  const nsId = useId();
  return (
    <Namespace id={nsId}>
      <Image
        systemName="star.fill"
        modifiers={[matchedGeometryEffect('star', nsId)]}
      />
    </Namespace>
  );
}
```

### Group

Groups views without adding layout structure. Apply shared modifiers to multiple children.

```tsx
import { Group } from '@expo/ui/swift-ui';
```

| Prop       | Type        | Description    |
| ---------- | ----------- | -------------- |
| `children` | `ReactNode` | Views to group |

```tsx
import { foregroundStyle } from '@expo/ui/swift-ui/modifiers';

<Group modifiers={[foregroundStyle({ color: 'blue' })]}>
  <Text>All children</Text>
  <Text>share blue color</Text>
</Group>;
```

---

## Layout Components

### VStack

Arranges children vertically.

```tsx
import { VStack } from '@expo/ui/swift-ui';
```

| Prop        | Type                                  | Description          |
| ----------- | ------------------------------------- | -------------------- |
| `children`  | `ReactNode`                           | Child elements       |
| `spacing`   | `number`                              | Gap between children |
| `alignment` | `'leading' \| 'center' \| 'trailing'` | Horizontal alignment |

```tsx
<VStack spacing={12} alignment="leading">
  <Text>First</Text>
  <Text>Second</Text>
  <Text>Third</Text>
</VStack>
```

### HStack

Arranges children horizontally.

```tsx
import { HStack } from '@expo/ui/swift-ui';
```

| Prop        | Type                                                                         | Description          |
| ----------- | ---------------------------------------------------------------------------- | -------------------- |
| `children`  | `ReactNode`                                                                  | Child elements       |
| `spacing`   | `number`                                                                     | Gap between children |
| `alignment` | `'top' \| 'center' \| 'bottom' \| 'firstTextBaseline' \| 'lastTextBaseline'` | Vertical alignment   |

```tsx
<HStack spacing={8} alignment="center">
  <Image systemName="star.fill" color="orange" />
  <Text>Favorited</Text>
</HStack>
```

### ZStack

Overlays children on the z-axis.

```tsx
import { ZStack } from '@expo/ui/swift-ui';
```

| Prop        | Type                                                                                                                               | Description                                |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `children`  | `ReactNode`                                                                                                                        | Child elements (last child renders on top) |
| `alignment` | `'center' \| 'leading' \| 'trailing' \| 'top' \| 'bottom' \| 'topLeading' \| 'topTrailing' \| 'bottomLeading' \| 'bottomTrailing'` | 2D alignment                               |

```tsx
<ZStack alignment="bottomTrailing">
  <Rectangle modifiers={[frame({ width: 100, height: 100 })]} />
  <Circle
    modifiers={[
      frame({ width: 24, height: 24 }),
      foregroundStyle({ color: 'red' }),
    ]}
  />
</ZStack>
```

### Spacer

Flexible space that expands to fill available room in a stack.

```tsx
import { Spacer } from '@expo/ui/swift-ui';
```

| Prop        | Type     | Description             |
| ----------- | -------- | ----------------------- |
| `minLength` | `number` | Minimum space in points |

```tsx
<HStack>
  <Text>Left</Text>
  <Spacer />
  <Text>Right</Text>
</HStack>
```

### Divider

Visual separator line.

```tsx
import { Divider } from '@expo/ui/swift-ui';
```

No component-specific props. Inherits `CommonViewModifierProps`.

```tsx
<VStack>
  <Text>Above</Text>
  <Divider />
  <Text>Below</Text>
</VStack>
```

---

## Text & Input Components

### Text

Displays styled text. Supports nested Text for inline formatting.

```tsx
import { Text } from '@expo/ui/swift-ui';
```

| Prop       | Type        | Description                            |
| ---------- | ----------- | -------------------------------------- |
| `children` | `ReactNode` | Text content or nested Text components |

Key modifiers: `font()`, `foregroundStyle()`, `bold()`, `italic()`, `lineLimit()`, `kerning()`, `strikethrough()`, `underline()`, `textCase()`, `multilineTextAlignment()`, `truncationMode()`

```tsx
import { font, foregroundStyle, bold } from '@expo/ui/swift-ui/modifiers';

// Basic styled text
<Text modifiers={[font({ size: 24, weight: 'bold' }), foregroundStyle({ color: '#333' })]}>
  Hello World
</Text>

// Nested inline formatting
<Text modifiers={[font({ size: 16 })]}>
  This is <Text modifiers={[bold(), foregroundStyle({ color: 'red' })]}>important</Text> text.
</Text>
```

**Font options:**

- `weight`: ultraLight, light, regular, medium, semibold, bold, heavy, black
- `design`: default, rounded, serif, monospaced
- `family`: custom font family name
- `size`: numeric point size

### TextField

Text input. **Uncontrolled component** -- uses `defaultValue`, not `value`.

```tsx
import { TextField } from '@expo/ui/swift-ui';
```

| Prop                | Type                         | Default     | Description                |
| ------------------- | ---------------------------- | ----------- | -------------------------- |
| `defaultValue`      | `string`                     | --          | Initial value              |
| `placeholder`       | `string`                     | --          | Placeholder text           |
| `onChangeText`      | `(value: string) => void`    | --          | Text change callback       |
| `onSubmit`          | `(value: string) => void`    | --          | Return key callback        |
| `onChangeFocus`     | `(focused: boolean) => void` | --          | Focus change callback      |
| `onChangeSelection` | `({ start, end }) => void`   | --          | Selection change (iOS 18+) |
| `autoFocus`         | `boolean`                    | `false`     | Auto-focus on mount        |
| `autocorrection`    | `boolean`                    | `true`      | Enable autocorrection      |
| `allowNewlines`     | `boolean`                    | `true`      | Allow newlines on return   |
| `multiline`         | `boolean`                    | --          | Enable multiline input     |
| `numberOfLines`     | `number`                     | unlimited   | Lines before scrolling     |
| `keyboardType`      | `TextFieldKeyboardType`      | `'default'` | Keyboard type              |
| `ref`               | `Ref<TextFieldRef>`          | --          | Imperative handle          |

**Keyboard types:** `default`, `numeric`, `email-address`, `phone-pad`, `decimal-pad`, `ascii-capable`, `url`, `numbers-and-punctuation`, `name-phone-pad`, `twitter`, `web-search`, `ascii-capable-number-pad`

**Ref methods:** `focus()`, `blur()`, `setText(text)`, `setSelection(start, end)` (iOS 18+)

```tsx
const [text, setText] = useState('');

<TextField
  defaultValue="Hello"
  placeholder="Enter name..."
  autocorrection={false}
  onChangeText={setText}
/>

// To update text externally, change the key:
<TextField key={resetKey} defaultValue={newValue} onChangeText={setText} />
```

### Image

Displays SF Symbols.

```tsx
import { Image } from '@expo/ui/swift-ui';
```

| Prop            | Type         | Description                                                     |
| --------------- | ------------ | --------------------------------------------------------------- |
| `systemName`    | `SFSymbol`   | SF Symbol identifier (e.g., `'star.fill'`, `'heart'`, `'gear'`) |
| `color`         | `ColorValue` | Symbol color (hex or named)                                     |
| `size`          | `number`     | Symbol size in points                                           |
| `variableValue` | `number`     | 0.0-1.0 for symbols supporting variable rendering (iOS 16+)     |
| `onPress`       | `() => void` | Tap callback                                                    |

```tsx
<Image systemName="heart.fill" size={24} color="red" />
<Image systemName="wifi" size={32} variableValue={0.7} color="blue" />
```

### Label

Text paired with an icon.

```tsx
import { Label } from '@expo/ui/swift-ui';
```

| Prop          | Type        | Description                                    |
| ------------- | ----------- | ---------------------------------------------- |
| `title`       | `string`    | Label text                                     |
| `systemImage` | `string`    | SF Symbol name                                 |
| `icon`        | `ReactNode` | Custom icon component (instead of systemImage) |

Key modifier: `labelStyle('automatic' | 'iconOnly' | 'titleAndIcon' | 'titleOnly')`

```tsx
<Label title="Favorites" systemImage="star.fill" />
<Label title="Settings" systemImage="gear" modifiers={[labelStyle('iconOnly')]} />
```

---

## Control Components

### Button

Tappable button with text, icons, roles, and custom content.

```tsx
import { Button } from '@expo/ui/swift-ui';
```

| Prop          | Type                                     | Description               |
| ------------- | ---------------------------------------- | ------------------------- |
| `label`       | `string`                                 | Button text               |
| `onPress`     | `() => void`                             | Press callback            |
| `role`        | `'default' \| 'cancel' \| 'destructive'` | Semantic role             |
| `systemImage` | `SFSymbol`                               | SF Symbol alongside label |
| `children`    | `ReactElement`                           | Custom label content      |

Key modifiers: `buttonStyle()`, `controlSize()`, `tint()`, `disabled()`

**Button styles:** `bordered`, `borderless`, `borderedProminent`, `plain`, `glass`, `glassProminent`, `automatic`
**Control sizes:** `mini`, `small`, `regular`, `large`, `extraLarge`

```tsx
// Basic
<Button label="Save" onPress={handleSave} />

// Styled with icon
<Button
  label="Download"
  systemImage="arrow.down.circle"
  modifiers={[buttonStyle('borderedProminent'), controlSize('large')]}
  onPress={handleDownload}
/>

// Destructive
<Button label="Delete" role="destructive" onPress={handleDelete} />

// Custom content
<Button onPress={handlePress}>
  <HStack spacing={4}>
    <Image systemName="folder" />
    <Text>Open Folder</Text>
  </HStack>
</Button>
```

### Toggle

On/off switch with label.

```tsx
import { Toggle } from '@expo/ui/swift-ui';
```

| Prop           | Type                      | Description                                               |
| -------------- | ------------------------- | --------------------------------------------------------- |
| `isOn`         | `boolean`                 | Current state                                             |
| `onIsOnChange` | `(isOn: boolean) => void` | State change callback                                     |
| `label`        | `string`                  | Description text                                          |
| `systemImage`  | `SFSymbol`                | Icon alongside label                                      |
| `children`     | `ReactNode`               | Custom label (first Text = title, second Text = subtitle) |

Key modifiers: `toggleStyle('switch' | 'button' | 'automatic')`, `tint()`

```tsx
const [enabled, setEnabled] = useState(false);

<Toggle label="Notifications" isOn={enabled} onIsOnChange={setEnabled} />

// With icon and tint
<Toggle
  label="Airplane Mode"
  systemImage="airplane"
  isOn={airplane}
  onIsOnChange={setAirplane}
  modifiers={[tint('#FF9500')]}
/>

// Custom labels (title + subtitle)
<Toggle isOn={vibrate} onIsOnChange={setVibrate}>
  <Text>Vibrate on Ring</Text>
  <Text>Enable vibration when phone rings</Text>
</Toggle>
```

### Slider

Continuous or stepped value selection.

```tsx
import { Slider } from '@expo/ui/swift-ui';
```

| Prop                | Type                           | Description                       |
| ------------------- | ------------------------------ | --------------------------------- |
| `value`             | `number`                       | Current value                     |
| `min`               | `number`                       | Minimum value                     |
| `max`               | `number`                       | Maximum value                     |
| `step`              | `number`                       | Step increment (0 for continuous) |
| `label`             | `ReactNode`                    | Description label                 |
| `minimumValueLabel` | `ReactNode`                    | Label at minimum position         |
| `maximumValueLabel` | `ReactNode`                    | Label at maximum position         |
| `onValueChange`     | `(value: number) => void`      | Drag callback                     |
| `onEditingChanged`  | `(isEditing: boolean) => void` | Start/end editing callback        |

```tsx
const [volume, setVolume] = useState(50);

<Slider
  value={volume}
  min={0}
  max={100}
  step={1}
  label={<Text>Volume</Text>}
  minimumValueLabel={<Text>0</Text>}
  maximumValueLabel={<Text>100</Text>}
  onValueChange={setVolume}
/>;
```

### Picker

Option selection with multiple display styles.

```tsx
import { Picker } from '@expo/ui/swift-ui';
```

| Prop                | Type                     | Description                       |
| ------------------- | ------------------------ | --------------------------------- |
| `children`          | `ReactNode`              | Text options with `tag` modifiers |
| `label`             | `string \| ReactNode`    | Picker label                      |
| `selection`         | `T`                      | Currently selected tag value      |
| `onSelectionChange` | `(selection: T) => void` | Selection callback                |
| `systemImage`       | `SFSymbol`               | Icon alongside label              |

Key modifier: `pickerStyle('segmented' | 'menu' | 'wheel' | 'inline' | 'palette' | 'navigationLink' | 'automatic')`

**Important:** Each option needs a `tag` modifier to identify its value.

```tsx
import { tag, pickerStyle } from '@expo/ui/swift-ui/modifiers';

const options = ['Apple', 'Banana', 'Orange'];
const [selected, setSelected] = useState(options[0]);

// Segmented
<Picker
  modifiers={[pickerStyle('segmented')]}
  label="Fruit"
  selection={selected}
  onSelectionChange={setSelected}
>
  {options.map(opt => (
    <Text key={opt} modifiers={[tag(opt)]}>{opt}</Text>
  ))}
</Picker>

// Menu style
<Picker modifiers={[pickerStyle('menu')]} selection={selected} onSelectionChange={setSelected}>
  {options.map(opt => (
    <Text key={opt} modifiers={[tag(opt)]}>{opt}</Text>
  ))}
</Picker>
```

### DatePicker

Date and/or time selection.

```tsx
import { DatePicker } from '@expo/ui/swift-ui';
```

| Prop                  | Type                            | Description                              |
| --------------------- | ------------------------------- | ---------------------------------------- |
| `selection`           | `Date`                          | Currently selected date                  |
| `onDateChange`        | `(date: Date) => void`          | Date change callback                     |
| `title`               | `string`                        | Label text                               |
| `displayedComponents` | `('date' \| 'hourAndMinute')[]` | Components to show (default: `['date']`) |
| `range`               | `{ start?: Date, end?: Date }`  | Selectable date range                    |
| `children`            | `ReactNode`                     | Custom label                             |

Key modifier: `datePickerStyle('automatic' | 'compact' | 'graphical' | 'wheel')`

```tsx
const [date, setDate] = useState(new Date());

// Compact date picker
<DatePicker title="Birthday" selection={date} onDateChange={setDate} />

// Date and time
<DatePicker
  title="Appointment"
  selection={date}
  displayedComponents={['date', 'hourAndMinute']}
  onDateChange={setDate}
/>

// Graphical calendar style
<DatePicker
  modifiers={[datePickerStyle('graphical')]}
  selection={date}
  displayedComponents={['date']}
  onDateChange={setDate}
/>

// With date range constraint
<DatePicker
  selection={date}
  range={{ start: new Date(2024, 0, 1), end: new Date(2024, 11, 31) }}
  onDateChange={setDate}
/>
```

### ColorPicker

Color selection with optional opacity control. **iOS only.**

```tsx
import { ColorPicker } from '@expo/ui/swift-ui';
```

| Prop                | Type                      | Description                              |
| ------------------- | ------------------------- | ---------------------------------------- |
| `label`             | `string`                  | Display label                            |
| `selection`         | `string \| null`          | Color in `#RRGGBB` or `#RRGGBBAA` format |
| `onSelectionChange` | `(value: string) => void` | Color change callback                    |
| `supportsOpacity`   | `boolean`                 | Enable alpha selection                   |

```tsx
const [color, setColor] = useState('#FF6347');

<ColorPicker label="Theme Color" selection={color} onSelectionChange={setColor} />
<ColorPicker label="With Opacity" selection={color} onSelectionChange={setColor} supportsOpacity />
```

### Gauge

Visual value/progress indicator. **iOS only.**

```tsx
import { Gauge } from '@expo/ui/swift-ui';
```

| Prop                | Type        | Default  | Description           |
| ------------------- | ----------- | -------- | --------------------- |
| `value`             | `number`    | required | Current value         |
| `min`               | `number`    | `0`      | Minimum value         |
| `max`               | `number`    | `1`      | Maximum value         |
| `children`          | `ReactNode` | --       | Label                 |
| `currentValueLabel` | `ReactNode` | --       | Current value display |
| `minimumValueLabel` | `ReactNode` | --       | Min value display     |
| `maximumValueLabel` | `ReactNode` | --       | Max value display     |

Key modifiers: `gaugeStyle('automatic' | 'circular' | 'circularCapacity' | 'linear' | 'linearCapacity')`, `tint()`

```tsx
<Gauge value={0.7} modifiers={[gaugeStyle('circular'), tint('green')]}>
  <Text>Battery</Text>
</Gauge>

<Gauge value={75} min={0} max={100}
  currentValueLabel={<Text>75%</Text>}
  minimumValueLabel={<Text>0</Text>}
  maximumValueLabel={<Text>100</Text>}
>
  <Text>Storage</Text>
</Gauge>
```

### ProgressView

Determinate or indeterminate progress indicator.

```tsx
import { ProgressView } from '@expo/ui/swift-ui';
```

| Prop            | Type                           | Description                                     |
| --------------- | ------------------------------ | ----------------------------------------------- |
| `value`         | `number \| null`               | Progress 0-1 (null/undefined for indeterminate) |
| `children`      | `ReactNode`                    | Label                                           |
| `timerInterval` | `{ lower: Date, upper: Date }` | Auto-progress timer (iOS 16+)                   |
| `countsDown`    | `boolean`                      | Timer empties vs fills (default: `true`)        |

Key modifiers: `progressViewStyle('automatic' | 'linear' | 'circular')`, `tint()`

```tsx
// Indeterminate spinner
<ProgressView />

// Determinate bar
<ProgressView value={0.6}>
  <Text>Uploading...</Text>
</ProgressView>

// Circular style
<ProgressView value={0.4} modifiers={[progressViewStyle('circular')]} />

// Timer-based
<ProgressView timerInterval={{ lower: startDate, upper: endDate }} countsDown={false} />
```

---

## Container Components

### Form

Settings-style grouped container. Scrollable by default.

```tsx
import { Form } from '@expo/ui/swift-ui';
```

| Prop       | Type        | Description                       |
| ---------- | ----------- | --------------------------------- |
| `children` | `ReactNode` | Form content (typically Sections) |

Key modifiers: `scrollContentBackground()`, `background()`, `scrollDisabled()`, `refreshable()`

```tsx
<Host style={{ flex: 1 }}>
  <Form>
    <Section title="Profile">
      <TextField placeholder="Name" />
      <TextField placeholder="Email" />
    </Section>
    <Section title="Preferences">
      <Toggle label="Notifications" isOn={notifs} onIsOnChange={setNotifs} />
      <Toggle label="Dark Mode" isOn={dark} onIsOnChange={setDark} />
    </Section>
    <Section>
      <Button label="Save" onPress={handleSave} />
    </Section>
  </Form>
</Host>
```

### List

Scrollable list with native selection, deletion, and reordering.

```tsx
import { List } from '@expo/ui/swift-ui';
```

| Prop                | Type                                        | Description                      |
| ------------------- | ------------------------------------------- | -------------------------------- |
| `children`          | `ReactNode`                                 | List content (Sections, ForEach) |
| `selection`         | `(string \| number)[]`                      | Selected item tags               |
| `onSelectionChange` | `(selection: (string \| number)[]) => void` | Selection callback               |

**List.ForEach** enables delete and reorder:

| Prop       | Type                                                     | Description      |
| ---------- | -------------------------------------------------------- | ---------------- |
| `children` | `ReactNode`                                              | Items            |
| `onDelete` | `(indices: number[]) => void`                            | Delete callback  |
| `onMove`   | `(sourceIndices: number[], destination: number) => void` | Reorder callback |

Key modifiers: `listStyle()`, `listRowBackground()`, `listRowSeparator()`, `listRowInsets()`, `headerProminence()`, `refreshable()`, `environment('editMode', 'active')`

```tsx
<Host style={{ flex: 1 }}>
  <List modifiers={[listStyle('insetGrouped')]}>
    <Section title="Fruits">
      <List.ForEach onDelete={handleDelete}>
        {items.map((item) => (
          <Text key={item.id} modifiers={[tag(item.id)]}>
            {item.name}
          </Text>
        ))}
      </List.ForEach>
    </Section>
  </List>
</Host>
```

### Section

Groups content with headers and footers inside Form or List.

```tsx
import { Section } from '@expo/ui/swift-ui';
```

| Prop                 | Type                            | Description                                     |
| -------------------- | ------------------------------- | ----------------------------------------------- |
| `children`           | `ReactNode`                     | Section content                                 |
| `title`              | `string`                        | Simple text header                              |
| `header`             | `ReactNode`                     | Custom header view                              |
| `footer`             | `ReactNode`                     | Custom footer view                              |
| `isExpanded`         | `boolean`                       | Collapsible state (iOS 17+, sidebar list style) |
| `onIsExpandedChange` | `(isExpanded: boolean) => void` | Expand callback                                 |

```tsx
<Section title="Account">
  <TextField placeholder="Username" />
  <TextField placeholder="Password" />
</Section>

// With custom footer
<Section title="Privacy" footer={<Text>Your data is encrypted end-to-end.</Text>}>
  <Toggle label="Share Analytics" isOn={analytics} onIsOnChange={setAnalytics} />
</Section>
```

### DisclosureGroup

Expandable/collapsible content block. **iOS only.**

```tsx
import { DisclosureGroup } from '@expo/ui/swift-ui';
```

| Prop                 | Type                            | Description                |
| -------------------- | ------------------------------- | -------------------------- |
| `label`              | `string`                        | Disclosure label           |
| `children`           | `ReactNode`                     | Expandable content         |
| `isExpanded`         | `boolean`                       | Controlled expansion state |
| `onIsExpandedChange` | `(isExpanded: boolean) => void` | Expansion callback         |

```tsx
<DisclosureGroup label="Advanced Settings">
  <Toggle label="Debug Mode" isOn={debug} onIsOnChange={setDebug} />
  <TextField placeholder="API Endpoint" />
</DisclosureGroup>;

// Controlled
const [open, setOpen] = useState(false);
<DisclosureGroup label="Details" isExpanded={open} onIsExpandedChange={setOpen}>
  <Text>Detailed information here.</Text>
</DisclosureGroup>;
```

---

## Menu & Overlay Components

### Menu

Tap-triggered dropdown menu.

```tsx
import { Menu } from '@expo/ui/swift-ui';
```

| Prop              | Type                  | Description                                                        |
| ----------------- | --------------------- | ------------------------------------------------------------------ |
| `label`           | `string \| ReactNode` | Menu trigger label                                                 |
| `systemImage`     | `string`              | SF Symbol for trigger                                              |
| `children`        | `ReactNode`           | Menu items (Button, Switch, Picker, Section, Divider, nested Menu) |
| `onPrimaryAction` | `() => void`          | Tap action (menu opens on long-press when set)                     |

```tsx
<Menu label="Options" systemImage="ellipsis.circle">
  <Button label="Edit" systemImage="pencil" onPress={handleEdit} />
  <Button label="Share" systemImage="square.and.arrow.up" onPress={handleShare} />
  <Divider />
  <Button label="Delete" role="destructive" systemImage="trash" onPress={handleDelete} />
</Menu>

// Nested submenu
<Menu label="Sort By">
  <Button label="Name" onPress={() => sort('name')} />
  <Button label="Date" onPress={() => sort('date')} />
  <Menu label="Custom">
    <Button label="Priority" onPress={() => sort('priority')} />
  </Menu>
</Menu>

// Primary action (tap = action, long-press = menu)
<Menu label="Add" onPrimaryAction={() => quickAdd()}>
  <Button label="From Camera" systemImage="camera" onPress={fromCamera} />
  <Button label="From Library" systemImage="photo" onPress={fromLibrary} />
</Menu>
```

### ContextMenu

Long-press context menu with optional preview.

```tsx
import { ContextMenu } from '@expo/ui/swift-ui';
```

| Prop       | Type        | Description                                         |
| ---------- | ----------- | --------------------------------------------------- |
| `children` | `ReactNode` | Must contain Trigger, Items, and optionally Preview |

**Subcomponents:**

- `ContextMenu.Trigger` -- Visible element (long-press to open)
- `ContextMenu.Items` -- Menu content (Button, Switch, Picker, Section, Divider, nested ContextMenu)
- `ContextMenu.Preview` -- Preview shown above menu

```tsx
<ContextMenu>
  <ContextMenu.Trigger>
    <Label title="Hold me" systemImage="hand.tap" />
  </ContextMenu.Trigger>
  <ContextMenu.Items>
    <Button label="Copy" systemImage="doc.on.doc" onPress={handleCopy} />
    <Button
      label="Share"
      systemImage="square.and.arrow.up"
      onPress={handleShare}
    />
    <Divider />
    <Button
      label="Delete"
      role="destructive"
      systemImage="trash"
      onPress={handleDelete}
    />
  </ContextMenu.Items>
  <ContextMenu.Preview>
    <VStack>
      <Text modifiers={[font({ size: 20, weight: 'bold' })]}>
        Preview Content
      </Text>
    </VStack>
  </ContextMenu.Preview>
</ContextMenu>
```

### Popover

Anchored floating overlay. **iOS only.**

```tsx
import { Popover } from '@expo/ui/swift-ui';
```

| Prop                  | Type                                                       | Default  | Description                      |
| --------------------- | ---------------------------------------------------------- | -------- | -------------------------------- |
| `isPresented`         | `boolean`                                                  | --       | Show/hide popover                |
| `onIsPresentedChange` | `(isPresented: boolean) => void`                           | --       | Presentation callback            |
| `attachmentAnchor`    | `'leading' \| 'trailing' \| 'center' \| 'top' \| 'bottom'` | --       | Anchor point                     |
| `arrowEdge`           | `'leading' \| 'trailing' \| 'top' \| 'bottom' \| 'none'`   | `'none'` | Arrow edge                       |
| `children`            | `ReactNode`                                                | --       | Must contain Trigger and Content |

**Subcomponents:**

- `Popover.Trigger` -- Element that anchors the popover
- `Popover.Content` -- Content shown in the popover

```tsx
const [show, setShow] = useState(false);

<Popover isPresented={show} onIsPresentedChange={setShow} arrowEdge="top">
  <Popover.Trigger>
    <Button label="Show Info" onPress={() => setShow(true)} />
  </Popover.Trigger>
  <Popover.Content>
    <VStack spacing={8}>
      <Text modifiers={[font({ weight: 'bold' })]}>Details</Text>
      <Text>Additional information here.</Text>
    </VStack>
  </Popover.Content>
</Popover>;
```

### BottomSheet

Modal sheet with detents and drag indicator.

```tsx
import { BottomSheet } from '@expo/ui/swift-ui';
```

| Prop                  | Type                             | Default | Description           |
| --------------------- | -------------------------------- | ------- | --------------------- |
| `isPresented`         | `boolean`                        | --      | Show/hide sheet       |
| `onIsPresentedChange` | `(isPresented: boolean) => void` | --      | Presentation callback |
| `fitToContents`       | `boolean`                        | `false` | Auto-size to content  |
| `children`            | `ReactNode`                      | --      | Sheet content         |

Use `Group` wrapper to apply presentation modifiers:

```tsx
import { presentationDetents, presentationDragIndicator, interactiveDismissDisabled } from '@expo/ui/swift-ui/modifiers';

const [show, setShow] = useState(false);

<BottomSheet isPresented={show} onIsPresentedChange={setShow}>
  <Group modifiers={[
    presentationDetents(['medium', 'large']),
    presentationDragIndicator('visible'),
  ]}>
    <VStack spacing={12}>
      <Text modifiers={[font({ size: 20, weight: 'bold' })]}>Sheet Title</Text>
      <Text>Sheet content goes here.</Text>
      <Button label="Close" onPress={() => setShow(false)} />
    </VStack>
  </Group>
</BottomSheet>

// With React Native content inside
<BottomSheet isPresented={show} onIsPresentedChange={setShow}>
  <RNHostView matchContents>
    <View style={{ padding: 20 }}>
      <RNText>React Native inside a SwiftUI sheet</RNText>
    </View>
  </RNHostView>
</BottomSheet>
```

**Presentation detent values:** `'medium'`, `'large'`, `{ fraction: 0.3 }`, `{ height: 200 }`
