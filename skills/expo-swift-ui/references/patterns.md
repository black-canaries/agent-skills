# Common SwiftUI Patterns

Real-world patterns for building native iOS interfaces with `@expo/ui/swift-ui`.

---

## Settings Screen

The most common use case -- a native iOS Settings-style form.

```tsx
import { useState } from 'react';
import {
  Host,
  Form,
  Section,
  Toggle,
  Picker,
  Text,
  Button,
  TextField,
  Slider,
} from '@expo/ui/swift-ui';
import { pickerStyle, tag, tint } from '@expo/ui/swift-ui/modifiers';

export default function SettingsScreen() {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [fontSize, setFontSize] = useState(16);
  const [language, setLanguage] = useState('en');

  return (
    <Host style={{ flex: 1 }}>
      <Form>
        <Section title="General">
          <Toggle
            label="Notifications"
            systemImage="bell.fill"
            isOn={notifications}
            onIsOnChange={setNotifications}
          />
          <Toggle
            label="Dark Mode"
            systemImage="moon.fill"
            isOn={darkMode}
            onIsOnChange={setDarkMode}
          />
        </Section>

        <Section title="Display">
          <Slider
            value={fontSize}
            min={12}
            max={24}
            step={1}
            label={<Text>Font Size</Text>}
            minimumValueLabel={<Text>A</Text>}
            maximumValueLabel={<Text>A</Text>}
            onValueChange={setFontSize}
          />
        </Section>

        <Section title="Language">
          <Picker
            modifiers={[pickerStyle('menu')]}
            label="Language"
            selection={language}
            onSelectionChange={setLanguage}
          >
            <Text modifiers={[tag('en')]}>English</Text>
            <Text modifiers={[tag('es')]}>Spanish</Text>
            <Text modifiers={[tag('fr')]}>French</Text>
          </Picker>
        </Section>

        <Section>
          <Button label="Sign Out" role="destructive" onPress={() => {}} />
        </Section>
      </Form>
    </Host>
  );
}
```

---

## Data List with Selection and Actions

```tsx
import { useState, useCallback } from 'react';
import { Host, List, Section, Text, Button } from '@expo/ui/swift-ui';
import {
  listStyle,
  tag,
  environment,
  refreshable,
  listRowBackground,
} from '@expo/ui/swift-ui/modifiers';

interface Item {
  id: string;
  name: string;
  category: string;
}

export default function DataListScreen() {
  const [items, setItems] = useState<Item[]>([
    { id: '1', name: 'Apples', category: 'Fruits' },
    { id: '2', name: 'Bananas', category: 'Fruits' },
    { id: '3', name: 'Carrots', category: 'Vegetables' },
  ]);
  const [selected, setSelected] = useState<string[]>([]);
  const [editing, setEditing] = useState(false);

  const handleDelete = useCallback((indices: number[]) => {
    setItems((prev) => prev.filter((_, i) => !indices.includes(i)));
  }, []);

  const handleRefresh = useCallback(async () => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    // Fetch new data
  }, []);

  const grouped = items.reduce(
    (acc, item) => {
      (acc[item.category] ??= []).push(item);
      return acc;
    },
    {} as Record<string, Item[]>
  );

  return (
    <Host style={{ flex: 1 }}>
      <List
        modifiers={[
          listStyle('insetGrouped'),
          refreshable(handleRefresh),
          ...(editing ? [environment('editMode', 'active')] : []),
        ]}
        selection={selected}
        onSelectionChange={setSelected}
      >
        {Object.entries(grouped).map(([category, categoryItems]) => (
          <Section key={category} title={category}>
            <List.ForEach onDelete={handleDelete}>
              {categoryItems.map((item) => (
                <Text key={item.id} modifiers={[tag(item.id)]}>
                  {item.name}
                </Text>
              ))}
            </List.ForEach>
          </Section>
        ))}
      </List>
    </Host>
  );
}
```

---

## Action Menu with Context Menu

