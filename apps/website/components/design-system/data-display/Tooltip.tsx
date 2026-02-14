'use client'

import React, { useState, useRef, useEffect } from 'react'
import { clsx } from '../utils'

/**
 * Tooltip Component
 * Tooltip component with positioning
 */

export interface TooltipProps {
  title: string
  children: React.ReactElement
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'top-start' | 'top-end' | 'bottom-start' | 'bottom-end' | 'left-start' | 'left-end' | 'right-start' | 'right-end'
  arrow?: boolean
  enterDelay?: number
  leaveDelay?: number
  className?: string
}

export function Tooltip({
  title,
  children,
  placement = 'bottom',
  arrow = false,
  enterDelay = 0,
  leaveDelay = 0,
  className,
}: TooltipProps) {
  const [open, setOpen] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const triggerRef = useRef<HTMLElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  let enterTimer: NodeJS.Timeout
  let leaveTimer: NodeJS.Timeout

  const updatePosition = () => {
    if (!triggerRef.current || !tooltipRef.current) return

    const triggerRect = triggerRef.current.getBoundingClientRect()
    const tooltipRect = tooltipRef.current.getBoundingClientRect()

    let top = 0
    let left = 0

    const [vertical, horizontal] = placement.split('-')
    const mainPlacement = vertical as 'top' | 'bottom' | 'left' | 'right'
    const subPlacement = horizontal as 'start' | 'end' | undefined

    switch (mainPlacement) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - 8
        left = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2
        if (subPlacement === 'start') left = triggerRect.left
        if (subPlacement === 'end') left = triggerRect.right - tooltipRect.width
        break
      case 'bottom':
        top = triggerRect.bottom + 8
        left = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2
        if (subPlacement === 'start') left = triggerRect.left
        if (subPlacement === 'end') left = triggerRect.right - tooltipRect.width
        break
      case 'left':
        left = triggerRect.left - tooltipRect.width - 8
        top = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
        if (subPlacement === 'start') top = triggerRect.top
        if (subPlacement === 'end') top = triggerRect.bottom - tooltipRect.height
        break
      case 'right':
        left = triggerRect.right + 8
        top = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
        if (subPlacement === 'start') top = triggerRect.top
        if (subPlacement === 'end') top = triggerRect.bottom - tooltipRect.height
        break
    }

    setPosition({ top, left })
  }

  useEffect(() => {
    if (open) {
      updatePosition()
      window.addEventListener('scroll', updatePosition, true)
      window.addEventListener('resize', updatePosition)
    }
    return () => {
      window.removeEventListener('scroll', updatePosition, true)
      window.removeEventListener('resize', updatePosition)
    }
  }, [open])

  const handleMouseEnter = () => {
    clearTimeout(leaveTimer)
    enterTimer = setTimeout(() => {
      setOpen(true)
    }, enterDelay)
  }

  const handleMouseLeave = () => {
    clearTimeout(enterTimer)
    leaveTimer = setTimeout(() => {
      setOpen(false)
    }, leaveDelay)
  }

  return (
    <>
      {React.cloneElement(children, {
        ref: triggerRef,
        onMouseEnter: handleMouseEnter,
        onMouseLeave: handleMouseLeave,
      })}
      {open && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            top: `${position.top}px`,
            left: `${position.left}px`,
            background: 'rgba(0, 0, 0, 0.87)',
            color: '#ffffff',
            padding: 'var(--spacing-2) var(--spacing-3)',
            borderRadius: 'var(--radius-sm)',
            fontSize: 'var(--font-size-xs)',
            zIndex: 'var(--z-tooltip)',
            pointerEvents: 'none',
            whiteSpace: 'nowrap',
            maxWidth: '200px',
            wordWrap: 'break-word',
            whiteSpace: 'normal',
          }}
          className={clsx('tooltip', className)}
          role="tooltip"
        >
          {title}
        </div>
      )}
    </>
  )
}
