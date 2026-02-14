/**
 * Visual Style Tests
 * Tests visual elements match the deployed Vercel app styling
 */

import React from 'react'
import { render } from '@testing-library/react'
import '@testing-library/jest-dom'

// Import components to test
import { Paper } from '@/components/design-system/layout/Paper'
import Typography from '@/components/design-system/data-display/Typography'
import Button from '@/components/design-system/Button'
import { Container } from '@/components/design-system/layout/Container'

describe('Visual Style Regression Tests', () => {
  describe('Paper Component Styling', () => {
    it('has correct padding (20px)', () => {
      const { container } = render(<Paper>Test</Paper>)
      const paper = container.querySelector('.paper') as HTMLElement
      expect(paper).toBeInTheDocument()
      
      // Check inline style (Paper component sets padding: '20px' inline)
      expect(paper.style.padding).toBe('20px')
    })

    it('has correct border-radius (6px)', () => {
      const { container } = render(<Paper>Test</Paper>)
      const paper = container.querySelector('.paper') as HTMLElement
      // Check inline style (Paper component sets borderRadius: '6px' inline)
      expect(paper.style.borderRadius).toBe('6px')
    })

    it('has white background', () => {
      const { container } = render(<Paper>Test</Paper>)
      const paper = container.querySelector('.paper') as HTMLElement
      // Check inline style (Paper component sets background: '#ffffff' inline)
      expect(paper.style.background).toBe('rgb(255, 255, 255)')
    })
  })

  describe('Typography Component Styling', () => {
    it('h1 has correct font size (32px)', () => {
      const { container } = render(<Typography variant="h1">Heading</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      const fontSize = parseFloat(styles.fontSize)
      expect(fontSize).toBeGreaterThanOrEqual(30)
      expect(fontSize).toBeLessThanOrEqual(34)
    })

    it('h1 has correct font weight (600)', () => {
      const { container } = render(<Typography variant="h1">Heading</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      const fontWeight = parseInt(styles.fontWeight)
      expect(fontWeight).toBeGreaterThanOrEqual(600)
    })

    it('h1 has correct line height', () => {
      const { container } = render(<Typography variant="h1">Heading</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      const lineHeight = parseFloat(styles.lineHeight)
      expect(lineHeight).toBeGreaterThanOrEqual(48)
      expect(lineHeight).toBeLessThanOrEqual(56)
    })

    it('h1 has correct letter spacing', () => {
      const { container } = render(<Typography variant="h1">Heading</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      const letterSpacing = parseFloat(styles.letterSpacing)
      expect(letterSpacing).toBeLessThanOrEqual(0)
      expect(letterSpacing).toBeGreaterThanOrEqual(-1)
    })

    it('h1 has black text color', () => {
      const { container } = render(<Typography variant="h1">Heading</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      expect(styles.color).toMatch(/rgb\(0,\s*0,\s*0\)|rgba\(0,\s*0,\s*0/)
    })

    it('h2 has correct font size (24px)', () => {
      const { container } = render(<Typography variant="h2">Subheading</Typography>)
      const h2 = container.querySelector('h2') as HTMLElement
      const styles = window.getComputedStyle(h2)
      const fontSize = parseFloat(styles.fontSize)
      expect(fontSize).toBeGreaterThanOrEqual(22)
      expect(fontSize).toBeLessThanOrEqual(26)
    })

    it('h2 has correct font weight (600)', () => {
      const { container } = render(<Typography variant="h2">Subheading</Typography>)
      const h2 = container.querySelector('h2') as HTMLElement
      const styles = window.getComputedStyle(h2)
      const fontWeight = parseInt(styles.fontWeight)
      expect(fontWeight).toBeGreaterThanOrEqual(600)
    })

    it('h2 has black text color', () => {
      const { container } = render(<Typography variant="h2">Subheading</Typography>)
      const h2 = container.querySelector('h2') as HTMLElement
      const styles = window.getComputedStyle(h2)
      expect(styles.color).toMatch(/rgb\(0,\s*0,\s*0\)|rgba\(0,\s*0,\s*0/)
    })
  })

  describe('Button Component Styling', () => {
    it('primary button has black background', () => {
      const { container } = render(<Button variant="primary">Click</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      expect(styles.backgroundColor).toBe('rgb(0, 0, 0)')
    })

    it('primary button has white text', () => {
      const { container } = render(<Button variant="primary">Click</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      expect(styles.color).toBe('rgb(255, 255, 255)')
    })

    it('button has correct border-radius', () => {
      const { container } = render(<Button>Click</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      // Should use CSS variable or 6px
      expect(['6px', '0.375rem']).toContain(styles.borderRadius)
    })
  })

  describe('CSS Variables', () => {
    it('has correct text-primary color (#000000)', () => {
      const root = document.documentElement
      const textPrimary = getComputedStyle(root).getPropertyValue('--color-text-primary') || 
                         getComputedStyle(root).getPropertyValue('--text-primary')
      expect(textPrimary.trim()).toBe('#000000')
    })

    it('has correct text-secondary color (#6b7280)', () => {
      const root = document.documentElement
      const textSecondary = getComputedStyle(root).getPropertyValue('--color-text-secondary') || 
                           getComputedStyle(root).getPropertyValue('--text-secondary')
      expect(textSecondary.trim()).toBe('#6b7280')
    })

    it('has correct bg-primary color (#ffffff)', () => {
      const root = document.documentElement
      const bgPrimary = getComputedStyle(root).getPropertyValue('--color-bg-primary') || 
                       getComputedStyle(root).getPropertyValue('--bg-primary')
      expect(bgPrimary.trim()).toBe('#ffffff')
    })

    it('has correct bg-secondary color (#fafafa)', () => {
      const root = document.documentElement
      const bgSecondary = getComputedStyle(root).getPropertyValue('--color-bg-secondary') || 
                         getComputedStyle(root).getPropertyValue('--bg-secondary')
      expect(bgSecondary.trim()).toBe('#fafafa')
    })

    it('has correct border color (#e5e7eb)', () => {
      const root = document.documentElement
      const border = getComputedStyle(root).getPropertyValue('--color-border-primary') || 
                    getComputedStyle(root).getPropertyValue('--border')
      expect(border.trim()).toBe('#e5e7eb')
    })

    it('has correct accent color (#000000)', () => {
      const root = document.documentElement
      const accent = getComputedStyle(root).getPropertyValue('--color-accent-primary') || 
                    getComputedStyle(root).getPropertyValue('--accent')
      expect(accent.trim()).toBe('#000000')
    })
  })

  describe('Body Typography', () => {
    it('has correct font size (16px)', () => {
      const body = document.body
      const styles = window.getComputedStyle(body)
      // In jsdom, font-size might be computed differently, check if it's close
      const fontSize = parseFloat(styles.fontSize)
      expect(fontSize).toBeGreaterThanOrEqual(15)
      expect(fontSize).toBeLessThanOrEqual(17)
    })

    it('has correct line height', () => {
      const body = document.body
      const styles = window.getComputedStyle(body)
      // Line height should be around 1.65 * font-size
      const lineHeight = parseFloat(styles.lineHeight)
      expect(lineHeight).toBeGreaterThanOrEqual(24)
      expect(lineHeight).toBeLessThanOrEqual(28)
    })

    it('has correct letter spacing', () => {
      const body = document.body
      const styles = window.getComputedStyle(body)
      const letterSpacing = parseFloat(styles.letterSpacing)
      expect(letterSpacing).toBeLessThanOrEqual(0)
      expect(letterSpacing).toBeGreaterThanOrEqual(-0.2)
    })

    it('has black text color', () => {
      const body = document.body
      const styles = window.getComputedStyle(body)
      // Check if color is black or very dark
      expect(styles.color).toMatch(/rgb\(0,\s*0,\s*0\)|rgba\(0,\s*0,\s*0/)
    })
  })
})
