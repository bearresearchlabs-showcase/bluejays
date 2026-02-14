'use client'

import React from 'react'
import { clsx } from './utils'

/**
 * Icon Component
 * Icon wrapper component for SVG icons
 */

export interface IconProps {
  children?: React.ReactNode
  component?: React.ComponentType<any>
  fontSize?: 'inherit' | 'sm' | 'md' | 'lg' | number
  color?: 'inherit' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success' | 'action' | 'disabled'
  className?: string
  style?: React.CSSProperties
}

const fontSizeMap = {
  inherit: 'inherit',
  sm: 'var(--font-size-sm)',
  md: 'var(--font-size-base)',
  lg: 'var(--font-size-lg)',
}

const colorMap = {
  inherit: 'inherit',
  primary: 'var(--color-primary-main)',
  secondary: 'var(--color-secondary-main)',
  error: 'var(--color-error-main)',
  warning: 'var(--color-warning-main)',
  info: 'var(--color-info-main)',
  success: 'var(--color-success-main)',
  action: 'var(--color-text-secondary)',
  disabled: 'var(--color-text-disabled)',
}

export function Icon({
  children,
  component: Component,
  fontSize = 'md',
  color = 'inherit',
  className,
  style,
}: IconProps) {
  const fontSizeValue = typeof fontSize === 'number' ? `${fontSize}px` : fontSizeMap[fontSize]
  const colorValue = colorMap[color]

  if (Component) {
    return (
      <Component
        style={{
          fontSize: fontSizeValue,
          color: colorValue,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          ...style,
        }}
        className={clsx('icon', className)}
      />
    )
  }

  return (
    <span
      style={{
        fontSize: fontSizeValue,
        color: colorValue,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        lineHeight: 1,
        ...style,
      }}
      className={clsx('icon', className)}
    >
      {children}
    </span>
  )
}

/**
 * Common icon components (using Unicode/Emoji as fallback)
 * In production, replace with SVG icon library (Material Icons, Heroicons, etc.)
 */

export const AddIcon = () => <Icon>+</Icon>
export const DeleteIcon = () => <Icon>×</Icon>
export const EditIcon = () => <Icon>✎</Icon>
export const SearchIcon = () => <Icon>🔍</Icon>
export const CloseIcon = () => <Icon>×</Icon>
export const CheckIcon = () => <Icon>✓</Icon>
export const ArrowUpIcon = () => <Icon>↑</Icon>
export const ArrowDownIcon = () => <Icon>↓</Icon>
export const ArrowLeftIcon = () => <Icon>←</Icon>
export const ArrowRightIcon = () => <Icon>→</Icon>
export const MenuIcon = () => <Icon>☰</Icon>
export const MoreVertIcon = () => <Icon>⋮</Icon>
export const MoreHorizIcon = () => <Icon>⋯</Icon>