```tsx
import {
  Host,
  ContextMenu,
  Label,
  Button,
  Divider,
  Section,
  VStack,
  Text,
} from '@expo/ui/swift-ui';
import { font, foregroundStyle } from '@expo/ui/swift-ui/modifiers';

function ItemCard({ item, onEdit, onShare, onDelete }) {
  return (
    <Host matchContents>
      <ContextMenu>
        <ContextMenu.Trigger>
          <VStack spacing={4}>
            <Text modifiers={[font({ size: 16, weight: 'semibold' })]}>
              {item.title}
            </Text>
            <Text
              modifiers={[
                font({ size: 14 }),
                foregroundStyle({ type: 'hierarchical', style: 'secondary' }),
              ]}
            >
              {item.subtitle}
            </Text>
          </VStack>
        </ContextMenu.Trigger>
        <ContextMenu.Items>
          <Section>
            <Button
              label="Edit"
              systemImage="pencil"
              onPress={() => onEdit(item)}
            />
            <Button
              label="Share"
              systemImage="square.and.arrow.up"
              onPress={() => onShare(item)}
            />
          </Section>
          <Section>
            <Button
              label="Delete"
              systemImage="trash"
              role="destructive"
              onPress={() => onDelete(item)}
            />
          </Section>
        </ContextMenu.Items>
        <ContextMenu.Preview>
          <VStack spacing={8}>
            <Text modifiers={[font({ size: 20, weight: 'bold' })]}>
              {item.title}
            </Text>
            <Text>{item.description}</Text>
          </VStack>
        </ContextMenu.Preview>
      </ContextMenu>
    </Host>
  );
}
```

---

## Bottom Sheet with Form

```tsx
import { useState } from 'react';
import {
  Host,
  BottomSheet,
  Group,
  Form,
  Section,
  TextField,
  Toggle,
  Button,
  Text,
} from '@expo/ui/swift-ui';
import {
  presentationDetents,
  presentationDragIndicator,
} from '@expo/ui/swift-ui/modifiers';

export default function SheetFormExample() {
  const [showSheet, setShowSheet] = useState(false);
  const [name, setName] = useState('');
  const [urgent, setUrgent] = useState(false);

  return (
    <Host style={{ flex: 1 }}>
      <Button label="Add New Item" onPress={() => setShowSheet(true)} />

      <BottomSheet isPresented={showSheet} onIsPresentedChange={setShowSheet}>
        <Group
          modifiers={[
            presentationDetents(['medium', 'large']),
            presentationDragIndicator('visible'),
          ]}
        >
          <Form>
            <Section title="New Item">
              <TextField placeholder="Item name" onChangeText={setName} />
              <Toggle label="Urgent" isOn={urgent} onIsOnChange={setUrgent} />
            </Section>
            <Section>
              <Button
                label="Save"
                onPress={() => {
                  // Save logic
                  setShowSheet(false);
                }}
              />
              <Button
                label="Cancel"
                role="cancel"
                onPress={() => setShowSheet(false)}
              />
            </Section>
          </Form>
        </Group>
      </BottomSheet>
    </Host>
  );
}
```

---

## Popover with Info

```tsx
import { useState } from 'react';
import {
  Host,
  Popover,
  Button,
  VStack,
  Text,
  HStack,
  Image,
  Spacer,
} from '@expo/ui/swift-ui';
import {
  font,
  foregroundStyle,
  frame,
  padding,
} from '@expo/ui/swift-ui/modifiers';

export default function InfoPopoverExample() {
  const [show, setShow] = useState(false);

  return (
    <Host matchContents>
      <Popover
        isPresented={show}
        onIsPresentedChange={setShow}
        arrowEdge="bottom"
      >
        <Popover.Trigger>
          <Button
            label="Info"
            systemImage="info.circle"
            onPress={() => setShow(true)}
          />
        </Popover.Trigger>
        <Popover.Content>
          <VStack
            spacing={8}
            modifiers={[padding({ all: 16 }), frame({ width: 250 })]}
          >
            <HStack spacing={8}>
              <Image
                systemName="checkmark.circle.fill"
                color="green"
                size={20}
              />
              <Text modifiers={[font({ weight: 'bold' })]}>Status: Active</Text>
            </HStack>
            <Text
              modifiers={[
                foregroundStyle({ type: 'hierarchical', style: 'secondary' }),
              ]}
            >
              Last updated 2 minutes ago
            </Text>
          </VStack>
        </Popover.Content>
      </Popover>
    </Host>
  );
}
```

---

## Segmented Control with Content

```tsx
import { useState } from 'react';
import { Host, VStack, Picker, Text, List, Section } from '@expo/ui/swift-ui';
import { pickerStyle, tag, font, padding } from '@expo/ui/swift-ui/modifiers';

const tabs = ['All', 'Active', 'Completed'];

export default function SegmentedExample() {
  const [tab, setTab] = useState(tabs[0]);

  return (
    <Host style={{ flex: 1 }}>
      <VStack>
        <Picker
          modifiers={[
            pickerStyle('segmented'),
            padding({ horizontal: 16, vertical: 8 }),
          ]}
          selection={tab}
          onSelectionChange={setTab}
        >
          {tabs.map((t) => (
            <Text key={t} modifiers={[tag(t)]}>
              {t}
            </Text>
          ))}
        </Picker>

        <List>
          <Section title={tab}>
            <Text>Filtered content for: {tab}</Text>
          </Section>
        </List>
      </VStack>
    </Host>
  );
}
```

