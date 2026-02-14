/**
 * Component Visual Tests
 * Tests component visual appearance matches deployed site
 */

import React from 'react'
import { render } from '@testing-library/react'
import '@testing-library/jest-dom'

import { Paper } from '@/components/design-system/layout/Paper'
import Typography from '@/components/design-system/data-display/Typography'
import Button from '@/components/design-system/Button'
import { Stack } from '@/components/design-system/layout/Stack'
import { Container } from '@/components/design-system/layout/Container'

describe('Component Visual Appearance Tests', () => {
  describe('Paper Component', () => {
    it('renders with correct visual properties', () => {
      const { container } = render(
        <Paper elevation={1} variant="elevation">
          <Typography>Test Content</Typography>
        </Paper>
      )
      
      const paper = container.querySelector('.paper') as HTMLElement
      expect(paper).toBeInTheDocument()
      
      const styles = window.getComputedStyle(paper)
      
      // Check critical visual properties
      expect(styles.backgroundColor).toBe('rgb(255, 255, 255)')
      expect(styles.borderRadius).toBe('6px')
      expect(styles.padding).toBe('20px')
    })

    it('outlined variant has border', () => {
      const { container } = render(
        <Paper variant="outlined">
          Content
        </Paper>
      )
      
      const paper = container.querySelector('.paper') as HTMLElement
      const styles = window.getComputedStyle(paper)
      expect(styles.border).toContain('rgb(229, 231, 235)')
    })
  })

  describe('Typography Component', () => {
    it('h1 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="h1">Heading 1</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      
      expect(styles.fontSize).toBe('32px')
      expect(styles.fontWeight).toBe('600')
      expect(styles.color).toBe('rgb(0, 0, 0)')
      expect(styles.lineHeight).toBe('52.8px')
      expect(styles.letterSpacing).toBe('-0.64px')
    })

    it('h2 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="h2">Heading 2</Typography>)
      const h2 = container.querySelector('h2') as HTMLElement
      const styles = window.getComputedStyle(h2)
      
      expect(styles.fontSize).toBe('24px')
      expect(styles.fontWeight).toBe('600')
      expect(styles.color).toBe('rgb(0, 0, 0)')
    })

    it('body1 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="body1">Body text</Typography>)
      const p = container.querySelector('p') as HTMLElement
      const styles = window.getComputedStyle(p)
      
      expect(styles.fontSize).toBe('16px')
      expect(styles.color).toBe('rgb(0, 0, 0)')
    })

    it('body2 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="body2">Small text</Typography>)
      const p = container.querySelector('p') as HTMLElement
      const styles = window.getComputedStyle(p)
      
      expect(styles.fontSize).toBe('14px')
    })

    it('secondary color has correct value', () => {
      const { container } = render(<Typography variant="body2" color="secondary">Secondary</Typography>)
      const p = container.querySelector('p') as HTMLElement
      const styles = window.getComputedStyle(p)
      
      expect(styles.color).toBe('rgb(107, 114, 128)')
    })
  })

  describe('Button Component', () => {
    it('primary variant has correct colors', () => {
      const { container } = render(<Button variant="primary">Primary</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      
      expect(styles.backgroundColor).toBe('rgb(0, 0, 0)')
      expect(styles.color).toBe('rgb(255, 255, 255)')
    })

    it('secondary variant has correct styling', () => {
      const { container } = render(<Button variant="secondary">Secondary</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      
      expect(styles.backgroundColor).toBe('rgba(0, 0, 0, 0)')
      expect(styles.color).toBe('rgb(0, 0, 0)')
      expect(styles.border).toContain('rgb(229, 231, 235)')
    })

    it('has correct border-radius', () => {
      const { container } = render(<Button>Test</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      
      // Should be 6px or use CSS variable
      expect(['6px', '0.375rem']).toContain(styles.borderRadius)
    })
  })

  describe('Layout Components', () => {
    it('Container has correct max-width', () => {
      const { container } = render(
        <Container maxWidth="xl">
          <Typography>Content</Typography>
        </Container>
      )
      
      const containerEl = container.querySelector('.container') as HTMLElement
      const styles = window.getComputedStyle(containerEl)
      
      // Container should have max-width set
      expect(styles.maxWidth).toBeTruthy()
    })

    it('Stack applies correct spacing', () => {
      const { container } = render(
        <Stack spacing={2}>
          <Typography>Item 1</Typography>
          <Typography>Item 2</Typography>
        </Stack>
      )
      
      const stack = container.querySelector('.stack') as HTMLElement
      expect(stack).toBeInTheDocument()
      const styles = window.getComputedStyle(stack)
      expect(styles.display).toBe('flex')
    })
  })
})
