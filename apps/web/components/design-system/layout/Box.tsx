'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Box Component
 * Generic container component with flexible styling props
 */

export interface BoxProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode
  component?: keyof React.JSX.IntrinsicElements
  sx?: React.CSSProperties
  className?: string
}

export function Box({
  children,
  component = 'div',
  sx,
  className,
  style,
  ...props
}: BoxProps) {
  const Component = component as any
  
  // Filter out non-DOM props that might be passed from parent components (e.g., Accordion)
  const {
    expanded,
    onToggle,
    disabled,
    ...domProps
  } = props as any

  return (
    <Component
      style={{
        ...style,
        ...sx,
      }}
      className={clsx('box', className)}
      {...domProps}
    >
      {children}
    </Component>
  )
}
