'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Typography Component
 * Typography component with variants
 */

export interface TypographyProps {
  children: React.ReactNode
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'body1' | 'body2' | 'button' | 'caption' | 'overline'
  component?: keyof React.JSX.IntrinsicElements
  color?: 'primary' | 'secondary' | 'tertiary' | 'disabled' | 'error' | 'warning' | 'info' | 'success'
  align?: 'left' | 'center' | 'right' | 'justify'
  gutterBottom?: boolean
  noWrap?: boolean
  className?: string
  style?: React.CSSProperties
  fontWeight?: 'normal' | 'medium' | 'semibold' | 'bold'
}

const variantStyles = {
  h1: {
    fontSize: 'var(--typography-h1-size)',
    fontWeight: 'var(--typography-h1-weight)',
    lineHeight: 'var(--typography-h1-line-height)',
  },
  h2: {
    fontSize: 'var(--typography-h2-size)',
    fontWeight: 'var(--typography-h2-weight)',
    lineHeight: 'var(--typography-h2-line-height)',
  },
  h3: {
    fontSize: 'var(--typography-h3-size)',
    fontWeight: 'var(--typography-h3-weight)',
    lineHeight: 'var(--typography-h3-line-height)',
  },
  h4: {
    fontSize: 'var(--typography-h4-size)',
    fontWeight: 'var(--typography-h4-weight)',
    lineHeight: 'var(--typography-h4-line-height)',
  },
  h5: {
    fontSize: 'var(--typography-h5-size)',
    fontWeight: 'var(--typography-h5-weight)',
    lineHeight: 'var(--typography-h5-line-height)',
  },
  h6: {
    fontSize: 'var(--typography-h6-size)',
    fontWeight: 'var(--typography-h6-weight)',
    lineHeight: 'var(--typography-h6-line-height)',
  },
  body1: {
    fontSize: 'var(--typography-body1-size)',
    fontWeight: 'var(--typography-body1-weight)',
    lineHeight: 'var(--typography-body1-line-height)',
  },
  body2: {
    fontSize: 'var(--typography-body2-size)',
    fontWeight: 'var(--typography-body2-weight)',
    lineHeight: 'var(--typography-body2-line-height)',
  },
  button: {
    fontSize: 'var(--typography-button-size)',
    fontWeight: 'var(--typography-button-weight)',
    lineHeight: 'var(--typography-button-line-height)',
  },
  caption: {
    fontSize: 'var(--typography-caption-size)',
    fontWeight: 'var(--typography-caption-weight)',
    lineHeight: 'var(--typography-caption-line-height)',
  },
  overline: {
    fontSize: 'var(--typography-overline-size)',
    fontWeight: 'var(--typography-overline-weight)',
    lineHeight: 'var(--typography-overline-line-height)',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
}

const colorStyles = {
  primary: 'var(--color-text-primary)',
  secondary: 'var(--color-text-secondary)',
  tertiary: 'var(--color-text-tertiary)',
  disabled: 'var(--color-text-disabled)',
  error: 'var(--color-error-main)',
  warning: 'var(--color-warning-main)',
  info: 'var(--color-info-main)',
  success: 'var(--color-success-main)',
}

const componentMap: Record<string, keyof React.JSX.IntrinsicElements> = {
  h1: 'h1',
  h2: 'h2',
  h3: 'h3',
  h4: 'h4',
  h5: 'h5',
  h6: 'h6',
  body1: 'p',
  body2: 'p',
  button: 'span',
  caption: 'span',
  overline: 'span',
}

export function Typography({
  children,
  variant = 'body1',
  component,
  color = 'primary',
  align,
  gutterBottom = false,
  noWrap = false,
  className,
  style,
  fontWeight,
}: TypographyProps) {
  const Component = component || componentMap[variant] || 'p'
  const styles = variantStyles[variant]
  const fontWeightValue = fontWeight ? `var(--font-weight-${fontWeight})` : undefined

  return (
    <Component
      style={{
        ...styles,
        color: colorStyles[color],
        textAlign: align,
        marginBottom: gutterBottom ? 'var(--spacing-2)' : 0,
        whiteSpace: noWrap ? 'nowrap' : 'normal',
        overflow: noWrap ? 'hidden' : 'visible',
        textOverflow: noWrap ? 'ellipsis' : 'clip',
        margin: 0,
        fontWeight: fontWeightValue,
        ...style,
      }}
      className={clsx('typography', `typography-${variant}`, className)}
    >
      {children}
    </Component>
  )
}
