'use client'

import React, { useEffect, useState } from 'react'
import { Alert, AlertProps } from './Alert'
import { clsx } from '../utils'

/**
 * Snackbar Component
 * Temporary notification component
 */

export interface SnackbarProps extends Omit<AlertProps, 'onClose'> {
  open: boolean
  onClose?: () => void
  autoHideDuration?: number
  anchorOrigin?: {
    vertical: 'top' | 'bottom'
    horizontal: 'left' | 'right' | 'center'
  }
  className?: string
}

export function Snackbar({
  open,
  onClose,
  autoHideDuration = 6000,
  anchorOrigin = { vertical: 'bottom', horizontal: 'center' },
  children,
  className,
  ...alertProps
}: SnackbarProps) {
  const [isVisible, setIsVisible] = useState(open)

  useEffect(() => {
    if (open) {
      setIsVisible(true)
      
      if (autoHideDuration > 0) {
        const timer = setTimeout(() => {
          setIsVisible(false)
          setTimeout(() => {
            onClose?.()
          }, 300) // Wait for exit animation
        }, autoHideDuration)

        return () => clearTimeout(timer)
      }
    } else {
      setIsVisible(false)
    }
  }, [open, autoHideDuration, onClose])

  if (!open && !isVisible) return null

  const positionStyles: React.CSSProperties = {
    position: 'fixed',
    zIndex: 'var(--z-snackbar)',
    [anchorOrigin.vertical]: 'var(--spacing-4)',
    [anchorOrigin.horizontal === 'left' ? 'left' : anchorOrigin.horizontal === 'right' ? 'right' : 'left']:
      anchorOrigin.horizontal === 'center' ? '50%' : 'var(--spacing-4)',
    transform: isVisible
      ? anchorOrigin.horizontal === 'center'
        ? 'translateX(-50%)'
        : 'none'
      : anchorOrigin.horizontal === 'center'
      ? 'translateX(-50%) translateY(20px)'
      : 'translateY(20px)',
    transition: 'opacity 300ms ease-in-out, transform 300ms ease-in-out',
    opacity: isVisible ? 1 : 0,
  }

  return (
    <div style={positionStyles} className={clsx('snackbar', className)}>
      <Alert {...alertProps} onClose={onClose}>
        {children}
      </Alert>
    </div>
  )
}