---

## Progress Dashboard

```tsx
import {
  Host,
  VStack,
  HStack,
  Gauge,
  ProgressView,
  Text,
  Spacer,
} from '@expo/ui/swift-ui';
import {
  gaugeStyle,
  tint,
  font,
  foregroundStyle,
  frame,
  padding,
} from '@expo/ui/swift-ui/modifiers';

export default function DashboardExample() {
  return (
    <Host matchContents>
      <VStack spacing={20} modifiers={[padding({ all: 16 })]}>
        <Text modifiers={[font({ size: 24, weight: 'bold' })]}>Dashboard</Text>

        <HStack spacing={24}>
          <VStack spacing={4}>
            <Gauge
              value={0.72}
              modifiers={[
                gaugeStyle('circularCapacity'),
                tint('green'),
                frame({ width: 80, height: 80 }),
              ]}
              currentValueLabel={<Text>72%</Text>}
            >
              <Text>CPU</Text>
            </Gauge>
          </VStack>

          <VStack spacing={4}>
            <Gauge
              value={0.45}
              modifiers={[
                gaugeStyle('circularCapacity'),
                tint('blue'),
                frame({ width: 80, height: 80 }),
              ]}
              currentValueLabel={<Text>45%</Text>}
            >
              <Text>Memory</Text>
            </Gauge>
          </VStack>

          <VStack spacing={4}>
            <Gauge
              value={0.89}
              modifiers={[
                gaugeStyle('circularCapacity'),
                tint('orange'),
                frame({ width: 80, height: 80 }),
              ]}
              currentValueLabel={<Text>89%</Text>}
            >
              <Text>Disk</Text>
            </Gauge>
          </VStack>
        </HStack>

        <VStack spacing={8}>
          <HStack>
            <Text>Upload Progress</Text>
            <Spacer />
            <Text
              modifiers={[
                foregroundStyle({ type: 'hierarchical', style: 'secondary' }),
              ]}
            >
              3 of 5 files
            </Text>
          </HStack>
          <ProgressView value={0.6} modifiers={[tint('purple')]} />
        </VStack>
      </VStack>
    </Host>
  );
}
```

---

## Mixing React Native and SwiftUI

Use `RNHostView` to embed React Native views inside SwiftUI containers.

```tsx
import { View, Text as RNText, Pressable } from 'react-native';
import {
  Host,
  BottomSheet,
  RNHostView,
  Group,
  VStack,
  Text,
  Button,
} from '@expo/ui/swift-ui';
import {
  presentationDetents,
  presentationDragIndicator,
} from '@expo/ui/swift-ui/modifiers';

export default function MixedExample() {
  const [show, setShow] = useState(false);

  return (
    <View style={{ flex: 1 }}>
      {/* React Native content */}
      <Pressable onPress={() => setShow(true)}>
        <RNText>Open SwiftUI Sheet</RNText>
      </Pressable>

      {/* SwiftUI bottom sheet */}
      <Host matchContents>
        <BottomSheet isPresented={show} onIsPresentedChange={setShow}>
          <Group
            modifiers={[
              presentationDetents(['medium']),
              presentationDragIndicator('visible'),
            ]}
          >
            <VStack spacing={12}>
              <Text>SwiftUI content above</Text>

              {/* React Native inside SwiftUI */}
              <RNHostView matchContents>
                <View
                  style={{
                    padding: 16,
                    backgroundColor: '#f0f0f0',
                    borderRadius: 12,
                  }}
                >
                  <RNText style={{ fontSize: 16 }}>
                    React Native content inside SwiftUI sheet
                  </RNText>
                </View>
              </RNHostView>

              <Button label="Close" onPress={() => setShow(false)} />
            </VStack>
          </Group>
        </BottomSheet>
      </Host>
    </View>
  );
}
```

---

## Dropdown Menu Button

