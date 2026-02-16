# Database Documentation Portal

A Next.js website for displaying database documentation and deliverables.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Testing

This project uses **Jest** and **React Testing Library** for testing. All components must include tests.

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run pre-commit checks
npm run pre-commit
```

### Test Coverage

- **Minimum**: 60% coverage required
- **Components**: 70% coverage required
- **Current**: All tests passing ✅

See [TESTING.md](./TESTING.md) for detailed testing documentation.

## Development Workflow

### Before Committing

1. Run pre-commit checks:
   ```bash
   npm run pre-commit
   ```

2. Or manually:
   ```bash
   npm run validate
   ```

### Creating Components

1. Create component file
2. Create test file in `__tests__/`
3. Write tests first (TDD)
4. Implement component
5. Run tests: `npm test`

See [DEVELOPMENT.md](./DEVELOPMENT.md) for complete development guide.

## Project Structure

```
apps/web/
├── app/                    # Next.js app directory
├── components/             # React components
│   └── design-system/      # Design system components
│       └── __tests__/      # Component tests
├── lib/                    # Utility libraries
├── scripts/                # Build and utility scripts
├── .github/                # GitHub workflows
│   └── workflows/          # CI/CD workflows
└── coverage/               # Test coverage reports
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run test:watch` - Watch mode for tests
- `npm run test:coverage` - Generate coverage report
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types
- `npm run validate` - Run all checks (type-check + lint + test)
- `npm run pre-commit` - Run pre-commit validation

## CI/CD

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Scheduled daily runs

See `.github/workflows/` for workflow definitions.

## Documentation

- [TESTING.md](./TESTING.md) - Testing guide
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development workflow
- [TESTING_WORKFLOW.md](./TESTING_WORKFLOW.md) - Testing workflow
- [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) - Design system documentation

## Contributing

1. Create feature branch
2. Write tests for new features
3. Implement feature
4. Ensure tests pass and coverage meets threshold
5. Submit pull request

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed contribution guidelines.

## License

Private project - All rights reserved
