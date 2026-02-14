'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Table Component
 * Data table component with sorting and selection
 */

export interface TableProps {
  children: React.ReactNode
  stickyHeader?: boolean
  size?: 'small' | 'medium'
  className?: string
}

export function Table({ children, stickyHeader = false, size = 'medium', className }: TableProps) {
  return (
    <div
      style={{
        width: '100%',
        overflowX: 'auto',
      }}
      className={clsx('table-wrapper', className)}
    >
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: size === 'small' ? 'var(--font-size-sm)' : 'var(--font-size-base)',
        }}
        className={clsx('table', `table-${size}`, className)}
      >
        {children}
      </table>
    </div>
  )
}

export interface TableHeadProps {
  children: React.ReactNode
  className?: string
}

export function TableHead({ children, className }: TableHeadProps) {
  return (
    <thead
      style={{
        background: 'var(--color-bg-secondary)',
      }}
      className={clsx('table-head', className)}
    >
      {children}
    </thead>
  )
}

export interface TableBodyProps {
  children: React.ReactNode
  className?: string
}

export function TableBody({ children, className }: TableBodyProps) {
  return (
    <tbody className={clsx('table-body', className)}>
      {children}
    </tbody>
  )
}

export interface TableRowProps {
  children: React.ReactNode
  hover?: boolean
  selected?: boolean
  onClick?: () => void
  className?: string
}

export function TableRow({ children, hover = false, selected = false, onClick, className }: TableRowProps) {
  return (
    <tr
      onClick={onClick}
      style={{
        borderBottom: '1px solid var(--color-border-primary)',
        background: selected ? 'var(--color-bg-secondary)' : 'transparent',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'background-color var(--transition-base)',
      }}
      className={clsx('table-row', hover && 'table-row-hover', selected && 'table-row-selected', className)}
      onMouseEnter={(e) => {
        if (hover && !selected) {
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
    </tr>
  )
}

export interface TableCellProps {
  children: React.ReactNode
  align?: 'left' | 'center' | 'right'
  padding?: 'none' | 'normal' | 'checkbox'
  component?: 'th' | 'td'
  className?: string
}

export function TableCell({
  children,
  align = 'left',
  padding = 'normal',
  component = 'td',
  className,
}: TableCellProps) {
  const Component = component

  const paddingStyles = {
    none: { padding: 0 },
    normal: { padding: 'var(--spacing-3) var(--spacing-4)' },
    checkbox: { padding: 'var(--spacing-1)' },
  }

  return (
    <Component
      style={{
        textAlign: align,
        ...paddingStyles[padding],
        fontWeight: component === 'th' ? 'var(--font-weight-medium)' : 'var(--font-weight-normal)',
      }}
      className={clsx('table-cell', className)}
    >
      {children}
    </Component>
  )
}

export interface TablePaginationProps {
  count: number
  page: number
  rowsPerPage: number
  onPageChange: (page: number) => void
  onRowsPerPageChange?: (rowsPerPage: number) => void
  rowsPerPageOptions?: number[]
  className?: string
}

export function TablePagination({
  count,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  rowsPerPageOptions = [5, 10, 25, 50],
  className,
}: TablePaginationProps) {
  const totalPages = Math.ceil(count / rowsPerPage)

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 'var(--spacing-3) var(--spacing-4)',
        borderTop: '1px solid var(--color-border-primary)',
      }}
      className={clsx('table-pagination', className)}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
        <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
          Rows per page:
        </span>
        {onRowsPerPageChange && (
          <select
            value={rowsPerPage}
            onChange={(e) => onRowsPerPageChange(Number(e.target.value))}
            style={{
              padding: 'var(--spacing-1) var(--spacing-2)',
              border: '1px solid var(--color-border-primary)',
              borderRadius: 'var(--radius-sm)',
              fontSize: 'var(--font-size-sm)',
            }}
          >
            {rowsPerPageOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
        <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
          {page * rowsPerPage + 1}-{Math.min((page + 1) * rowsPerPage, count)} of {count}
        </span>
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 0}
          style={{
            padding: 'var(--spacing-1) var(--spacing-2)',
            border: '1px solid var(--color-border-primary)',
            borderRadius: 'var(--radius-sm)',
            background: 'transparent',
            cursor: page === 0 ? 'not-allowed' : 'pointer',
            opacity: page === 0 ? 0.5 : 1,
          }}
        >
          ‹
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages - 1}
          style={{
            padding: 'var(--spacing-1) var(--spacing-2)',
            border: '1px solid var(--color-border-primary)',
            borderRadius: 'var(--radius-sm)',
            background: 'transparent',
            cursor: page >= totalPages - 1 ? 'not-allowed' : 'pointer',
            opacity: page >= totalPages - 1 ? 0.5 : 1,
          }}
        >
          ›
        </button>
      </div>
    </div>
  )
}
