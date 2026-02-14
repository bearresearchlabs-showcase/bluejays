'use client'

import React, { useState, createContext, useContext } from 'react'
import { clsx } from '../utils'

/**
 * Tabs Component
 * Tab navigation component
 */

interface TabsContextValue {
  value: string | number
  onChange: (value: string | number) => void
  orientation: 'horizontal' | 'vertical'
  variant: 'standard' | 'scrollable' | 'fullWidth'
}

const TabsContext = createContext<TabsContextValue | undefined>(undefined)

function useTabsContext() {
  const context = useContext(TabsContext)
  if (!context) {
    throw new Error('Tabs components must be used within Tabs')
  }
  return context
}

export interface TabItem {
  value: string | number
  label: string
  icon?: React.ReactNode
  disabled?: boolean
}

export interface TabsProps {
  children: React.ReactNode
  value?: string | number
  defaultValue?: string | number
  onChange?: (value: string | number) => void
  orientation?: 'horizontal' | 'vertical'
  variant?: 'standard' | 'scrollable' | 'fullWidth'
  className?: string
}

export function Tabs({
  children,
  value: controlledValue,
  defaultValue,
  onChange: onChangeProp,
  orientation = 'horizontal',
  variant = 'standard',
  className,
}: TabsProps) {
  const [uncontrolledValue, setUncontrolledValue] = useState<string | number | undefined>(defaultValue)
  const isControlled = controlledValue !== undefined
  const value = isControlled ? controlledValue : uncontrolledValue

  const onChange = (newValue: string | number) => {
    if (!isControlled) {
      setUncontrolledValue(newValue)
    }
    onChangeProp?.(newValue)
  }

  return (
    <TabsContext.Provider value={{ value: value || '', onChange, orientation, variant }}>
      <div
        style={{
          display: 'flex',
          flexDirection: orientation === 'vertical' ? 'row' : 'column',
          width: '100%',
        }}
        className={clsx('tabs', className)}
      >
        {children}
      </div>
    </TabsContext.Provider>
  )
}

export interface TabListProps {
  children: React.ReactNode
  className?: string
}

export function TabList({ children, className }: TabListProps) {
  const { orientation, variant } = useTabsContext()

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: orientation === 'vertical' ? 'column' : 'row',
        borderBottom: orientation === 'horizontal' && variant !== 'fullWidth' ? '1px solid var(--color-border-primary)' : 'none',
        borderRight: orientation === 'vertical' ? '1px solid var(--color-border-primary)' : 'none',
        gap: variant === 'fullWidth' ? 0 : 'var(--spacing-2)',
        overflowX: variant === 'scrollable' ? 'auto' : 'visible',
      }}
      className={clsx('tab-list', className)}
    >
      {children}
    </div>
  )
}

export interface TabProps {
  value: string | number
  label?: string
  icon?: React.ReactNode
  disabled?: boolean
  className?: string
}

export function Tab({ value, label, icon, disabled = false, className }: TabProps) {
  const { value: selectedValue, onChange, orientation, variant } = useTabsContext()
  const isSelected = selectedValue === value

  return (
    <button
      onClick={() => !disabled && onChange(value)}
      disabled={disabled}
      style={{
        padding: 'var(--spacing-3) var(--spacing-4)',
        border: 'none',
        background: 'transparent',
        color: isSelected ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
        fontSize: 'var(--font-size-sm)',
        fontWeight: isSelected ? 'var(--font-weight-medium)' : 'var(--font-weight-normal)',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        borderBottom: orientation === 'horizontal' && isSelected ? '2px solid var(--color-accent-primary)' : 'none',
        borderRight: orientation === 'vertical' && isSelected ? '2px solid var(--color-accent-primary)' : 'none',
        flex: variant === 'fullWidth' ? 1 : 'none',
        display: 'flex',
        alignItems: 'center',
        gap: icon ? 'var(--spacing-2)' : 0,
        justifyContent: 'center',
        transition: 'all var(--transition-base)',
        whiteSpace: 'nowrap',
      }}
      className={clsx('tab', isSelected && 'tab-selected', className)}
      onMouseEnter={(e) => {
        if (!disabled && !isSelected) {
          e.currentTarget.style.color = 'var(--color-text-primary)'
        }
      }}
      onMouseLeave={(e) => {
        if (!isSelected) {
          e.currentTarget.style.color = 'var(--color-text-secondary)'
        }
      }}
    >
      {icon && <span>{icon}</span>}
      {label && <span>{label}</span>}
    </button>
  )
}

export interface TabPanelProps {
  value: string | number
  children: React.ReactNode
  className?: string
}

export function TabPanel({ value, children, className }: TabPanelProps) {
  const { value: selectedValue } = useTabsContext()
  const isSelected = selectedValue === value

  if (!isSelected) {
    return null
  }

  return (
    <div
      style={{
        padding: 'var(--spacing-4)',
        display: isSelected ? 'block' : 'none',
      }}
      className={clsx('tab-panel', className)}
    >
      {children}
    </div>
  )
}
