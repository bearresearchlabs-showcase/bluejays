'use client'

import React, { forwardRef } from 'react'
import Input, { InputProps } from './Input'
import { clsx } from '../utils'

/**
 * TextField Component
 * Enhanced input with label and helper text
 */

export interface TextFieldProps extends InputProps {
  label?: string
  placeholder?: string
  required?: boolean
  multiline?: boolean
  rows?: number
}

const TextField = forwardRef<HTMLInputElement | HTMLTextAreaElement, TextFieldProps>(
  (
    {
      label,
      placeholder,
      required,
      multiline = false,
      rows = 4,
      helperText,
      error,
      id,
      ...props
    },
    ref
  ) => {
    const fieldId = id || `textfield-${Math.random().toString(36).substr(2, 9)}`
    const hasLabel = Boolean(label)

    if (multiline) {
      return (
        <div style={{ width: props.fullWidth ? '100%' : 'auto' }}>
          {hasLabel && (
            <label
              htmlFor={fieldId}
              style={{
                display: 'block',
                marginBottom: 'var(--spacing-2)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-medium)',
                color: error ? 'var(--color-error-main)' : 'var(--color-text-primary)',
              }}
            >
              {label}
              {required && <span style={{ color: 'var(--color-error-main)', marginLeft: 'var(--spacing-1)' }}>*</span>}
            </label>
          )}
          <textarea
            ref={ref as React.Ref<HTMLTextAreaElement>}
            id={fieldId}
            placeholder={placeholder}
            required={required}
            rows={rows}
            style={{
              width: '100%',
              padding: 'var(--spacing-3) var(--spacing-4)',
              border: `1px solid ${error ? 'var(--color-error-main)' : 'var(--color-border-primary)'}`,
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-bg-primary)',
              color: 'var(--color-text-primary)',
              fontFamily: 'var(--font-family-system)',
              fontSize: 'var(--font-size-base)',
              lineHeight: 'var(--line-height-normal)',
              resize: 'vertical',
              outline: 'none',
              transition: 'all var(--transition-base)',
            }}
            className={clsx('textarea', error && 'textarea-error')}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'var(--color-border-focus)'
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = error ? 'var(--color-error-main)' : 'var(--color-border-primary)'
            }}
            {...(props as any)}
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

    return (
      <div style={{ width: props.fullWidth ? '100%' : 'auto' }}>
        {hasLabel && (
          <label
            htmlFor={fieldId}
            style={{
              display: 'block',
              marginBottom: 'var(--spacing-2)',
              fontSize: 'var(--font-size-sm)',
              fontWeight: 'var(--font-weight-medium)',
              color: error ? 'var(--color-error-main)' : 'var(--color-text-primary)',
            }}
          >
            {label}
            {required && <span style={{ color: 'var(--color-error-main)', marginLeft: 'var(--spacing-1)' }}>*</span>}
          </label>
        )}
        <Input
          ref={ref as React.Ref<HTMLInputElement>}
          id={fieldId}
          placeholder={placeholder}
          required={required}
          error={error}
          helperText={helperText}
          {...props}
        />
      </div>
    )
  }
)

TextField.displayName = 'TextField'

export default TextField
