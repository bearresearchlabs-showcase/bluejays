'use client'

import React, { forwardRef } from 'react'
import { clsx } from '../utils'

/**
 * Input Component
 * Base input component with variants and states
 */

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'outlined' | 'filled' | 'standard'
  size?: 'sm' | 'md' | 'lg'
  error?: boolean
  helperText?: string
  startAdornment?: React.ReactNode
  endAdornment?: React.ReactNode
  fullWidth?: boolean
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'outlined',
      size = 'md',
      error = false,
      helperText,
      startAdornment,
      endAdornment,
      fullWidth = false,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const sizeStyles = {
      sm: {
        padding: 'var(--spacing-2) var(--spacing-3)',
        fontSize: 'var(--font-size-sm)',
      },
      md: {
        padding: 'var(--spacing-3) var(--spacing-4)',
        fontSize: 'var(--font-size-base)',
      },
      lg: {
        padding: 'var(--spacing-4) var(--spacing-5)',
        fontSize: 'var(--font-size-lg)',
      },
    }

    const variantStyles = {
      outlined: {
        border: `1px solid ${error ? 'var(--color-error-main)' : 'var(--color-border-primary)'}`,
        borderRadius: 'var(--radius-md)',
        background: 'var(--color-bg-primary)',
      },
      filled: {
        border: 'none',
        borderBottom: `2px solid ${error ? 'var(--color-error-main)' : 'var(--color-border-primary)'}`,
        borderRadius: 'var(--radius-md) var(--radius-md) 0 0',
        background: 'var(--color-bg-secondary)',
      },
      standard: {
        border: 'none',
        borderBottom: `1px solid ${error ? 'var(--color-error-main)' : 'var(--color-border-primary)'}`,
        borderRadius: 0,
        background: 'transparent',
      },
    }

    return (
      <div style={{ width: fullWidth ? '100%' : 'auto' }}>
        <div
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            ...variantStyles[variant],
            ...sizeStyles[size],
            opacity: disabled ? 0.6 : 1,
            transition: 'all var(--transition-base)',
          }}
          className={clsx('input-wrapper', className)}
        >
          {startAdornment && (
            <div style={{ marginRight: 'var(--spacing-2)', display: 'flex', alignItems: 'center' }}>
              {startAdornment}
            </div>
          )}
          <input
            ref={ref}
            disabled={disabled}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              background: 'transparent',
              color: 'var(--color-text-primary)',
              fontFamily: 'var(--font-family-system)',
              fontSize: 'inherit',
              width: '100%',
            }}
            className={clsx('input', error && 'input-error')}
            {...props}
          />
          {endAdornment && (
            <div style={{ marginLeft: 'var(--spacing-2)', display: 'flex', alignItems: 'center' }}>
              {endAdornment}
            </div>
          )}
        </div>
        {helperText && (
          <div
            style={{
              marginTop: 'var(--spacing-1)',
              fontSize: 'var(--font-size-xs)',
              color: error ? 'var(--color-error-main)' : 'var(--color-text-secondary)',
            }}
          >
            {helperText}
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
