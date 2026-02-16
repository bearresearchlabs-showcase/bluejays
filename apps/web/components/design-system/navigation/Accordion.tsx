'use client'

import React, { useState } from 'react'
import { clsx } from '../utils'

/**
 * Accordion Component
 * Expandable/collapsible content sections
 */

export interface AccordionProps {
  children: React.ReactNode
  defaultExpanded?: boolean
  expanded?: boolean
  onChange?: (expanded: boolean) => void
  disabled?: boolean
  className?: string
}

export function Accordion({
  children,
  defaultExpanded = false,
  expanded: controlledExpanded,
  onChange,
  disabled = false,
  className,
}: AccordionProps) {
  const [uncontrolledExpanded, setUncontrolledExpanded] = useState(defaultExpanded)
  const isControlled = controlledExpanded !== undefined
  const expanded = isControlled ? controlledExpanded : uncontrolledExpanded

  const handleToggle = () => {
    if (disabled) return
    const newExpanded = !expanded
    if (!isControlled) {
      setUncontrolledExpanded(newExpanded)
    }
    onChange?.(newExpanded)
  }

  return (
    <div
      style={{
        border: '1px solid var(--color-border-primary)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        marginBottom: 'var(--spacing-2)',
      }}
      className={clsx('accordion', className)}
    >
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            expanded,
            onToggle: handleToggle,
            disabled,
          })
        }
        return child
      })}
    </div>
  )
}

export interface AccordionSummaryProps {
  children: React.ReactNode
  expandIcon?: React.ReactNode
  expanded?: boolean
  onToggle?: () => void
  disabled?: boolean
  className?: string
}

export function AccordionSummary({
  children,
  expandIcon,
  expanded = false,
  onToggle,
  disabled = false,
  className,
}: AccordionSummaryProps) {
  return (
    <div
      onClick={onToggle}
      style={{
        padding: 'var(--spacing-4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        cursor: disabled ? 'not-allowed' : 'pointer',
        background: expanded ? 'var(--color-bg-secondary)' : 'var(--color-bg-primary)',
        transition: 'all var(--transition-base)',
        userSelect: 'none',
      }}
      className={clsx('accordion-summary', className)}
    >
      <div style={{ flex: 1 }}>{children}</div>
      <div
        style={{
          marginLeft: 'var(--spacing-2)',
          transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform var(--transition-base)',
          fontSize: 'var(--font-size-sm)',
          color: 'var(--color-text-secondary)',
        }}
      >
        {expandIcon || '▼'}
      </div>
    </div>
  )
}

export interface AccordionDetailsProps {
  children: React.ReactNode
  expanded?: boolean
  className?: string
}

export function AccordionDetails({ children, expanded = false, className }: AccordionDetailsProps) {
  return (
    <div
      style={{
        padding: expanded ? 'var(--spacing-4)' : '0 var(--spacing-4)',
        maxHeight: expanded ? '1000px' : '0',
        overflow: 'hidden',
        transition: 'all var(--transition-base)',
        borderTop: expanded ? '1px solid var(--color-border-primary)' : 'none',
      }}
      className={clsx('accordion-details', className)}
    >
      {children}
    </div>
  )
}
