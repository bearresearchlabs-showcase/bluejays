'use client'

import React, { useState, useRef, useEffect } from 'react'
import { clsx } from '../utils'

/**
 * Menu Component
 * Dropdown menu component
 */

export interface MenuItemProps {
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  divider?: boolean
  icon?: React.ReactNode
  className?: string
}

export function MenuItem({
  children,
  onClick,
  disabled = false,
  divider = false,
  icon,
  className,
}: MenuItemProps) {
  if (divider) {
    return (
      <div
        style={{
          height: '1px',
          background: 'var(--color-border-primary)',
          margin: 'var(--spacing-2) 0',
        }}
        className={clsx('menu-divider', className)}
      />
    )
  }

  return (
    <div
      onClick={() => !disabled && onClick?.()}
      style={{
        padding: 'var(--spacing-3) var(--spacing-4)',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        display: 'flex',
        alignItems: 'center',
        gap: icon ? 'var(--spacing-2)' : 0,
        fontSize: 'var(--font-size-sm)',
        color: 'var(--color-text-primary)',
        transition: 'background-color var(--transition-base)',
      }}
      className={clsx('menu-item', className)}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)'
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'transparent'
      }}
    >
      {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
      <span>{children}</span>
    </div>
  )
}

export interface MenuProps {
  anchorEl: HTMLElement | null
  open: boolean
  onClose: () => void
  children: React.ReactNode
  anchorOrigin?: {
    vertical: 'top' | 'bottom'
    horizontal: 'left' | 'right' | 'center'
  }
  transformOrigin?: {
    vertical: 'top' | 'bottom'
    horizontal: 'left' | 'right' | 'center'
  }
  className?: string
}

export function Menu({
  anchorEl,
  open,
  onClose,
  children,
  anchorOrigin = { vertical: 'bottom', horizontal: 'left' },
  transformOrigin = { vertical: 'top', horizontal: 'left' },
  className,
}: MenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open || !anchorEl || !menuRef.current) return

    const updatePosition = () => {
      if (!anchorEl || !menuRef.current) return

      const anchorRect = anchorEl.getBoundingClientRect()
      const menuRect = menuRef.current.getBoundingClientRect()

      let top = 0
      let left = 0

      if (anchorOrigin.vertical === 'bottom') {
        top = anchorRect.bottom + 4
      } else {
        top = anchorRect.top - menuRect.height - 4
      }

      if (anchorOrigin.horizontal === 'left') {
        left = anchorRect.left
      } else if (anchorOrigin.horizontal === 'right') {
        left = anchorRect.right - menuRect.width
      } else {
        left = anchorRect.left + (anchorRect.width - menuRect.width) / 2
      }

      menuRef.current.style.top = `${top}px`
      menuRef.current.style.left = `${left}px`
    }

    updatePosition()
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition, true)

    return () => {
      window.removeEventListener('resize', updatePosition)
      window.removeEventListener('scroll', updatePosition, true)
    }
  }, [open, anchorEl, anchorOrigin])

  useEffect(() => {
    if (!open) return

    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        anchorEl &&
        !anchorEl.contains(event.target as Node)
      ) {
        onClose()
      }
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [open, onClose, anchorEl])

  if (!open) return null

  return (
    <div
      ref={menuRef}
      style={{
        position: 'fixed',
        background: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border-primary)',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-lg)',
        zIndex: 'var(--z-menu)',
        minWidth: '160px',
        maxWidth: '320px',
        maxHeight: '400px',
        overflowY: 'auto',
      }}
      className={clsx('menu', className)}
    >
      {children}
    </div>
  )
}
