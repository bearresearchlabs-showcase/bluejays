'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Alert Component
 * Alert message component with variants
 */

export interface AlertProps {
  children: React.ReactNode
  severity?: 'success' | 'error' | 'warning' | 'info'
  variant?: 'standard' | 'filled' | 'outlined'
  icon?: React.ReactNode
  action?: React.ReactNode
  onClose?: () => void
  className?: string
}

const severityStyles = {
  success: {
    standard: {
      background: '#d1fae5',
      color: '#065f46',
      border: '1px solid #10b981',
    },
    filled: {
      background: '#10b981',
      color: '#ffffff',
      border: 'none',
    },
    outlined: {
      background: 'transparent',
      color: '#065f46',
      border: '1px solid #10b981',
    },
  },
  error: {
    standard: {
      background: '#fee2e2',
      color: '#991b1b',
      border: '1px solid #ef4444',
    },
    filled: {
      background: '#ef4444',
      color: '#ffffff',
      border: 'none',
    },
    outlined: {
      background: 'transparent',
      color: '#991b1b',
      border: '1px solid #ef4444',
    },
  },
  warning: {
    standard: {
      background: '#fef3c7',
      color: '#92400e',
      border: '1px solid #f59e0b',
    },
    filled: {
      background: '#f59e0b',
      color: '#000000',
      border: 'none',
    },
    outlined: {
      background: 'transparent',
      color: '#92400e',
      border: '1px solid #f59e0b',
    },
  },
  info: {
    standard: {
      background: '#dbeafe',
      color: '#1e40af',
      border: '1px solid #3b82f6',
    },
    filled: {
      background: '#3b82f6',
      color: '#ffffff',
      border: 'none',
    },
    outlined: {
      background: 'transparent',
      color: '#1e40af',
      border: '1px solid #3b82f6',
    },
  },
}

const defaultIcons = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'ℹ',
}

export function Alert({
  children,
  severity = 'info',
  variant = 'standard',
  icon,
  action,
  onClose,
  className,
}: AlertProps) {
  const styles = severityStyles[severity][variant]
  const defaultIcon = defaultIcons[severity]

  return (
    <div
      style={{
        ...styles,
        padding: 'var(--spacing-4)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--spacing-3)',
        fontSize: 'var(--font-size-sm)',
        lineHeight: 'var(--line-height-normal)',
      }}
      className={clsx('alert', `alert-${severity}`, `alert-${variant}`, className)}
      role="alert"
    >
      {(icon || defaultIcon) && (
        <div style={{ flexShrink: 0, fontSize: 'var(--font-size-lg)' }}>
          {icon || defaultIcon}
        </div>
      )}
      <div style={{ flex: 1 }}>{children}</div>
      {(action || onClose) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
          {action}
          {onClose && (
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: 'var(--spacing-1)',
                color: 'inherit',
                fontSize: 'var(--font-size-lg)',
                lineHeight: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              aria-label="Close alert"
            >
              ×
            </button>
          )}
        </div>
      )}
    </div>
  )
}
