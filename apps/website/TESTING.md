# Testing Framework Documentation

## Overview

The design system components are tested using **Jest** and **React Testing Library**, following Next.js testing best practices.

## Test Setup

### Configuration Files

- **`jest.config.js`**: Jest configuration using Next.js Jest preset
- **`jest.setup.js`**: Test environment setup with mocks for Next.js router and Link components

### Dependencies

```json
{
  "devDependencies": {
    "jest": "^29.0.0",
    "jest-environment-jsdom": "^29.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@testing-library/user-event": "^14.0.0"
  }
}
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## Test Structure

Tests are located in `components/design-system/__tests__/` directory:

- `Button.test.tsx` - Button component tests
- `TextField.test.tsx` - TextField component tests
- `Alert.test.tsx` - Alert component tests
- `Chip.test.tsx` - Chip component tests
- `Tabs.test.tsx` - Tabs component tests
- `Container.test.tsx` - Container component tests
- `Stack.test.tsx` - Stack component tests
- `Typography.test.tsx` - Typography component tests

## Test Coverage

### Current Coverage

- **8 test suites** (all passing)
- **63 tests** (all passing)
- Components tested:
  - Button (12 tests)
  - TextField (8 tests)
  - Alert (8 tests)
  - Chip (9 tests)
  - Tabs (6 tests)
  - Container (4 tests)
  - Stack (6 tests)
  - Typography (10 tests)

### Test Categories

1. **Rendering Tests**: Verify components render correctly
2. **Interaction Tests**: Test user interactions (clicks, changes)
3. **Props Tests**: Verify props are applied correctly
4. **State Tests**: Test component state changes
5. **Accessibility Tests**: Verify ARIA attributes and roles

## Testing Patterns

### Basic Component Test

```typescript
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import Button from '../Button'

describe('Button Component', () => {
  it('renders button with children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

### Interaction Test

```typescript
it('calls onClick when clicked', () => {
  const handleClick = jest.fn()
  render(<Button onClick={handleClick}>Click me</Button>)
  
  const button = screen.getByText('Click me')
  fireEvent.click(button)
  
  expect(handleClick).toHaveBeenCalledTimes(1)
})
```

### Props Test

```typescript
it('renders with primary variant by default', () => {
  render(<Button>Primary</Button>)
  const button = screen.getByText('Primary').closest('button')!
  expect(button.className).toContain('button-primary')
})
```

## Best Practices

1. **Use `screen` queries**: Prefer `screen.getBy*` over container queries
2. **Test user behavior**: Test what users see and do, not implementation details
3. **Accessibility first**: Use `getByRole`, `getByLabelText` for accessible queries
4. **Clean up**: Tests automatically clean up after each test
5. **Mock external dependencies**: Mock Next.js router and Link components

## Common Patterns

### Testing Nested Components

When components wrap children in additional elements, use `.closest()`:

```typescript
const button = screen.getByText('Label').closest('button')!
expect(button.className).toContain('expected-class')
```

### Testing Inline Styles

```typescript
const element = screen.getByText('Text')
expect(element.style.width).toBe('100%')
```

### Testing Class Names

```typescript
const element = screen.getByText('Text')
expect(element.className).toContain('expected-class')
```

## Next Steps

To add more tests:

1. Create test file: `components/design-system/__tests__/ComponentName.test.tsx`
2. Import component and testing utilities
3. Write test cases covering:
   - Basic rendering
   - Props variations
   - User interactions
   - Edge cases
4. Run tests: `npm test`

## References

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Next.js Testing](https://nextjs.org/docs/testing)
