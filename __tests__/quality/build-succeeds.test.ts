/**
 * Verifies that the Next.js production build completes successfully.
 * Run: npm run test:build (or npm run test with TEST_BUILD=1)
 * Skip in normal test runs to keep test suite fast.
 */
import { execSync } from 'child_process'
import path from 'path'

const RUN_BUILD = process.env.TEST_BUILD === '1'

describe('Quality: Build', () => {
  const itBuild = RUN_BUILD ? it : it.skip
  itBuild(
    'next build --webpack completes without errors',
    () => {
      const root = path.join(__dirname, '../..')
      execSync('node scripts/generate-sources-manifest.js && npx next build --webpack', {
        cwd: root,
        encoding: 'utf-8',
        stdio: 'pipe',
      })
    },
    120000
  )
})
