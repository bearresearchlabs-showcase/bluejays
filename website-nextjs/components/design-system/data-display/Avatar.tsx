'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Avatar Component
 * Avatar component with image, letter, or icon support
 */

export interface AvatarProps {
  src?: string
  alt?: string
  children?: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | number
  variant?: 'circular' | 'rounded' | 'square'
  className?: string
}

const sizeMap = {
  sm: '32px',
  md: '40px',
  lg: '56px',
}

export function Avatar({
  src,
  alt,
  children,
  size = 'md',
  variant = 'circular',
  className,
}: AvatarProps) {
  const sizeValue = typeof size === 'number' ? `${size}px` : sizeMap[size]

  const borderRadiusMap = {
    circular: 'var(--radius-full)',
    rounded: 'var(--radius-md)',
    square: '0',
  }

  if (src) {
    return (
      <div
        style={{
          width: sizeValue,
          height: sizeValue,
          borderRadius: borderRadiusMap[variant],
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--color-bg-secondary)',
        }}
        className={clsx('avatar', `avatar-${variant}`, className)}
      >
        <img
          src={src}
          alt={alt || ''}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      </div>
    )
  }

  return (
    <div
      style={{
        width: sizeValue,
        height: sizeValue,
        borderRadius: borderRadiusMap[variant],
        background: 'var(--color-primary-main)',
        color: 'var(--color-primary-contrast-text)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: typeof size === 'number' ? `${size * 0.4}px` : size === 'sm' ? 'var(--font-size-sm)' : size === 'lg' ? 'var(--font-size-lg)' : 'var(--font-size-base)',
        fontWeight: 'var(--font-weight-medium)',
      }}
      className={clsx('avatar', `avatar-${variant}`, className)}
    >
      {children}
    </div>
  )
}
