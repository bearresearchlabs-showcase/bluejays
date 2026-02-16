/**
 * Verifies that TypeScript compiles without errors.
 * Run: npm run test
 */
import { execSync } from 'child_process'
import path from 'path'

describe('Quality: TypeScript', () => {
  it('tsc --noEmit passes with no errors', () => {
    const root = path.join(__dirname, '../..')
    execSync('npx tsc --noEmit', {
      cwd: root,
      encoding: 'utf-8',
    })
  })
})
