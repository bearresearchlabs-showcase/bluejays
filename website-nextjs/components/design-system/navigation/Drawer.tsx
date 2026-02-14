'use client'

import React, { useEffect } from 'react'
import { clsx } from '../utils'

/**
 * Drawer Component
 * Side navigation drawer component
 */

export interface DrawerProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  anchor?: 'left' | 'right' | 'top' | 'bottom'
  variant?: 'permanent' | 'persistent' | 'temporary'
  width?: string | number
  className?: string
}

export function Drawer({
  open,
  onClose,
  children,
  anchor = 'left',
  variant = 'temporary',
  width = 280,
  className,
}: DrawerProps) {
  useEffect(() => {
    if (variant === 'temporary' && open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [open, variant])

  const widthValue = typeof width === 'number' ? `${width}px` : width

  const anchorStyles = {
    left: {
      left: 0,
      top: 0,
      bottom: 0,
      width: widthValue,
      transform: variant === 'temporary' && !open ? 'translateX(-100%)' : 'translateX(0)',
    },
    right: {
      right: 0,
      top: 0,
      bottom: 0,
      width: widthValue,
      transform: variant === 'temporary' && !open ? 'translateX(100%)' : 'translateX(0)',
    },
    top: {
      top: 0,
      left: 0,
      right: 0,
      height: widthValue,
      transform: variant === 'temporary' && !open ? 'translateY(-100%)' : 'translateY(0)',
    },
    bottom: {
      bottom: 0,
      left: 0,
      right: 0,
      height: widthValue,
      transform: variant === 'temporary' && !open ? 'translateY(100%)' : 'translateY(0)',
    },
  }

  if (variant === 'permanent') {
    return (
      <aside
        style={{
          position: 'fixed',
          ...anchorStyles[anchor],
          background: 'var(--color-bg-elevated)',
          borderRight: anchor === 'left' ? '1px solid var(--color-border-primary)' : 'none',
          borderLeft: anchor === 'right' ? '1px solid var(--color-border-primary)' : 'none',
          borderBottom: anchor === 'top' ? '1px solid var(--color-border-primary)' : 'none',
          borderTop: anchor === 'bottom' ? '1px solid var(--color-border-primary)' : 'none',
          zIndex: 'var(--z-drawer)',
          overflowY: 'auto',
          transition: 'transform var(--transition-base)',
        }}
        className={clsx('drawer', `drawer-${anchor}`, className)}
      >
        {children}
      </aside>
    )
  }

  return (
    <>
      {variant === 'temporary' && open && (
        <div
          onClick={onClose}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            zIndex: 'var(--z-modal-backdrop)',
            transition: 'opacity var(--transition-base)',
          }}
          className="drawer-backdrop"
        />
      )}
      <aside
        style={{
          position: 'fixed',
          ...anchorStyles[anchor],
          background: 'var(--color-bg-elevated)',
          borderRight: anchor === 'left' ? '1px solid var(--color-border-primary)' : 'none',
          borderLeft: anchor === 'right' ? '1px solid var(--color-border-primary)' : 'none',
          borderBottom: anchor === 'top' ? '1px solid var(--color-border-primary)' : 'none',
          borderTop: anchor === 'bottom' ? '1px solid var(--color-border-primary)' : 'none',
          boxShadow: variant === 'temporary' ? 'var(--shadow-lg)' : 'none',
          zIndex: 'var(--z-drawer)',
          overflowY: 'auto',
          transition: 'transform var(--transition-base)',
        }}
        className={clsx('drawer', `drawer-${anchor}`, className)}
      >
        {children}
      </aside>
    </>
  )
}
