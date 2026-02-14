'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Skeleton Component
 * Loading placeholder component
 */

export interface SkeletonProps {
  variant?: 'text' | 'rectangular' | 'circular'
  width?: number | string
  height?: number | string
  animation?: 'pulse' | 'wave' | false
  className?: string
}

export function Skeleton({
  variant = 'text',
  width,
  height,
  animation = 'pulse',
  className,
}: SkeletonProps) {
  const variantStyles = {
    text: {
      height: height || '1em',
      width: width || '100%',
      borderRadius: 'var(--radius-sm)',
    },
    rectangular: {
      height: height || '1em',
      width: width || '100%',
      borderRadius: 'var(--radius-md)',
    },
    circular: {
      height: height || '40px',
      width: width || '40px',
      borderRadius: 'var(--radius-full)',
    },
  }

  const animationClass = animation === 'pulse' ? 'skeleton-pulse' : animation === 'wave' ? 'skeleton-wave' : ''

  return (
    <div
      style={{
        ...variantStyles[variant],
        background: 'var(--color-bg-secondary)',
        display: 'inline-block',
      }}
      className={clsx('skeleton', `skeleton-${variant}`, animationClass, className)}
    >
      {animation === 'wave' && (
        <div
          style={{
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
            animation: 'skeleton-wave 1.5s ease-in-out infinite',
          }}
        />
      )}
      <style jsx>{`
        .skeleton-pulse {
          animation: skeleton-pulse 1.5s ease-in-out infinite;
        }
        @keyframes skeleton-pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        @keyframes skeleton-wave {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  )
}
