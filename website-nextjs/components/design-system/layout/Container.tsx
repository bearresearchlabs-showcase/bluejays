'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Container Component
 * Responsive container component with max-width constraints
 */

export interface ContainerProps {
  children: React.ReactNode
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false
  fixed?: boolean
  disableGutters?: boolean
  className?: string
  style?: React.CSSProperties
}

const maxWidthMap = {
  xs: '444px',
  sm: '600px',
  md: '900px',
  lg: '1200px',
  xl: '1536px',
}

export function Container({
  children,
  maxWidth = 'lg',
  fixed = false,
  disableGutters = false,
  className,
  style,
}: ContainerProps) {
  return (
    <div
      style={{
        width: '100%',
        marginLeft: 'auto',
        marginRight: 'auto',
        paddingLeft: disableGutters ? 0 : 'var(--spacing-4)',
        paddingRight: disableGutters ? 0 : 'var(--spacing-4)',
        maxWidth: maxWidth === false ? 'none' : maxWidthMap[maxWidth],
        boxSizing: 'border-box',
        ...style,
      }}
      className={clsx('container', className)}
    >
      {children}
    </div>
  )
}
