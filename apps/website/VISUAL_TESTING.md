# Visual Testing Framework

This document describes the visual testing framework used to verify that visual elements match the deployed Vercel app.

## Overview

The visual testing framework consists of multiple test suites:

1. **CSS Variable Tests** (`css-variables.test.js`) - ✅ Passing
   - Tests CSS variables directly from CSS files
   - Verifies color, spacing, and border-radius variables match deployed site

2. **CSS File Checks** (`test-visual-styles.js`) - ✅ Passing
   - Node.js script that checks CSS file content
   - Verifies padding, border-radius, and other properties in CSS files

3. **Component Visual Tests** (`visual-styles.test.tsx`, `component-visual.test.tsx`) - ⚠️ Partial
   - React component tests using Jest + jsdom
   - Limited by jsdom's CSS computed style support

## Running Tests

```bash
# Run all visual tests
npm run test:visual

# Run CSS variable checks only (recommended)
npm run test:visual:styles
```

## Test Results

### ✅ CSS Variable Tests (Passing)
All CSS variables match the deployed site:
- `--text-primary`: `#000000` ✅
- `--text-secondary`: `#6b7280` ✅
- `--bg-primary`: `#ffffff` ✅
- `--bg-secondary`: `#fafafa` ✅
- `--border`: `#e5e7eb` ✅
- `--accent`: `#000000` ✅

### ✅ CSS File Content Checks (Passing)
CSS file properties verified:
- Main content padding: `24px` ✅
- Card padding: `20px` ✅
- Card border-radius: `6px` ✅
- Paper component padding: `20px` ✅
- Paper component border-radius: `6px` ✅

### ⚠️ Component Visual Tests (Partial)
React component tests have limitations due to jsdom:
- Paper component inline styles: ✅ Verified (padding, border-radius, background)
- Typography computed styles: ⚠️ Limited by jsdom
- Button computed styles: ⚠️ Limited by jsdom

## Expected Visual Values

All tests compare against: https://db-documentation-f51u.vercel.app/

### Spacing
- Main content padding: `24px`
- Card padding: `20px`
- Sidebar padding: `32px 0px`

### Border Radius
- Cards: `6px`
- Paper components: `6px`

### Typography
- H1: `32px`, `600`, `52.8px` line-height, `-0.64px` letter-spacing
- H2: `24px`, `600`
- Body: `16px`, `26.4px` line-height, `-0.16px` letter-spacing

### Colors
- Text primary: `#000000` (black)
- Text secondary: `#6b7280` (gray-500)
- Background primary: `#ffffff` (white)
- Background secondary: `#fafafa` (gray-50)
- Border: `#e5e7eb` (gray-200)
- Accent: `#000000` (black)

## Test Files

- `__tests__/visual/css-variables.test.js` - CSS variable tests
- `__tests__/visual/visual-styles.test.tsx` - Component style tests
- `__tests__/visual/component-visual.test.tsx` - Component appearance tests
- `scripts/test-visual-styles.js` - CSS file content checker

## Recommendations

1. **Use `npm run test:visual:styles`** for reliable CSS variable checks
2. **CSS variable tests** are the most reliable and should be run regularly
3. **Component tests** are useful for verifying component structure but have limitations with computed styles in jsdom
4. For full visual regression testing, consider using Playwright or similar tools for browser-based testing

## CI/CD Integration

The visual tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Visual Tests
  run: |
    npm run test:visual:styles
    npm run test:visual
```

## Future Improvements

1. Add Playwright for full browser-based visual regression testing
2. Add screenshot comparison tests
3. Add visual diff testing against deployed site
4. Improve component tests with better jsdom configuration
