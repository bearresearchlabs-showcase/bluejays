'use client'

import React from 'react'
import { useFormControl } from './FormControl'
import { clsx } from '../utils'

/**
 * FormLabel Component
 * Label for form controls
 */

export interface FormLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  children: React.ReactNode
  required?: boolean
  error?: boolean
}

export function FormLabel({ children, required, error, className, ...props }: FormLabelProps) {
  const formControl = useFormControl()
  const isRequired = required !== undefined ? required : formControl.required
  const hasError = error !== undefined ? error : formControl.error

  return (
    <label
      style={{
        display: 'block',
        marginBottom: 'var(--spacing-2)',
        fontSize: 'var(--font-size-sm)',
        fontWeight: 'var(--font-weight-medium)',
        color: hasError ? 'var(--color-error-main)' : 'var(--color-text-primary)',
      }}
      className={clsx('form-label', className)}
      {...props}
    >
      {children}
      {isRequired && (
        <span style={{ color: 'var(--color-error-main)', marginLeft: 'var(--spacing-1)' }}>*</span>
      )}
    </label>
  )
}
