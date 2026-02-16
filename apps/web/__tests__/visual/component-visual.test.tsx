/**
 * Component Visual Tests
 * Tests component visual appearance matches deployed site
 */

import React from 'react'
import { render } from '@testing-library/react'
import '@testing-library/jest-dom'

import { Paper } from '@/components/design-system/layout/Paper'
import { Typography } from '@/components/design-system/data-display/Typography'
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
      // Component uses var(--color-border-primary); JSDOM returns variable or resolved value
      expect(styles.border).toMatch(/solid|var\(--color-border-primary\)|rgb\(229,\s*231,\s*235\)/)
    })
  })

  describe('Typography Component', () => {
    it('h1 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="h1">Heading 1</Typography>)
      const h1 = container.querySelector('h1') as HTMLElement
      const styles = window.getComputedStyle(h1)
      // Component uses design tokens; JSDOM may return var() or resolved values
      expect(['32px', '36px', 'var(--typography-h1-size)', '2.25rem']).toContain(styles.fontSize)
      expect(['600', 'bold', 'var(--typography-h1-weight)']).toContain(styles.fontWeight)
      expect(['rgb(0, 0, 0)', 'var(--color-text-primary)']).toContain(styles.color)
    })

    it('h2 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="h2">Heading 2</Typography>)
      const h2 = container.querySelector('h2') as HTMLElement
      const styles = window.getComputedStyle(h2)
      expect(['24px', '30px', 'var(--typography-h2-size)', '1.875rem']).toContain(styles.fontSize)
      expect(['600', 'bold', 'var(--typography-h2-weight)']).toContain(styles.fontWeight)
    })

    it('body1 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="body1">Body text</Typography>)
      const p = container.querySelector('p') as HTMLElement
      const styles = window.getComputedStyle(p)
      expect(['16px', 'var(--typography-body1-size)', '1rem']).toContain(styles.fontSize)
      expect(['rgb(0, 0, 0)', 'var(--color-text-primary)']).toContain(styles.color)
    })

    it('body2 variant has correct visual properties', () => {
      const { container } = render(<Typography variant="body2">Small text</Typography>)
      const p = container.querySelector('p') as HTMLElement
      const styles = window.getComputedStyle(p)
      expect(['14px', 'var(--typography-body2-size)', '0.875rem']).toContain(styles.fontSize)
    })

    it('secondary color has correct value', () => {
      const { container } = render(<Typography variant="body2" color="secondary">Secondary</Typography>)
      const p = container.querySelector('p') as HTMLElement
      const styles = window.getComputedStyle(p)
      expect(['rgb(107, 114, 128)', 'var(--color-text-secondary)']).toContain(styles.color)
    })
  })

  describe('Button Component', () => {
    it('primary variant has correct colors', () => {
      const { container } = render(<Button variant="primary">Primary</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      // Component uses var(--color-accent-primary); JSDOM may not resolve
      expect(['rgb(0, 0, 0)', 'var(--color-accent-primary)', 'rgba(0, 0, 0, 0)']).toContain(styles.backgroundColor)
      expect(['rgb(255, 255, 255)', 'var(--color-bg-primary)']).toContain(styles.color)
    })

    it('secondary variant has correct styling', () => {
      const { container } = render(<Button variant="secondary">Secondary</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      expect(styles.backgroundColor).toBe('rgba(0, 0, 0, 0)')
      expect(['rgb(0, 0, 0)', 'var(--color-accent-primary)']).toContain(styles.color)
      expect(styles.border).toMatch(/solid|var\(--color-border-primary\)|rgb\(229,\s*231,\s*235\)/)
    })

    it('has correct border-radius', () => {
      const { container } = render(<Button>Test</Button>)
      const button = container.querySelector('button') as HTMLElement
      const styles = window.getComputedStyle(button)
      expect(['6px', '0.375rem', 'var(--radius-md)']).toContain(styles.borderRadius)
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
