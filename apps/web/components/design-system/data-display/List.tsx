'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * List Component
 * List container component
 */

export interface ListProps {
  children: React.ReactNode
  dense?: boolean
  disablePadding?: boolean
  className?: string
}

export function List({ children, dense = false, disablePadding = false, className }: ListProps) {
  return (
    <ul
      style={{
        listStyle: 'none',
        padding: disablePadding ? 0 : 'var(--spacing-2) 0',
        margin: 0,
        fontSize: dense ? 'var(--font-size-sm)' : 'var(--font-size-base)',
      }}
      className={clsx('list', dense && 'list-dense', className)}
    >
      {children}
    </ul>
  )
}

export interface ListItemProps {
  children: React.ReactNode
  button?: boolean
  onClick?: () => void
  selected?: boolean
  className?: string
  style?: React.CSSProperties
}

export function ListItem({ children, button = false, onClick, selected = false, className, style }: ListItemProps) {
  return (
    <li
      onClick={button || onClick ? onClick : undefined}
      style={{
        padding: 'var(--spacing-3) var(--spacing-4)',
        cursor: button || onClick ? 'pointer' : 'default',
        background: selected ? 'var(--color-bg-secondary)' : 'transparent',
        transition: 'background-color var(--transition-base)',
        ...style,
      }}
      className={clsx('list-item', button && 'list-item-button', selected && 'list-item-selected', className)}
      onMouseEnter={(e) => {
        if ((button || onClick) && !selected) {
          e.currentTarget.style.backgroundColor = 'var(--color-bg-secondary)'
        }
      }}
      onMouseLeave={(e) => {
        if (!selected) {
          e.currentTarget.style.backgroundColor = 'transparent'
        }
      }}
    >
      {children}
    </li>
  )
}

export interface ListItemTextProps {
  primary: React.ReactNode
  secondary?: React.ReactNode
  className?: string
}

export function ListItemText({ primary, secondary, className }: ListItemTextProps) {
  return (
    <div className={clsx('list-item-text', className)}>
      <div
        style={{
          fontSize: 'var(--font-size-base)',
          color: 'var(--color-text-primary)',
          fontWeight: 'var(--font-weight-normal)',
        }}
      >
        {primary}
      </div>
      {secondary && (
        <div
          style={{
            fontSize: 'var(--font-size-sm)',
            color: 'var(--color-text-secondary)',
            marginTop: 'var(--spacing-1)',
          }}
        >
          {secondary}
        </div>
      )}
    </div>
  )
}

export interface ListItemIconProps {
  children: React.ReactNode
  className?: string
}

export function ListItemIcon({ children, className }: ListItemIconProps) {
  return (
    <div
      style={{
        marginRight: 'var(--spacing-3)',
        display: 'flex',
        alignItems: 'center',
        color: 'var(--color-text-secondary)',
      }}
      className={clsx('list-item-icon', className)}
    >
      {children}
    </div>
  )
}

export interface ListItemButtonProps {
  children: React.ReactNode
  onClick?: () => void
  selected?: boolean
  className?: string
  style?: React.CSSProperties
}

export function ListItemButton({ children, onClick, selected = false, className, style }: ListItemButtonProps) {
  return (
    <ListItem button onClick={onClick} selected={selected} className={className} style={style}>
      {children}
    </ListItem>
  )
}
