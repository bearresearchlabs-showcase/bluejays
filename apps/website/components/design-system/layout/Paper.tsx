'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Paper Component
 * Elevated surface component with shadow
 */

export interface PaperProps {
  children: React.ReactNode
  elevation?: number
  variant?: 'elevation' | 'outlined'
  square?: boolean
  className?: string
  style?: React.CSSProperties
  onMouseEnter?: (e: React.MouseEvent<HTMLDivElement>) => void
  onMouseLeave?: (e: React.MouseEvent<HTMLDivElement>) => void
}

export function Paper({
  children,
  elevation = 1,
  variant = 'elevation',
  square = false,
  className,
  style,
  onMouseEnter,
  onMouseLeave,
}: PaperProps) {
  const elevationShadow = elevation > 0 && variant === 'elevation' 
    ? `var(--elevation-${Math.min(elevation, 24)})` 
    : 'none'

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: square ? 0 : '6px',
        boxShadow: elevationShadow,
        border: variant === 'outlined' ? '1px solid var(--color-border-primary)' : 'none',
        padding: '20px',
        ...style,
      }}
      className={clsx('paper', className)}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {children}
    </div>
  )
}
