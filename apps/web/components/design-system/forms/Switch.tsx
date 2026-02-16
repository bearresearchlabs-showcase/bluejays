'use client'

import React, { forwardRef } from 'react'
import { clsx } from '../utils'

/**
 * Switch Component
 * Toggle switch component
 */

export interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'size'> {
  label?: string
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
}

const Switch = forwardRef<HTMLInputElement, SwitchProps>(
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
      sm: { width: '32px', height: '18px' },
      md: { width: '40px', height: '22px' },
      lg: { width: '48px', height: '26px' },
    }

    const colorStyles = {
      primary: 'var(--color-primary-main)',
      secondary: 'var(--color-secondary-main)',
      error: 'var(--color-error-main)',
      warning: 'var(--color-warning-main)',
      info: 'var(--color-info-main)',
      success: 'var(--color-success-main)',
    }

    const switchElement = (
      <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
        <input
          ref={ref}
          type="checkbox"
          role="switch"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          style={{
            ...sizeStyles[size],
            cursor: disabled ? 'not-allowed' : 'pointer',
            opacity: disabled ? 0.5 : 1,
            accentColor: colorStyles[color],
          }}
          className={clsx('switch', className)}
          {...props}
        />
      </div>
    )

    if (!label) {
      return switchElement
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
        {switchElement}
        <span>{label}</span>
      </label>
    )
  }
)

Switch.displayName = 'Switch'

export default Switch
