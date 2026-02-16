'use client'

import React from 'react'
import { CircularProgress } from './feedback/CircularProgress'
import { clsx } from './utils'

/**
 * Button Component
 * Primary actions with brand accent colors.
 * Enhanced with loading state, icon support, and FAB variant.
 * Based on OpenAI Apps SDK UI guidelines.
 */

export interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'fab'
  size?: 'sm' | 'md' | 'lg'
  onClick?: React.MouseEventHandler<HTMLButtonElement>
  disabled?: boolean
  fullWidth?: boolean
  loading?: boolean
  startIcon?: React.ReactNode
  endIcon?: React.ReactNode
  className?: string
  type?: 'button' | 'submit' | 'reset'
  style?: React.CSSProperties
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  fullWidth = false,
  loading = false,
  startIcon,
  endIcon,
  className = '',
  type = 'button',
  style,
}: ButtonProps) {
  const variantStyles = {
    primary: {
      background: 'var(--color-accent-primary)',
      color: 'var(--color-bg-primary)',
      border: 'none'
    },
    secondary: {
      background: 'transparent',
      color: 'var(--color-accent-primary)',
      border: '1px solid var(--color-border-primary)'
    },
    ghost: {
      background: 'transparent',
      color: 'var(--color-text-secondary)',
      border: 'none'
    },
    fab: {
      background: 'var(--color-accent-primary)',
      color: 'var(--color-bg-primary)',
      border: 'none',
      borderRadius: 'var(--radius-full)',
      width: size === 'sm' ? '40px' : size === 'lg' ? '56px' : '48px',
      height: size === 'sm' ? '40px' : size === 'lg' ? '56px' : '48px',
      padding: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: 'var(--elevation-6)'
    }
  }

  const sizeStyles = {
    sm: {
      padding: variant === 'fab' ? 0 : 'var(--spacing-2) var(--spacing-4)',
      fontSize: 'var(--font-size-sm)',
      minHeight: '32px'
    },
    md: {
      padding: variant === 'fab' ? 0 : 'var(--spacing-3) var(--spacing-5)',
      fontSize: 'var(--font-size-base)',
      minHeight: '40px'
    },
    lg: {
      padding: variant === 'fab' ? 0 : 'var(--spacing-4) var(--spacing-6)',
      fontSize: 'var(--font-size-lg)',
      minHeight: '48px'
    }
  }

  const isDisabled = disabled || loading

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={clsx('button', `button-${variant}`, `button-${size}`, className)}
      style={{
        ...variantStyles[variant],
        ...sizeStyles[size],
        borderRadius: variant === 'fab' ? 'var(--radius-full)' : 'var(--radius-md)',
        fontWeight: 'var(--font-weight-medium)',
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        opacity: isDisabled ? 0.5 : 1,
        width: fullWidth && variant !== 'fab' ? '100%' : variant === 'fab' ? variantStyles.fab.width : 'auto',
        height: variant === 'fab' ? variantStyles.fab.height : 'auto',
        transition: 'all var(--transition-base)',
        fontFamily: 'var(--font-family-system)',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 'var(--spacing-2)',
        position: 'relative',
        ...style,
      }}
      onMouseEnter={(e) => {
        if (!isDisabled) {
          if (variant === 'primary' || variant === 'fab') {
            e.currentTarget.style.background = 'var(--color-accent-primary-hover)'
            if (variant === 'fab') {
              e.currentTarget.style.boxShadow = 'var(--elevation-8)'
            }
          } else if (variant === 'secondary') {
            e.currentTarget.style.borderColor = 'var(--color-accent-primary)'
          }
        }
      }}
      onMouseLeave={(e) => {
        if (variant === 'primary' || variant === 'fab') {
          e.currentTarget.style.background = 'var(--color-accent-primary)'
          if (variant === 'fab') {
            e.currentTarget.style.boxShadow = 'var(--elevation-6)'
          }
        } else if (variant === 'secondary') {
          e.currentTarget.style.borderColor = 'var(--color-border-primary)'
        }
      }}
    >
      {loading ? (
        <CircularProgress size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
      ) : (
        <>
          {startIcon && <span style={{ display: 'flex', alignItems: 'center' }}>{startIcon}</span>}
          {variant !== 'fab' && <span>{children}</span>}
          {variant === 'fab' && <span style={{ display: 'flex', alignItems: 'center' }}>{children}</span>}
          {endIcon && <span style={{ display: 'flex', alignItems: 'center' }}>{endIcon}</span>}
        </>
      )}
    </button>
  )
}
