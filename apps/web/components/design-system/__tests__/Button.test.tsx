import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import Button from '../Button'

describe('Button Component', () => {
  it('renders button with children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByText('Click me')
    fireEvent.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick} disabled>Click me</Button>)
    
    const button = screen.getByText('Click me')
    fireEvent.click(button)
    
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('renders with primary variant by default', () => {
    render(<Button>Primary</Button>)
    const button = screen.getByText('Primary').closest('button')!
    expect(button.className).toContain('button')
    expect(button.className).toContain('button-primary')
  })

  it('renders with secondary variant', () => {
    render(<Button variant="secondary">Secondary</Button>)
    const button = screen.getByText('Secondary').closest('button')!
    expect(button.className).toContain('button')
    expect(button.className).toContain('button-secondary')
  })

  it('renders with ghost variant', () => {
    render(<Button variant="ghost">Ghost</Button>)
    const button = screen.getByText('Ghost').closest('button')!
    expect(button.className).toContain('button')
    expect(button.className).toContain('button-ghost')
  })

  it('renders with fab variant', () => {
    render(<Button variant="fab">+</Button>)
    const button = screen.getByText('+').closest('button')!
    expect(button.className).toContain('button')
    expect(button.className).toContain('button-fab')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    const smallButton = screen.getByText('Small').closest('button')!
    // Check className contains button-sm
    expect(smallButton.className).toContain('button-sm')
    
    rerender(<Button size="md">Medium</Button>)
    const mediumButton = screen.getByText('Medium').closest('button')!
    expect(mediumButton.className).toContain('button-md')
    
    rerender(<Button size="lg">Large</Button>)
    const largeButton = screen.getByText('Large').closest('button')!
    expect(largeButton.className).toContain('button-lg')
  })

  it('renders with loading state', () => {
    render(<Button loading>Loading</Button>)
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    // Button should be disabled when loading
    expect(button).toHaveAttribute('disabled')
  })

  it('renders with startIcon', () => {
    render(<Button startIcon={<span data-testid="start-icon">+</span>}>Add</Button>)
    expect(screen.getByTestId('start-icon')).toBeInTheDocument()
  })

  it('renders with endIcon', () => {
    render(<Button endIcon={<span data-testid="end-icon">→</span>}>Next</Button>)
    expect(screen.getByTestId('end-icon')).toBeInTheDocument()
  })

  it('applies fullWidth style', () => {
    render(<Button fullWidth>Full Width</Button>)
    const button = screen.getByText('Full Width').closest('button') as HTMLButtonElement
    // Check inline style - Button sets width: '100%' when fullWidth is true
    expect(button.style.width).toBe('100%')
  })

  it('renders with correct type attribute', () => {
    const { rerender } = render(<Button type="submit">Submit</Button>)
    const submitButton = screen.getByText('Submit').closest('button') as HTMLButtonElement
    // Button type should be submit
    expect(submitButton.type).toBe('submit')
    
    rerender(<Button type="reset">Reset</Button>)
    const resetButton = screen.getByText('Reset').closest('button') as HTMLButtonElement
    expect(resetButton.type).toBe('reset')
  })
})
