---
name: debug-test-failures
description: Debug failing Jest, integration, or Playwright E2E tests. Use when the user reports a test failure or asks to debug a failing test.
---

# Debug Test Failures

## Trigger

- User reports a test failure
- User asks to debug a failing test
- CI or local run shows test errors

## Steps

### 1. Run the failing test with verbose output

```bash
# Jest (unit/integration)
npm test -- --verbose --no-cache path/to/test-file

# Playwright E2E
npm run test:e2e -- path/to/spec.ts --project=chromium
```

### 2. Parse the error

Identify error type:

- **AssertionError**: Wrong expected value, selector, or assertion
- **Timeout**: Element not found, slow load, or wrong selector
- **404 / 401**: Wrong URL, auth missing, or app not running
- **ECONNREFUSED**: App not running (integration/E2E)

### 3. E2E-specific debugging

- Run headed: `npm run test:e2e:headed -- path/to/spec.ts`
- Or UI mode: `npm run test:e2e:ui`
- Use **cursor-ide-browser MCP**: `browser_navigate`, `browser_snapshot`, `browser_click` to reproduce and inspect DOM/network
- Playwright trace: `npx playwright show-trace trace.zip` (after run with `trace: 'on-first-retry'`)

### 4. Integration-specific debugging

- Verify app is running: `npm run dev:test` (port 3007)
- Check `BASE_URL` env: default `http://localhost:3007`
- Add `console.log` or increase timeout in the test
- Confirm auth: credentials `staff`/`annotator`/`customer` = `123123` (see `lib/auth.ts`)

### 5. Propose fix

- **Assertion**: Adjust expected value or selector
- **Selector**: Use more stable locators (role, label, test-id)
- **Mock**: Fix or add mock for API/auth
- **Code**: Fix the implementation if the test is correct

### 6. Re-run to verify

```bash
npm test -- path/to/test-file
# or
npm run test:e2e -- path/to/spec.ts
```

## Quick reference

| Test type | Command | App required |
|-----------|---------|--------------|
| Jest unit | `npm test` | No |
| Integration | `npm run test:integration` | Yes (port 3007) |
| E2E | `npm run test:e2e` | Auto-started |
| Full app | `npm run test:app` | Auto-started |
