# React Native testID Patterns for Maestro

## Naming Convention

Use `kebab-case` with a descriptive pattern: `{feature}-{element-type}`

```
login-email-input
login-password-input
login-submit-button
home-screen
profile-avatar
cart-item-0
settings-toggle-notifications
```

## Where to Add testIDs

Add `testID` to every interactive element and key landmarks:

### Buttons / Pressables
```tsx
<Pressable testID="login-submit-button" onPress={handleSubmit}>
  <Text>Sign In</Text>
</Pressable>

<TouchableOpacity testID="cart-checkout-button" onPress={onCheckout}>
  <Text>Checkout</Text>
</TouchableOpacity>
```

### Text Inputs
```tsx
<TextInput
  testID="login-email-input"
  placeholder="Email"
  value={email}
  onChangeText={setEmail}
/>
```

### Screen Containers (for assertVisible)
```tsx
export default function HomeScreen() {
  return (
    <View testID="home-screen" className="flex-1">
      {/* screen content */}
    </View>
  );
}
```

### List Items (with dynamic index)
```tsx
{items.map((item, index) => (
  <Pressable
    key={item.id}
    testID={`item-card-${index}`}
    onPress={() => onSelect(item)}
  >
    <Text>{item.name}</Text>
  </Pressable>
))}
```

### Tab Bar Items
```tsx
<Pressable testID="tab-home" onPress={() => navigate('Home')}>
  <Icon name="home" />
  <Text>Home</Text>
</Pressable>
```

### Toggle / Switch
```tsx
<Switch
  testID="settings-toggle-notifications"
  value={notificationsEnabled}
  onValueChange={setNotificationsEnabled}
/>
```

### Modal / Sheet
```tsx
<Modal testID="confirm-delete-modal" visible={showModal}>
  <Pressable testID="confirm-delete-yes" onPress={onDelete}>
    <Text>Delete</Text>
  </Pressable>
  <Pressable testID="confirm-delete-cancel" onPress={onCancel}>
    <Text>Cancel</Text>
  </Pressable>
</Modal>
```

## iOS Nested Tappable Elements

When tappable elements are nested, iOS accessibility can prevent Maestro from reaching the inner element. Fix by disabling accessibility on the parent:

```tsx
// BAD - Maestro can't tap the inner button on iOS
<TouchableOpacity onPress={onCardPress}>
  <View>
    <Text>Card Title</Text>
    <TouchableOpacity onPress={onDelete}>
      <Text>Delete</Text>
    </TouchableOpacity>
  </View>
</TouchableOpacity>

// GOOD - accessible={false} on parent lets Maestro reach inner elements
<TouchableOpacity
  accessible={false}
  onPress={onCardPress}
  testID="item-card"
>
  <View>
    <Text>Card Title</Text>
    <TouchableOpacity
      accessible={true}
      testID="item-delete-button"
      onPress={onDelete}
    >
      <Text>Delete</Text>
    </TouchableOpacity>
  </View>
</TouchableOpacity>
```

## Expo Router Screen testIDs

For Expo Router screens, add testID to the root container of each screen:

```tsx
// app/(drawer)/home.tsx
export default function HomeScreen() {
  return (
    <ScrollView
      testID="home-screen"
      contentInsetAdjustmentBehavior="automatic"
    >
      {/* content */}
    </ScrollView>
  );
}

// app/(auth)/login.tsx
export default function LoginScreen() {
  return (
    <KeyboardAvoidingView testID="login-screen" className="flex-1">
      <TextInput testID="login-email-input" />
      <TextInput testID="login-password-input" secureTextEntry />
      <Pressable testID="login-submit-button">
        <Text>Sign In</Text>
      </Pressable>
    </KeyboardAvoidingView>
  );
}
```

## testID Audit Checklist

When preparing an app for Maestro testing, check:

- [ ] Every screen's root container has a `testID` (e.g., `home-screen`, `login-screen`)
- [ ] Every button/pressable has a `testID`
- [ ] Every text input has a `testID`
- [ ] Every toggle/switch has a `testID`
- [ ] Tab bar items have `testID`s
- [ ] List items use indexed `testID`s (e.g., `item-card-0`)
- [ ] Modals/sheets have `testID`s on the container and action buttons
- [ ] Nested tappable elements use `accessible={false}` on the parent (iOS)
- [ ] No duplicate `testID` values across the app (use feature prefix)
