'use client'

import React, { forwardRef } from 'react'
import { clsx } from '../utils'

/**
 * Radio Component
 * Radio button input with custom styling
 */

export interface RadioProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'size'> {
  label?: string
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
}

const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      label,
      size = 'md',
      color = 'primary',
      className,
      checked,
      onChange,
      disabled,
      ...props
    },
    ref
  ) => {
    const sizeStyles = {
      sm: { width: '16px', height: '16px' },
      md: { width: '20px', height: '20px' },
      lg: { width: '24px', height: '24px' },
    }

    const colorStyles = {
      primary: 'var(--color-primary-main)',
      secondary: 'var(--color-secondary-main)',
      error: 'var(--color-error-main)',
      warning: 'var(--color-warning-main)',
      info: 'var(--color-info-main)',
      success: 'var(--color-success-main)',
    }

    const radio = (
      <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
        <input
          ref={ref}
          type="radio"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          style={{
            ...sizeStyles[size],
            cursor: disabled ? 'not-allowed' : 'pointer',
            opacity: disabled ? 0.5 : 1,
            accentColor: colorStyles[color],
          }}
          className={clsx('radio', className)}
          {...props}
        />
      </div>
    )

    if (!label) {
      return radio
    }

    return (
      <label
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
          cursor: disabled ? 'not-allowed' : 'pointer',
          fontSize: 'var(--font-size-base)',
          color: disabled ? 'var(--color-text-disabled)' : 'var(--color-text-primary)',
          userSelect: 'none',
        }}
      >
        {radio}
        <span>{label}</span>
      </label>
    )
  }
)

Radio.displayName = 'Radio'

export default Radio
