# Visual Regression Tests

This directory contains visual regression tests to ensure the website's visual elements match the deployed Vercel app.

## Test Files

- `css-variables.test.js` - Tests CSS variables match deployed site values
- `visual-styles.test.tsx` - Tests component visual styling (React components)
- `component-visual.test.tsx` - Tests component visual appearance

## Running Tests

```bash
# Run all visual tests
npm run test:visual

# Run CSS variable checks only
npm run test:visual:styles
```

## Test Coverage

### CSS Variables
- Color variables (text-primary, text-secondary, bg-primary, bg-secondary, border, accent)
- Spacing variables
- Border radius variables

### Component Styling
- Paper component padding (20px)
- Paper component border-radius (6px)
- Typography font sizes and weights
- Button colors
- Layout component properties

### Visual Properties Verified
- Padding: Main content (24px), Cards (20px)
- Border radius: Cards (6px)
- Colors: All CSS color variables
- Typography: Font sizes, weights, line heights, letter spacing

## Expected Values

All tests compare against the deployed site: https://db-documentation-f51u.vercel.app/

### Key Values
- Main content padding: `24px`
- Card padding: `20px`
- Card border-radius: `6px`
- Text primary: `#000000`
- Text secondary: `#6b7280`
- Background primary: `#ffffff`
- Background secondary: `#fafafa`
- Border: `#e5e7eb`
- Accent: `#000000`
