import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Chip } from '../data-display/Chip'

describe('Chip Component', () => {
  it('renders chip with label', () => {
    render(<Chip label="Chip Label" />)
    expect(screen.getByText('Chip Label')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Chip label="Clickable" onClick={handleClick} />)
    
    const chip = screen.getByText('Clickable')
    fireEvent.click(chip)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('calls onDelete when delete button is clicked', () => {
    const handleDelete = jest.fn()
    render(<Chip label="Deletable" onDelete={handleDelete} />)
    
    const deleteButton = screen.getByLabelText('Delete chip')
    fireEvent.click(deleteButton)
    
    expect(handleDelete).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when delete button is clicked', () => {
    const handleClick = jest.fn()
    const handleDelete = jest.fn()
    render(<Chip label="Test" onClick={handleClick} onDelete={handleDelete} />)
    
    const deleteButton = screen.getByLabelText('Delete chip')
    fireEvent.click(deleteButton)
    
    expect(handleDelete).toHaveBeenCalledTimes(1)
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Chip label="Default" variant="default" />)
    // Chip wraps label in a span, so we need to get the parent span
    const labelSpan = screen.getByText('Default')
    const chip = labelSpan.parentElement!
    expect(chip.className).toContain('chip')
    expect(chip.className).toContain('chip-default')
    
    rerender(<Chip label="Outlined" variant="outlined" />)
    const outlinedLabelSpan = screen.getByText('Outlined')
    const outlinedChip = outlinedLabelSpan.parentElement!
    expect(outlinedChip.className).toContain('chip')
    expect(outlinedChip.className).toContain('chip-outlined')
    
    rerender(<Chip label="Filled" variant="filled" />)
    const filledLabelSpan = screen.getByText('Filled')
    const filledChip = filledLabelSpan.parentElement!
    expect(filledChip.className).toContain('chip')
    expect(filledChip.className).toContain('chip-filled')
  })

  it('renders with different colors', () => {
    const { rerender } = render(<Chip label="Primary" color="primary" />)
    const labelSpan = screen.getByText('Primary')
    const chip = labelSpan.parentElement!
    expect(chip.className).toContain('chip')
    expect(chip.className).toContain('chip-primary')
    
    rerender(<Chip label="Success" color="success" />)
    const successLabelSpan = screen.getByText('Success')
    const successChip = successLabelSpan.parentElement!
    expect(successChip.className).toContain('chip')
    expect(successChip.className).toContain('chip-success')
  })

  it('renders with avatar', () => {
    render(<Chip label="Avatar Chip" avatar={<span data-testid="avatar">A</span>} />)
    expect(screen.getByTestId('avatar')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(<Chip label="Icon Chip" icon={<span data-testid="icon">★</span>} />)
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Chip label="Small" size="sm" />)
    const chip = screen.getByText('Small')
    expect(chip).toBeInTheDocument()
    
    rerender(<Chip label="Medium" size="md" />)
    expect(screen.getByText('Medium')).toBeInTheDocument()
  })
})
