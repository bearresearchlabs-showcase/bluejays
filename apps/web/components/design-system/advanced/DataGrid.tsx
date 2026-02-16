'use client'

import React, { useState, useMemo } from 'react'
import { Table, TableHead, TableBody, TableRow, TableCell, TablePagination } from '../data-display/Table'
import Checkbox from '../forms/Checkbox'
import { clsx } from '../utils'

/**
 * DataGrid Component
 * Basic data grid with sorting, filtering, and pagination
 */

export interface Column<T = any> {
  field: string
  headerName: string
  width?: number
  sortable?: boolean
  filterable?: boolean
  renderCell?: (value: any, row: T) => React.ReactNode
}

export interface DataGridProps<T = any> {
  rows: T[]
  columns: Column<T>[]
  pageSize?: number
  pageSizeOptions?: number[]
  checkboxSelection?: boolean
  onRowClick?: (row: T) => void
  className?: string
}

export function DataGrid<T extends Record<string, any>>({
  rows,
  columns,
  pageSize: initialPageSize = 10,
  pageSizeOptions = [5, 10, 25, 50],
  checkboxSelection = false,
  onRowClick,
  className,
}: DataGridProps<T>) {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(initialPageSize)
  const [sortField, setSortField] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())

  const sortedRows = useMemo(() => {
    if (!sortField) return rows

    return [...rows].sort((a, b) => {
      const aValue = a[sortField]
      const bValue = b[sortField]

      if (aValue === bValue) return 0

      const comparison = aValue < bValue ? -1 : 1
      return sortDirection === 'asc' ? comparison : -comparison
    })
  }, [rows, sortField, sortDirection])

  const paginatedRows = useMemo(() => {
    const start = page * rowsPerPage
    return sortedRows.slice(start, start + rowsPerPage)
  }, [sortedRows, page, rowsPerPage])

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedRows(new Set(paginatedRows.map((_, index) => page * rowsPerPage + index)))
    } else {
      setSelectedRows(new Set())
    }
  }

  const handleSelectRow = (index: number) => {
    const newSelected = new Set(selectedRows)
    const absoluteIndex = page * rowsPerPage + index

    if (newSelected.has(absoluteIndex)) {
      newSelected.delete(absoluteIndex)
    } else {
      newSelected.add(absoluteIndex)
    }

    setSelectedRows(newSelected)
  }

  const isAllSelected = paginatedRows.length > 0 && paginatedRows.every((_, index) => selectedRows.has(page * rowsPerPage + index))

  return (
    <div className={clsx('data-grid', className)}>
      <Table>
        <TableHead>
          <TableRow>
            {checkboxSelection && (
              <TableCell padding="checkbox">
                <Checkbox
                  checked={isAllSelected}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
              </TableCell>
            )}
            {columns.map((column) => (
              <TableCell
                key={column.field}
                component="th"
                onClick={() => column.sortable && handleSort(column.field)}
                style={{
                  cursor: column.sortable ? 'pointer' : 'default',
                  userSelect: 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
                  {column.headerName}
                  {column.sortable && sortField === column.field && (
                    <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {paginatedRows.map((row, index) => {
            const absoluteIndex = page * rowsPerPage + index
            const isSelected = selectedRows.has(absoluteIndex)

            return (
              <TableRow
                key={index}
                hover
                selected={isSelected}
                onClick={() => onRowClick?.(row)}
              >
                {checkboxSelection && (
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={isSelected}
                      onChange={() => handleSelectRow(index)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </TableCell>
                )}
                {columns.map((column) => (
                  <TableCell key={column.field}>
                    {column.renderCell
                      ? column.renderCell(row[column.field], row)
                      : String(row[column.field] ?? '')}
                  </TableCell>
                ))}
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
      <TablePagination
        count={rows.length}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={setPage}
        onRowsPerPageChange={setRowsPerPage}
        rowsPerPageOptions={pageSizeOptions}
      />
    </div>
  )
}
