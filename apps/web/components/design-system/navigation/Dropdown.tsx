'use client'

import React, { useState, useRef } from 'react'
import { Menu, MenuItem, MenuProps } from './Menu'
import { clsx } from '../utils'

/**
 * Dropdown Component
 * Button with dropdown menu
 */

export interface DropdownOption {
  label: string
  value: string | number
  disabled?: boolean
  divider?: boolean
  icon?: React.ReactNode
}

export interface DropdownProps {
  options: DropdownOption[]
  onSelect?: (value: string | number) => void
  trigger?: React.ReactNode
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end'
  className?: string
}

export function Dropdown({
  options,
  onSelect,
  trigger,
  placement = 'bottom-start',
  className,
}: DropdownProps) {
  const [open, setOpen] = useState(false)
  const anchorRef = useRef<HTMLDivElement>(null)

  const anchorOrigin = {
    vertical: placement.startsWith('top') ? ('top' as const) : ('bottom' as const),
    horizontal: placement.endsWith('end') ? ('right' as const) : ('left' as const),
  }

  const transformOrigin = {
    vertical: placement.startsWith('top') ? ('bottom' as const) : ('top' as const),
    horizontal: placement.endsWith('end') ? ('right' as const) : ('left' as const),
  }

  return (
    <div ref={anchorRef} style={{ position: 'relative', display: 'inline-block' }} className={clsx('dropdown', className)}>
      <div onClick={() => setOpen(!open)}>{trigger}</div>
      <Menu
        anchorEl={anchorRef.current}
        open={open}
        onClose={() => setOpen(false)}
        anchorOrigin={anchorOrigin}
        transformOrigin={transformOrigin}
      >
        {options.map((option, index) => (
          <MenuItem
            key={option.value}
            onClick={() => {
              onSelect?.(option.value)
              setOpen(false)
            }}
            disabled={option.disabled}
            divider={option.divider}
            icon={option.icon}
          >
            {option.label}
          </MenuItem>
        ))}
      </Menu>
    </div>
  )
}
