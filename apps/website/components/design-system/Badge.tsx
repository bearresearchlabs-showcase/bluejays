'use client'

import React from 'react'

/**
 * Badge Component
 * Small labels for status, categories, or metadata.
 * Based on OpenAI Apps SDK UI guidelines.
 */

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md'
  className?: string
}

export default function Badge({
  children,
  variant = 'default',
  size = 'md',
  className = ''
}: BadgeProps) {
  const variantStyles = {
    default: {
      background: 'var(--color-bg-secondary)',
      color: 'var(--color-text-secondary)'
    },
    success: {
      background: '#d1fae5',
      color: '#065f46'
    },
    warning: {
      background: '#fef3c7',
      color: '#92400e'
    },
    error: {
      background: '#fee2e2',
      color: '#991b1b'
    },
    info: {
      background: '#dbeafe',
      color: '#1e40af'
    }
  }

  const sizeStyles = {
    sm: {
      padding: 'var(--spacing-1) var(--spacing-2)',
      fontSize: 'var(--font-size-xs)'
    },
    md: {
      padding: 'var(--spacing-2) var(--spacing-3)',
      fontSize: 'var(--font-size-sm)'
    }
  }

  return (
    <span
      className={`badge badge-${variant} badge-${size} ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        borderRadius: 'var(--radius-full)',
        fontWeight: 'var(--font-weight-medium)',
        whiteSpace: 'nowrap',
        ...variantStyles[variant],
        ...sizeStyles[size]
      }}
    >
      {children}
    </span>
  )
}
