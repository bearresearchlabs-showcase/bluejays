'use client'

import React, { useState, useRef, useEffect } from 'react'
import { clsx } from '../utils'

/**
 * Popover Component
 * Popover component with anchor positioning
 */

export interface PopoverProps {
  anchorEl: HTMLElement | null
  open: boolean
  onClose: () => void
  children: React.ReactNode
  anchorOrigin?: {
    vertical: 'top' | 'bottom' | 'center'
    horizontal: 'left' | 'right' | 'center'
  }
  transformOrigin?: {
    vertical: 'top' | 'bottom' | 'center'
    horizontal: 'left' | 'right' | 'center'
  }
  className?: string
}

export function Popover({
  anchorEl,
  open,
  onClose,
  children,
  anchorOrigin = { vertical: 'bottom', horizontal: 'left' },
  transformOrigin = { vertical: 'top', horizontal: 'left' },
  className,
}: PopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open || !anchorEl || !popoverRef.current) return

    const updatePosition = () => {
      if (!anchorEl || !popoverRef.current) return

      const anchorRect = anchorEl.getBoundingClientRect()
      const popoverRect = popoverRef.current.getBoundingClientRect()

      let top = 0
      let left = 0

      if (anchorOrigin.vertical === 'bottom') {
        top = anchorRect.bottom + 8
      } else if (anchorOrigin.vertical === 'top') {
        top = anchorRect.top - popoverRect.height - 8
      } else {
        top = anchorRect.top + anchorRect.height / 2 - popoverRect.height / 2
      }

      if (anchorOrigin.horizontal === 'left') {
        left = anchorRect.left
      } else if (anchorOrigin.horizontal === 'right') {
        left = anchorRect.right - popoverRect.width
      } else {
        left = anchorRect.left + anchorRect.width / 2 - popoverRect.width / 2
      }

      popoverRef.current.style.top = `${top}px`
      popoverRef.current.style.left = `${left}px`
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
        popoverRef.current &&
        !popoverRef.current.contains(event.target as Node) &&
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
      ref={popoverRef}
      style={{
        position: 'fixed',
        background: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border-primary)',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-lg)',
        zIndex: 'var(--z-popover)',
        padding: 'var(--spacing-2)',
        maxWidth: '400px',
        maxHeight: '400px',
        overflowY: 'auto',
      }}
      className={clsx('popover', className)}
    >
      {children}
    </div>
  )
}
