'use client'

import React from 'react'
import { useFormControl } from './FormControl'
import { clsx } from '../utils'

/**
 * FormHelperText Component
 * Helper text for form controls
 */

export interface FormHelperTextProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  error?: boolean
}

export function FormHelperText({ children, error, className, ...props }: FormHelperTextProps) {
  const formControl = useFormControl()
  const hasError = error !== undefined ? error : formControl.error

  return (
    <div
      style={{
        marginTop: 'var(--spacing-1)',
        fontSize: 'var(--font-size-xs)',
        color: hasError ? 'var(--color-error-main)' : 'var(--color-text-secondary)',
      }}
      className={clsx('form-helper-text', className)}
      {...props}
    >
      {children}
    </div>
  )
}
