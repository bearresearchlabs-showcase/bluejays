'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * LinearProgress Component
 * Linear progress indicator
 */

export interface LinearProgressProps {
  value?: number
  variant?: 'determinate' | 'indeterminate' | 'buffer'
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const colorStyles = {
  primary: 'var(--color-primary-main)',
  secondary: 'var(--color-secondary-main)',
  error: 'var(--color-error-main)',
  warning: 'var(--color-warning-main)',
  info: 'var(--color-info-main)',
  success: 'var(--color-success-main)',
}

const sizeStyles = {
  sm: { height: '4px' },
  md: { height: '6px' },
  lg: { height: '8px' },
}

export function LinearProgress({
  value,
  variant = 'indeterminate',
  color = 'primary',
  size = 'md',
  className,
}: LinearProgressProps) {
  return (
    <div
      style={{
        width: '100%',
        ...sizeStyles[size],
        background: 'var(--color-bg-secondary)',
        borderRadius: 'var(--radius-full)',
        overflow: 'hidden',
        position: 'relative',
      }}
      className={clsx('linear-progress', className)}
      role="progressbar"
      aria-valuenow={variant === 'determinate' ? value : undefined}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      {variant === 'indeterminate' ? (
        <div
          style={{
            width: '100%',
            height: '100%',
            background: `linear-gradient(to right, transparent, ${colorStyles[color]}, transparent)`,
            animation: 'linear-indeterminate 1.5s ease-in-out infinite',
          }}
        />
      ) : (
        <div
          style={{
            width: `${value || 0}%`,
            height: '100%',
            background: colorStyles[color],
            transition: 'width 300ms ease-in-out',
            borderRadius: 'var(--radius-full)',
          }}
        />
      )}
      <style jsx>{`
        @keyframes linear-indeterminate {
          0% {
            transform: translateX(-100%);
          }
          50% {
            transform: translateX(0%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  )
}
