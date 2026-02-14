import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Alert } from '../feedback/Alert'

describe('Alert Component', () => {
  it('renders alert with children', () => {
    render(<Alert>Alert message</Alert>)
    expect(screen.getByText('Alert message')).toBeInTheDocument()
  })

  it('renders with success severity', () => {
    render(<Alert severity="success">Success</Alert>)
    const alert = screen.getByRole('alert')
    expect(alert).toHaveClass('alert-success')
  })

  it('renders with error severity', () => {
    render(<Alert severity="error">Error</Alert>)
    const alert = screen.getByRole('alert')
    expect(alert).toHaveClass('alert-error')
  })

  it('renders with warning severity', () => {
    render(<Alert severity="warning">Warning</Alert>)
    const alert = screen.getByRole('alert')
    expect(alert).toHaveClass('alert-warning')
  })

  it('renders with info severity', () => {
    render(<Alert severity="info">Info</Alert>)
    const alert = screen.getByRole('alert')
    expect(alert).toHaveClass('alert-info')
  })

  it('calls onClose when close button is clicked', () => {
    const handleClose = jest.fn()
    render(<Alert onClose={handleClose}>Dismissible</Alert>)
    
    const closeButton = screen.getByLabelText('Close alert')
    fireEvent.click(closeButton)
    
    expect(handleClose).toHaveBeenCalledTimes(1)
  })

  it('renders with custom icon', () => {
    render(<Alert icon={<span data-testid="custom-icon">!</span>}>Custom icon</Alert>)
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
  })

  it('renders with action button', () => {
    render(
      <Alert action={<button>Action</button>}>With action</Alert>
    )
    expect(screen.getByText('Action')).toBeInTheDocument()
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Alert variant="standard">Standard</Alert>)
    expect(screen.getByRole('alert')).toHaveClass('alert-standard')
    
    rerender(<Alert variant="filled">Filled</Alert>)
    expect(screen.getByRole('alert')).toHaveClass('alert-filled')
    
    rerender(<Alert variant="outlined">Outlined</Alert>)
    expect(screen.getByRole('alert')).toHaveClass('alert-outlined')
  })
})
