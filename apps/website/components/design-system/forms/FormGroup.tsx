'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * FormGroup Component
 * Group of form controls
 */

export interface FormGroupProps {
  children: React.ReactNode
  row?: boolean
  className?: string
}

export function FormGroup({ children, row = false, className }: FormGroupProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: row ? 'row' : 'column',
        gap: 'var(--spacing-4)',
      }}
      className={clsx('form-group', className)}
    >
      {children}
    </div>
  )
}
