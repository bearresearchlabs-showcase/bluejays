'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * AppBar Component
 * Application bar component
 */

export interface AppBarProps {
  children: React.ReactNode
  position?: 'static' | 'fixed' | 'sticky' | 'relative'
  color?: 'default' | 'primary' | 'secondary'
  elevation?: number
  className?: string
}

export function AppBar({
  children,
  position = 'static',
  color = 'default',
  elevation = 0,
  className,
}: AppBarProps) {
  const colorStyles = {
    default: {
      background: 'var(--color-bg-elevated)',
      color: 'var(--color-text-primary)',
    },
    primary: {
      background: 'var(--color-primary-main)',
      color: 'var(--color-primary-contrast-text)',
    },
    secondary: {
      background: 'var(--color-secondary-main)',
      color: 'var(--color-secondary-contrast-text)',
    },
  }

  const elevationShadow = elevation > 0 ? `var(--elevation-${Math.min(elevation, 24)})` : 'none'

  return (
    <header
      style={{
        position,
        top: position === 'fixed' || position === 'sticky' ? 0 : 'auto',
        left: 0,
        right: 0,
        zIndex: 'var(--z-app-bar)',
        ...colorStyles[color],
        boxShadow: elevationShadow,
        padding: 'var(--spacing-3) var(--spacing-6)',
        display: 'flex',
        alignItems: 'center',
        minHeight: '64px',
      }}
      className={clsx('app-bar', className)}
    >
      {children}
    </header>
  )
}
