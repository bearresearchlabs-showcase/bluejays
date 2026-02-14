import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Container } from '../layout/Container'

describe('Container Component', () => {
  it('renders container with children', () => {
    render(<Container>Container content</Container>)
    expect(screen.getByText('Container content')).toBeInTheDocument()
  })

  it('applies maxWidth constraint', () => {
    const { rerender } = render(<Container maxWidth="sm">Content</Container>)
    const container = screen.getByText('Content')
    expect(container).toHaveStyle({ maxWidth: '600px' })
    
    rerender(<Container maxWidth="lg">Content</Container>)
    expect(container).toHaveStyle({ maxWidth: '1200px' })
  })

  it('disables gutters when disableGutters is true', () => {
    render(<Container disableGutters>Content</Container>)
    const container = screen.getByText('Content')
    expect(container).toHaveStyle({ paddingLeft: '0', paddingRight: '0' })
  })

  it('applies gutters by default', () => {
    render(<Container>Content</Container>)
    const container = screen.getByText('Content')
    expect(container).toHaveStyle({ paddingLeft: 'var(--spacing-4)' })
  })
})