```tsx
import { Host, Menu, Button, Divider } from '@expo/ui/swift-ui';
import { labelStyle } from '@expo/ui/swift-ui/modifiers';

// Icon-only menu button (common "..." pattern)
function MoreButton({ onEdit, onDuplicate, onDelete }) {
  return (
    <Host matchContents>
      <Menu
        label="More"
        systemImage="ellipsis.circle"
        modifiers={[labelStyle('iconOnly')]}
      >
        <Button label="Edit" systemImage="pencil" onPress={onEdit} />
        <Button
          label="Duplicate"
          systemImage="doc.on.doc"
          onPress={onDuplicate}
        />
        <Divider />
        <Button
          label="Delete"
          systemImage="trash"
          role="destructive"
          onPress={onDelete}
        />
      </Menu>
    </Host>
  );
}

// Menu with primary action (tap does default, long-press shows options)
function AddButton({ onQuickAdd, onFromCamera, onFromLibrary }) {
  return (
    <Host matchContents>
      <Menu label="Add" systemImage="plus" onPrimaryAction={onQuickAdd}>
        <Button
          label="Take Photo"
          systemImage="camera"
          onPress={onFromCamera}
        />
        <Button
          label="Photo Library"
          systemImage="photo"
          onPress={onFromLibrary}
        />
      </Menu>
    </Host>
  );
}
```

---

## Collapsible Sections

```tsx
import { useState } from 'react';
import { Host, List, Section, Text, Toggle } from '@expo/ui/swift-ui';
import { listStyle } from '@expo/ui/swift-ui/modifiers';

export default function CollapsibleSections() {
  const [generalOpen, setGeneralOpen] = useState(true);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [debug, setDebug] = useState(false);

  return (
    <Host style={{ flex: 1 }}>
      <List modifiers={[listStyle('sidebar')]}>
        <Section
          title="General"
          isExpanded={generalOpen}
          onIsExpandedChange={setGeneralOpen}
        >
          <Text>Account Settings</Text>
          <Text>Preferences</Text>
        </Section>

        <Section
          title="Advanced"
          isExpanded={advancedOpen}
          onIsExpandedChange={setAdvancedOpen}
        >
          <Toggle label="Debug Mode" isOn={debug} onIsOnChange={setDebug} />
          <Text>Developer Options</Text>
        </Section>
      </List>
    </Host>
  );
}
```

---

## Color Theme Picker

```tsx
import { useState } from 'react';
import {
  Host,
  Form,
  Section,
  ColorPicker,
  Toggle,
  Text,
} from '@expo/ui/swift-ui';
import { foregroundStyle } from '@expo/ui/swift-ui/modifiers';

export default function ThemeEditor() {
  const [primary, setPrimary] = useState('#007AFF');
  const [accent, setAccent] = useState('#FF9500');
  const [useCustom, setUseCustom] = useState(false);

  return (
    <Host style={{ flex: 1 }}>
      <Form>
        <Section title="Theme Colors">
          <Toggle
            label="Custom Theme"
            isOn={useCustom}
            onIsOnChange={setUseCustom}
          />
          {useCustom && (
            <>
              <ColorPicker
                label="Primary Color"
                selection={primary}
                onSelectionChange={setPrimary}
              />
              <ColorPicker
                label="Accent Color"
                selection={accent}
                onSelectionChange={setAccent}
                supportsOpacity
              />
            </>
          )}
        </Section>
        <Section title="Preview">
          <Text modifiers={[foregroundStyle({ color: primary })]}>
            Primary Text
          </Text>
          <Text modifiers={[foregroundStyle({ color: accent })]}>
            Accent Text
          </Text>
        </Section>
      </Form>
    </Host>
  );
}
```

---

## Date Range Selection

```tsx
import { useState } from 'react';
import { Host, Form, Section, DatePicker, Text } from '@expo/ui/swift-ui';
import { datePickerStyle } from '@expo/ui/swift-ui/modifiers';

export default function DateRangeForm() {
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date(Date.now() + 86400000 * 7));

  return (
    <Host style={{ flex: 1 }}>
      <Form>
        <Section title="Trip Dates">
          <DatePicker
            title="Departure"
            selection={startDate}
            displayedComponents={['date']}
            range={{ start: new Date() }}
            onDateChange={setStartDate}
          />
          <DatePicker
            title="Return"
            selection={endDate}
            displayedComponents={['date']}
            range={{ start: startDate }}
            onDateChange={setEndDate}
          />
        </Section>
        <Section title="Time">
          <DatePicker
            title="Check-in Time"
            selection={startDate}
            displayedComponents={['hourAndMinute']}
            onDateChange={setStartDate}
          />
        </Section>
        <Section
          title="Calendar View"
          footer={<Text>Select your preferred date</Text>}
        >
          <DatePicker
            modifiers={[datePickerStyle('graphical')]}
            selection={startDate}
            displayedComponents={['date']}
            onDateChange={setStartDate}
          />
        </Section>
      </Form>
    </Host>
  );
}
```
