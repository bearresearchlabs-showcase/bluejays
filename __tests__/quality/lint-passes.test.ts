/**
 * Verifies that ESLint passes with zero errors and zero warnings.
 * Run: npm run test
 */
import { execSync } from 'child_process'
import path from 'path'

describe('Quality: Lint', () => {
  it('eslint passes with --max-warnings 0', () => {
    const root = path.join(__dirname, '../..')
    const result = execSync('npx eslint . --max-warnings 0', {
      cwd: root,
      encoding: 'utf-8',
    })
    expect(result).toBeDefined()
    expect(typeof result).toBe('string')
  })
})
