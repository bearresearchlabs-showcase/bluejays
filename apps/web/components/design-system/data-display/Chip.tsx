'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Chip Component
 * Small label component (enhanced Badge)
 */

export interface ChipProps {
  label: string
  variant?: 'default' | 'outlined' | 'filled'
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
  size?: 'sm' | 'md'
  onDelete?: () => void
  onClick?: () => void
  avatar?: React.ReactNode
  icon?: React.ReactNode
  className?: string
}

const colorStyles = {
  default: {
    background: 'var(--color-bg-secondary)',
    color: 'var(--color-text-primary)',
    border: '1px solid var(--color-border-primary)',
  },
  primary: {
    background: 'var(--color-primary-main)',
    color: 'var(--color-primary-contrast-text)',
    border: 'none',
  },
  secondary: {
    background: 'var(--color-secondary-main)',
    color: 'var(--color-secondary-contrast-text)',
    border: 'none',
  },
  error: {
    background: 'var(--color-error-main)',
    color: 'var(--color-error-contrast-text)',
    border: 'none',
  },
  warning: {
    background: 'var(--color-warning-main)',
    color: 'var(--color-warning-contrast-text)',
    border: 'none',
  },
  info: {
    background: 'var(--color-info-main)',
    color: 'var(--color-info-contrast-text)',
    border: 'none',
  },
  success: {
    background: 'var(--color-success-main)',
    color: 'var(--color-success-contrast-text)',
    border: 'none',
  },
}

export function Chip({
  label,
  variant = 'default',
  color = 'default',
  size = 'md',
  onDelete,
  onClick,
  avatar,
  icon,
  className,
}: ChipProps) {
  const styles = colorStyles[color]
  const isOutlined = variant === 'outlined'
  const isFilled = variant === 'filled'

  const chipStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--spacing-1)',
    padding: size === 'sm' ? 'var(--spacing-1) var(--spacing-2)' : 'var(--spacing-2) var(--spacing-3)',
    borderRadius: 'var(--radius-full)',
    fontSize: size === 'sm' ? 'var(--font-size-xs)' : 'var(--font-size-sm)',
    fontWeight: 'var(--font-weight-medium)',
    background: isOutlined ? 'transparent' : isFilled ? styles.background : styles.background,
    color: isOutlined ? styles.color : styles.color,
    border: isOutlined ? styles.border : 'none',
    cursor: onClick ? 'pointer' : 'default',
    transition: 'all var(--transition-base)',
  }

  return (
    <span
      onClick={onClick}
      style={chipStyles}
      className={clsx('chip', `chip-${variant}`, `chip-${color}`, className)}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.opacity = '0.8'
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.opacity = '1'
      }}
    >
      {avatar && <span style={{ display: 'flex', alignItems: 'center' }}>{avatar}</span>}
      {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
      <span>{label}</span>
      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          style={{
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
            marginLeft: 'var(--spacing-1)',
            display: 'flex',
            alignItems: 'center',
            fontSize: 'var(--font-size-sm)',
            color: 'inherit',
            lineHeight: 1,
          }}
          aria-label="Delete chip"
        >
          ×
        </button>
      )}
    </span>
  )
}
