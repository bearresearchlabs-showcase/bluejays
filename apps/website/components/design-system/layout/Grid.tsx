'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Grid Component
 * 12-column grid system component
 */

export interface GridProps {
  children: React.ReactNode
  container?: boolean
  item?: boolean
  xs?: number | 'auto'
  sm?: number | 'auto'
  md?: number | 'auto'
  lg?: number | 'auto'
  xl?: number | 'auto'
  spacing?: number
  direction?: 'row' | 'column' | 'row-reverse' | 'column-reverse'
  justifyContent?: 'flex-start' | 'flex-end' | 'center' | 'space-between' | 'space-around' | 'space-evenly'
  alignItems?: 'flex-start' | 'flex-end' | 'center' | 'stretch' | 'baseline'
  className?: string
  style?: React.CSSProperties
}

export function Grid({
  children,
  container = false,
  item = false,
  xs,
  sm,
  md,
  lg,
  xl,
  spacing = 0,
  direction = 'row',
  justifyContent,
  alignItems,
  className,
  style,
}: GridProps) {
  if (container) {
    return (
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          flexDirection: direction,
          justifyContent,
          alignItems,
          width: '100%',
          margin: spacing > 0 ? `calc(-1 * var(--spacing-${spacing}) / 2)` : 0,
          ...style,
        }}
        className={clsx('grid-container', className)}
      >
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            return (
              <div
                style={{
                  padding: spacing > 0 ? `calc(var(--spacing-${spacing}) / 2)` : 0,
                }}
              >
                {child}
              </div>
            )
          }
          return child
        })}
      </div>
    )
  }

  const getColSpan = (breakpoint: string | number | 'auto' | undefined): string => {
    if (breakpoint === 'auto') return 'auto'
    if (typeof breakpoint === 'number') {
      return `${(breakpoint / 12) * 100}%`
    }
    return 'auto'
  }

  const baseStyle: React.CSSProperties = {
    flexGrow: 0,
    flexShrink: 0,
    flexBasis: 'auto',
    maxWidth: '100%',
    boxSizing: 'border-box',
  }

  const responsiveStyles: React.CSSProperties = {
    ...baseStyle,
    flexBasis: xs !== undefined ? getColSpan(xs) : 'auto',
    maxWidth: xs !== undefined && xs !== 'auto' ? getColSpan(xs) : '100%',
  }

  // Add responsive breakpoint styles via inline styles (simplified)
  // In a full implementation, you'd use CSS classes with media queries

  return (
    <div
      style={responsiveStyles}
      className={clsx('grid-item', className)}
      data-xs={xs}
      data-sm={sm}
      data-md={md}
      data-lg={lg}
      data-xl={xl}
    >
      {children}
    </div>
  )
}

export interface GridItemProps {
  children: React.ReactNode
  xs?: number | 'auto'
  sm?: number | 'auto'
  md?: number | 'auto'
  lg?: number | 'auto'
  xl?: number | 'auto'
  className?: string
}

export function GridItem({ children, xs, sm, md, lg, xl, className }: GridItemProps) {
  return (
    <Grid item xs={xs} sm={sm} md={md} lg={lg} xl={xl} className={className}>
      {children}
    </Grid>
  )
}
