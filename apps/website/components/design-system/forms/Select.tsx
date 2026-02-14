'use client'

import React, { forwardRef, useState, useRef, useEffect } from 'react'
import { clsx } from '../utils'

/**
 * Select Component
 * Dropdown select component with custom styling
 */

export interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  options: SelectOption[]
  variant?: 'outlined' | 'filled' | 'standard'
  size?: 'sm' | 'md' | 'lg'
  error?: boolean
  helperText?: string
  label?: string
  fullWidth?: boolean
  placeholder?: string
  native?: boolean
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      options,
      variant = 'outlined',
      size = 'md',
      error = false,
      helperText,
      label,
      fullWidth = false,
      placeholder,
      native = true,
      className,
      disabled,
      value,
      onChange,
      ...props
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = useState(false)
    const [selectedValue, setSelectedValue] = useState<string | number | undefined>(value as string | number | undefined)
    const selectRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
      setSelectedValue(value as string | number | undefined)
    }, [value])

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
          setIsOpen(false)
        }
      }

      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside)
      }

      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
      }
    }, [isOpen])

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

    const selectedOption = options.find((opt) => opt.value === selectedValue)

    if (native) {
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
          <select
            ref={ref}
            disabled={disabled}
            value={selectedValue}
            onChange={(e) => {
              setSelectedValue(e.target.value)
              onChange?.(e)
            }}
            style={{
              width: '100%',
              ...variantStyles[variant],
              ...sizeStyles[size],
              color: 'var(--color-text-primary)',
              fontFamily: 'var(--font-family-system)',
              outline: 'none',
              opacity: disabled ? 0.6 : 1,
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'all var(--transition-base)',
              appearance: 'none',
              backgroundImage: 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'12\' viewBox=\'0 0 12 12\'%3E%3Cpath fill=\'%23000\' d=\'M6 9L1 4h10z\'/%3E%3C/svg%3E")',
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'right var(--spacing-3) center',
              paddingRight: 'var(--spacing-10)',
            }}
            className={clsx('select', error && 'select-error', className)}
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
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))}
          </select>
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

    // Custom select implementation (simplified)
    return (
      <div ref={selectRef} style={{ width: fullWidth ? '100%' : 'auto', position: 'relative' }}>
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
        <div
          onClick={() => !disabled && setIsOpen(!isOpen)}
          style={{
            width: '100%',
            ...variantStyles[variant],
            ...sizeStyles[size],
            color: selectedValue ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
            fontFamily: 'var(--font-family-system)',
            outline: 'none',
            opacity: disabled ? 0.6 : 1,
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all var(--transition-base)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
          className={clsx('select-custom', error && 'select-error', className)}
        >
          <span>{selectedOption ? selectedOption.label : placeholder || 'Select...'}</span>
          <span style={{ fontSize: 'var(--font-size-xs)', transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform var(--transition-base)' }}>
            ▼
          </span>
        </div>
        {isOpen && (
          <div
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              marginTop: 'var(--spacing-1)',
              background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border-primary)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-lg)',
              zIndex: 'var(--z-dropdown)',
              maxHeight: '200px',
              overflowY: 'auto',
            }}
          >
            {options.map((option) => (
              <div
                key={option.value}
                onClick={() => {
                  if (!option.disabled) {
                    setSelectedValue(option.value)
                    setIsOpen(false)
                    onChange?.({
                      target: { value: String(option.value) },
                    } as React.ChangeEvent<HTMLSelectElement>)
                  }
                }}
                style={{
                  padding: 'var(--spacing-3) var(--spacing-4)',
                  cursor: option.disabled ? 'not-allowed' : 'pointer',
                  opacity: option.disabled ? 0.5 : 1,
                  backgroundColor: selectedValue === option.value ? 'var(--color-bg-secondary)' : 'transparent',
                  color: 'var(--color-text-primary)',
                  fontSize: 'var(--font-size-sm)',
                }}
                onMouseEnter={(e) => {
                  if (!option.disabled) {
                    e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedValue !== option.value) {
                    e.currentTarget.style.backgroundColor = 'transparent'
                  }
                }}
              >
                {option.label}
              </div>
            ))}
          </div>
        )}
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

Select.displayName = 'Select'

export default Select
