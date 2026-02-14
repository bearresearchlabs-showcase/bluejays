import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Stack } from '../layout/Stack'

describe('Stack Component', () => {
  it('renders stack with children', () => {
    render(
      <Stack>
        <div>Item 1</div>
        <div>Item 2</div>
      </Stack>
    )
    
    expect(screen.getByText('Item 1')).toBeInTheDocument()
    expect(screen.getByText('Item 2')).toBeInTheDocument()
  })

  it('renders with row direction', () => {
    render(<Stack direction="row"><div>Item</div></Stack>)
    const stack = screen.getByText('Item').parentElement
    expect(stack).toHaveStyle({ flexDirection: 'row' })
  })

  it('renders with column direction by default', () => {
    render(<Stack><div>Item</div></Stack>)
    const stack = screen.getByText('Item').parentElement
    expect(stack).toHaveStyle({ flexDirection: 'column' })
  })

  it('applies spacing', () => {
    render(<Stack spacing={4}><div>Item</div></Stack>)
    const stack = screen.getByText('Item').parentElement
    expect(stack).toHaveStyle({ gap: 'var(--spacing-4)' })
  })

  it('applies justifyContent', () => {
    render(<Stack justifyContent="center"><div>Item</div></Stack>)
    const stack = screen.getByText('Item').parentElement
    expect(stack).toHaveStyle({ justifyContent: 'center' })
  })

  it('applies alignItems', () => {
    render(<Stack alignItems="center"><div>Item</div></Stack>)
    const stack = screen.getByText('Item').parentElement
    expect(stack).toHaveStyle({ alignItems: 'center' })
  })
})
