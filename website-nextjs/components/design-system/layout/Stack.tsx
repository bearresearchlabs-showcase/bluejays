'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Stack Component
 * Flexbox-based layout component for stacking items
 */

export interface StackProps {
  children: React.ReactNode
  direction?: 'row' | 'column' | 'row-reverse' | 'column-reverse'
  spacing?: number
  justifyContent?: 'flex-start' | 'flex-end' | 'center' | 'space-between' | 'space-around' | 'space-evenly'
  alignItems?: 'flex-start' | 'flex-end' | 'center' | 'stretch' | 'baseline'
  flexWrap?: 'nowrap' | 'wrap' | 'wrap-reverse'
  className?: string
  style?: React.CSSProperties
}

export function Stack({
  children,
  direction = 'column',
  spacing = 2,
  justifyContent,
  alignItems,
  flexWrap,
  className,
  style,
}: StackProps) {
  const spacingValue = spacing > 0 ? `var(--spacing-${spacing})` : '0'

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: direction,
        gap: spacingValue,
        justifyContent,
        alignItems,
        flexWrap,
        ...style,
      }}
      className={clsx('stack', className)}
    >
      {children}
    </div>
  )
}
