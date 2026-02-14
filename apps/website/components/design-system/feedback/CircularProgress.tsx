'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * CircularProgress Component
 * Circular progress indicator
 */

export interface CircularProgressProps {
  size?: number | string
  thickness?: number
  value?: number
  variant?: 'determinate' | 'indeterminate'
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
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

export function CircularProgress({
  size = 40,
  thickness = 4,
  value,
  variant = 'indeterminate',
  color = 'primary',
  className,
}: CircularProgressProps) {
  const sizeValue = typeof size === 'number' ? `${size}px` : size
  const radius = (typeof size === 'number' ? size : parseInt(size)) / 2 - thickness / 2
  const circumference = 2 * Math.PI * radius
  const offset = variant === 'determinate' && value !== undefined
    ? circumference - (value / 100) * circumference
    : 0

  return (
    <div
      style={{
        display: 'inline-block',
        position: 'relative',
        width: sizeValue,
        height: sizeValue,
      }}
      className={clsx('circular-progress', className)}
    >
      <svg
        width={sizeValue}
        height={sizeValue}
        style={{
          transform: 'rotate(-90deg)',
        }}
      >
        <circle
          cx={typeof size === 'number' ? size / 2 : '50%'}
          cy={typeof size === 'number' ? size / 2 : '50%'}
          r={radius}
          fill="none"
          stroke={colorStyles[color]}
          strokeWidth={thickness}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transition: variant === 'determinate' ? 'stroke-dashoffset 300ms ease-in-out' : 'none',
            animation: variant === 'indeterminate' ? 'circular-rotate 1.4s linear infinite' : 'none',
          }}
        />
        {variant === 'indeterminate' && (
          <circle
            cx={typeof size === 'number' ? size / 2 : '50%'}
            cy={typeof size === 'number' ? size / 2 : '50%'}
            r={radius}
            fill="none"
            stroke={colorStyles[color]}
            strokeWidth={thickness}
            strokeDasharray={circumference * 0.25}
            strokeLinecap="round"
            style={{
              opacity: 0.3,
            }}
          />
        )}
      </svg>
      {variant === 'determinate' && value !== undefined && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--color-text-secondary)',
            fontWeight: 'var(--font-weight-medium)',
          }}
        >
          {Math.round(value)}%
        </div>
      )}
      <style jsx>{`
        @keyframes circular-rotate {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  )
}
