'use client'

import React from 'react'
import { CircularProgress } from './CircularProgress'
import { LinearProgress } from './LinearProgress'
import { clsx } from '../utils'

/**
 * Loading Component
 * Loading state component with overlay support
 */

export interface LoadingProps {
  variant?: 'circular' | 'linear'
  overlay?: boolean
  size?: number | string
  message?: string
  className?: string
}

export function Loading({
  variant = 'circular',
  overlay = false,
  size,
  message,
  className,
}: LoadingProps) {
  const content = (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: message ? 'var(--spacing-4)' : 0,
      }}
      className={clsx('loading', className)}
    >
      {variant === 'circular' ? (
        <CircularProgress size={size} />
      ) : (
        <div style={{ width: size || '200px' }}>
          <LinearProgress />
        </div>
      )}
      {message && (
        <div
          style={{
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-secondary)',
            textAlign: 'center',
          }}
        >
          {message}
        </div>
      )}
    </div>
  )

  if (overlay) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(255, 255, 255, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 'var(--z-modal)',
        }}
        className="loading-overlay"
      >
        {content}
      </div>
    )
  }

  return content
}
