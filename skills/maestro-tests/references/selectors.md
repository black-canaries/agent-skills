# Maestro Selector Reference

## Selector Priority (most to least reliable)

1. **id** (testID) - Most stable, won't break on text changes
2. **text** - Works for static labels, fragile for dynamic content
3. **Relative selectors** - Disambiguate when multiple matches exist
4. **point** - Last resort, breaks on layout changes

## ID Selector (testID)

Maps directly to React Native's `testID` prop.

```yaml
- tapOn:
    id: "submit-button"

- assertVisible:
    id: "home-screen"

- longPressOn:
    id: "item-card"
```

## Text Selector

Matches visible text or accessibility label.

```yaml
# Exact match
- tapOn: "Sign In"

# Regex pattern
- tapOn:
    text: "Item \\d+"           # Matches "Item 1", "Item 42", etc.

# Case-sensitive by default
- tapOn:
    text: "Submit"
```

## Point Selector

Target by screen coordinates.

```yaml
# Percentage (responsive)
- tapOn:
    point: "50%, 50%"          # Center of screen

# Absolute pixels (fragile)
- tapOn:
    point: "200, 400"
```

## Index Selector

When multiple elements match, pick by index (0-based).

```yaml
- tapOn:
    text: "Delete"
    index: 0                   # First "Delete" button

- tapOn:
    id: "list-item"
    index: 3                   # Fourth item
```

## State Selectors

Filter by element state.

```yaml
- tapOn:
    id: "submit-button"
    enabled: true              # Only enabled elements

- assertVisible:
    id: "checkbox"
    checked: true              # Checked state

- tapOn:
    id: "input-field"
    focused: true              # Focused state

- assertVisible:
    id: "tab-home"
    selected: true             # Selected state
```

## Size Selectors

Filter by element dimensions.

```yaml
- tapOn:
    text: "Icon"
    width: 44
    height: 44
    tolerance: 5               # +/- 5px variance allowed
```

## Relative Position Selectors

Find elements relative to other elements.

```yaml
# Below another element
- tapOn:
    id: "edit-button"
    below: "Section Title"

# Above another element
- tapOn:
    text: "Cancel"
    above: "Footer"

# Left/right of another element
- tapOn:
    id: "delete-icon"
    rightOf: "Item Name"

- tapOn:
    text: "Back"
    leftOf: "Title"
```

## Hierarchy Selectors

Find elements by parent/child relationships.

```yaml
# Element contains a specific child
- tapOn:
    containsChild:
      id: "star-icon"

# Element is child of container
- tapOn:
    id: "action-button"
    childOf:
      id: "toolbar"

# Element has a specific descendant
- tapOn:
    containsDescendants:
      - id: "avatar"
      - text: "John"
```

## Trait Selectors

Filter by element traits.

```yaml
# Any text element
- tapOn:
    traits: text

# Long text (200+ chars)
- assertVisible:
    traits: long-text

# Square elements (width/height variance < 3%)
- tapOn:
    traits: square
```

## Optional Selector

Skip assertion if element not found (doesn't fail the flow).

```yaml
- assertVisible:
    id: "promotional-banner"
    optional: true             # Won't fail if banner isn't shown
```

## Combining Selectors

Multiple selectors act as AND conditions.

```yaml
- tapOn:
    id: "action-button"
    below: "Header"
    enabled: true
    index: 0
```

## Debugging Selectors

When selectors don't work:

1. Run `maestro hierarchy` to inspect the view tree
2. Use `maestro studio` for visual element picking
3. Check that `testID` is set on the correct element (not a wrapper)
4. On iOS, ensure parent has `accessible={false}` for nested tappable elements
