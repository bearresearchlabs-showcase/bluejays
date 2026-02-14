# Development Guide

## Testing-Driven Development Workflow

This project uses a **testing-first approach** to guide development. All new features and components must include tests.

## Quick Start

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (for development)
npm run test:watch

# Run tests with coverage report
npm run test:coverage

# Run tests for specific component
npm test -- Button

# Run tests matching a pattern
npm test -- --testNamePattern="renders"
```

### Pre-commit Checks

Before committing code, run:

```bash
# Run all pre-commit checks
./scripts/pre-commit.sh

# Or manually:
npm run lint
npm test
npx tsc --noEmit
```

## Development Workflow

### 1. Create Component with Tests

When creating a new component:

1. **Create the component file**:
   ```
   components/design-system/NewComponent.tsx
   ```

2. **Create test file** (in parallel):
   ```
   components/design-system/__tests__/NewComponent.test.tsx
   ```

3. **Write tests first** (TDD approach):
   ```typescript
   describe('NewComponent', () => {
     it('renders correctly', () => {
       render(<NewComponent />)
       expect(screen.getByRole('...')).toBeInTheDocument()
     })
   })
   ```

4. **Implement component** to pass tests

5. **Run tests**:
   ```bash
   npm test -- NewComponent
   ```

### 2. Test Coverage Requirements

- **Minimum coverage**: 60% for all code
- **Design system components**: 70% coverage required
- **New features**: Must include tests before merging

### 3. Test Checklist

Before submitting a PR, ensure:

- [ ] All tests pass (`npm test`)
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] No linting errors (`npm run lint`)
- [ ] Test coverage meets threshold (`npm run test:coverage`)
- [ ] Tests cover:
  - [ ] Component rendering
  - [ ] User interactions
  - [ ] Props variations
  - [ ] Edge cases
  - [ ] Accessibility (ARIA attributes)

## Test Structure

### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import Component from '../Component'

describe('Component', () => {
  // Rendering tests
  it('renders correctly', () => {})
  
  // Interaction tests
  it('handles user interactions', () => {})
  
  // Props tests
  it('applies props correctly', () => {})
  
  // Edge cases
  it('handles edge cases', () => {})
})
```

### Integration Tests

For testing component interactions:

```typescript
describe('Component Integration', () => {
  it('works with other components', () => {})
})
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- **Push to main/develop**: Full test suite
- **Pull requests**: Pre-commit checks + tests
- **Scheduled**: Daily test runs

### Test Reports

- Coverage reports: Available in GitHub Actions artifacts
- Test results: Displayed in PR checks
- Coverage badges: Can be added to README

## Best Practices

### 1. Test User Behavior

✅ **Good**: Test what users see and do
```typescript
it('shows error message when form is invalid', () => {
  render(<Form />)
  fireEvent.click(screen.getByText('Submit'))
  expect(screen.getByText('Please fill all fields')).toBeInTheDocument()
})
```

❌ **Bad**: Test implementation details
```typescript
it('sets state.error to true', () => {
  // Don't test internal state
})
```

### 2. Use Accessible Queries

✅ **Good**: Use semantic queries
```typescript
screen.getByRole('button', { name: 'Submit' })
screen.getByLabelText('Email')
screen.getByText('Error message')
```

❌ **Bad**: Use non-semantic queries
```typescript
screen.getByTestId('submit-button') // Only if necessary
```

### 3. Keep Tests Isolated

Each test should:
- Be independent (no shared state)
- Clean up after itself
- Not depend on other tests

### 4. Test Edge Cases

Don't just test the happy path:
- Empty states
- Error states
- Loading states
- Disabled states
- Invalid inputs

### 5. Mock External Dependencies

Mock Next.js features:
```typescript
// Already set up in jest.setup.js
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
  usePathname: () => '/',
}))
```

## Debugging Tests

### Run Single Test

```bash
npm test -- --testNamePattern="specific test name"
```

### Debug Mode

```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

### Watch Mode

```bash
npm run test:watch
```

## Coverage Reports

After running `npm run test:coverage`:

- **HTML report**: `coverage/lcov-report/index.html`
- **Text summary**: Displayed in terminal
- **LCOV file**: `coverage/lcov.info` (for CI/CD)

## Common Issues

### Tests Fail After Component Changes

1. Check if component API changed
2. Update tests to match new API
3. Verify test assertions are correct

### Coverage Below Threshold

1. Identify untested code paths
2. Add tests for missing coverage
3. Focus on critical paths first

### Tests Are Slow

1. Use `--maxWorkers=2` for parallel execution
2. Mock heavy dependencies
3. Avoid unnecessary renders

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Next.js Testing](https://nextjs.org/docs/testing)

## Getting Help

If you encounter issues:

1. Check test output for error messages
2. Review component implementation
3. Check test examples in `components/design-system/__tests__/`
4. Consult `TESTING.md` for detailed testing documentation
