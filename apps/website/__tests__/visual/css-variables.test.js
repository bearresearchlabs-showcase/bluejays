/**
 * CSS Variables Visual Test
 * Tests CSS variables match deployed site values
 */

const fs = require('fs')
const path = require('path')

describe('CSS Variables Visual Regression', () => {
  let designSystemCSS = ''
  let globalsCSS = ''

  beforeAll(() => {
    const designSystemPath = path.join(__dirname, '../../app/design-system.css')
    const globalsPath = path.join(__dirname, '../../app/globals.css')
    
    if (fs.existsSync(designSystemPath)) {
      designSystemCSS = fs.readFileSync(designSystemPath, 'utf8')
    }
    if (fs.existsSync(globalsPath)) {
      globalsCSS = fs.readFileSync(globalsPath, 'utf8')
    }
  })

  const getCSSVariable = (varName) => {
    const combinedCSS = designSystemCSS + '\n' + globalsCSS
    const regex = new RegExp(`${varName}:\\s*([^;]+)`, 'i')
    const match = combinedCSS.match(regex)
    return match ? match[1].trim() : null
  }

  describe('Color Variables', () => {
    it('--text-primary should be #000000', () => {
      const value = getCSSVariable('--text-primary') || getCSSVariable('--color-text-primary')
      expect(value).toBe('#000000')
    })

    it('--text-secondary should be #6b7280', () => {
      const value = getCSSVariable('--text-secondary') || getCSSVariable('--color-text-secondary')
      expect(value).toBe('#6b7280')
    })

    it('--bg-primary should be #ffffff', () => {
      const value = getCSSVariable('--bg-primary') || getCSSVariable('--color-bg-primary')
      expect(value).toBe('#ffffff')
    })

    it('--bg-secondary should be #fafafa', () => {
      const value = getCSSVariable('--bg-secondary') || getCSSVariable('--color-bg-secondary')
      expect(value).toBe('#fafafa')
    })

    it('--border should be #e5e7eb', () => {
      const value = getCSSVariable('--border') || getCSSVariable('--color-border-primary')
      expect(value).toBe('#e5e7eb')
    })

    it('--accent should be #000000', () => {
      const value = getCSSVariable('--accent') || getCSSVariable('--color-accent-primary')
      expect(value).toBe('#000000')
    })

    it('--link-color should be #000000', () => {
      const value = getCSSVariable('--link-color')
      expect(value).toBe('#000000')
    })
  })

  describe('Spacing Variables', () => {
    it('--spacing-md should be 1rem', () => {
      const value = getCSSVariable('--spacing-md')
      expect(value).toBe('1rem')
    })

    it('--spacing-xl should be 2rem', () => {
      const value = getCSSVariable('--spacing-xl')
      expect(value).toBe('2rem')
    })
  })

  describe('Border Radius Variables', () => {
    it('--radius-md should be 0.375rem (6px)', () => {
      const value = getCSSVariable('--radius-md')
      expect(['0.375rem', '6px']).toContain(value)
    })
  })
})

describe('CSS File Content Checks', () => {
  let globalsCSS = ''

  beforeAll(() => {
    const globalsPath = path.join(__dirname, '../../app/globals.css')
    if (fs.existsSync(globalsPath)) {
      globalsCSS = fs.readFileSync(globalsPath, 'utf8')
    }
  })

  it('main-content padding should be 24px', () => {
    const paddingMatch = globalsCSS.match(/\.main-content\s*\{[^}]*padding:\s*([^;]+)/s)
    if (paddingMatch) {
      const padding = paddingMatch[1].trim()
      expect(padding).toBe('24px')
    }
  })

  it('card padding should be 20px', () => {
    const paddingMatch = globalsCSS.match(/\.card\s*\{[^}]*padding:\s*([^;]+)/s)
    if (paddingMatch) {
      const padding = paddingMatch[1].trim()
      expect(padding).toBe('20px')
    }
  })

  it('card border-radius should be 6px', () => {
    const radiusMatch = globalsCSS.match(/\.card\s*\{[^}]*border-radius:\s*([^;]+)/s)
    if (radiusMatch) {
      const radius = radiusMatch[1].trim()
      expect(radius).toBe('6px')
    }
  })

  it('paper component should have 20px padding', () => {
    const paddingMatch = globalsCSS.match(/\.paper\s*\{[^}]*padding:\s*([^;]+)/s)
    if (paddingMatch) {
      const padding = paddingMatch[1].trim()
      expect(padding).toBe('20px')
    }
  })

  it('paper component should have 6px border-radius', () => {
    const radiusMatch = globalsCSS.match(/\.paper\s*\{[^}]*border-radius:\s*([^;]+)/s)
    if (radiusMatch) {
      const radius = radiusMatch[1].trim()
      expect(radius).toBe('6px')
    }
  })
})
