'use client'

import React, { forwardRef } from 'react'
import { clsx } from '../utils'

/**
 * Textarea Component
 * Multi-line text input component
 */

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'outlined' | 'filled' | 'standard'
  size?: 'sm' | 'md' | 'lg'
  error?: boolean
  helperText?: string
  label?: string
  fullWidth?: boolean
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      variant = 'outlined',
      size = 'md',
      error = false,
      helperText,
      label,
      fullWidth = false,
      className,
      disabled,
      rows = 4,
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
        {label && (
          <label
            style={{
              display: 'block',
              marginBottom: 'var(--spacing-2)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 'var(--font-weight-medium)',
              color: error ? 'var(--color-error-main)' : 'var(--color-text-primary)',
            }}
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          disabled={disabled}
          rows={rows}
          style={{
            width: '100%',
            ...variantStyles[variant],
            ...sizeStyles[size],
            color: 'var(--color-text-primary)',
            fontFamily: 'var(--font-family-system)',
            lineHeight: 'var(--line-height-normal)',
            resize: 'vertical',
            outline: 'none',
            opacity: disabled ? 0.6 : 1,
            transition: 'all var(--transition-base)',
          }}
          className={clsx('textarea', error && 'textarea-error', className)}
          onFocus={(e) => {
            if (variant === 'outlined') {
              e.currentTarget.style.borderColor = 'var(--color-border-focus)'
            } else if (variant === 'filled' || variant === 'standard') {
              e.currentTarget.style.borderBottomColor = 'var(--color-border-focus)'
            }
          }}
          onBlur={(e) => {
            if (variant === 'outlined') {
              e.currentTarget.style.borderColor = error ? 'var(--color-error-main)' : 'var(--color-border-primary)'
            } else if (variant === 'filled' || variant === 'standard') {
              e.currentTarget.style.borderBottomColor = error ? 'var(--color-error-main)' : 'var(--color-border-primary)'
            }
          }}
          {...props}
        />
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

Textarea.displayName = 'Textarea'

export default Textarea
