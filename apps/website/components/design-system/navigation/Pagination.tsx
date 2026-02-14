'use client'

import React from 'react'
import { clsx } from '../utils'
import Button from '../Button'

/**
 * Pagination Component
 * Page navigation component
 */

export interface PaginationProps {
  page: number
  count: number
  onChange: (page: number) => void
  showFirstButton?: boolean
  showLastButton?: boolean
  siblingCount?: number
  boundaryCount?: number
  disabled?: boolean
  className?: string
}

export function Pagination({
  page,
  count,
  onChange,
  showFirstButton = false,
  showLastButton = false,
  siblingCount = 1,
  boundaryCount = 1,
  disabled = false,
  className,
}: PaginationProps) {
  const handleChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= count && !disabled) {
      onChange(newPage)
    }
  }

  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    const totalNumbers = siblingCount * 2 + 5
    const totalBlocks = totalNumbers + 2

    if (count <= totalBlocks) {
      for (let i = 1; i <= count; i++) {
        pages.push(i)
      }
      return pages
    }

    const startPages = []
    const endPages = []

    for (let i = 1; i <= boundaryCount; i++) {
      startPages.push(i)
    }

    for (let i = count - boundaryCount + 1; i <= count; i++) {
      endPages.push(i)
    }

    const siblingsStart = Math.max(
      boundaryCount + 1,
      page - siblingCount
    )
    const siblingsEnd = Math.min(
      count - boundaryCount,
      page + siblingCount
    )

    pages.push(...startPages)

    if (siblingsStart > boundaryCount + 1) {
      pages.push('...')
    }

    for (let i = siblingsStart; i <= siblingsEnd; i++) {
      pages.push(i)
    }

    if (siblingsEnd < count - boundaryCount) {
      pages.push('...')
    }

    pages.push(...endPages)

    return pages
  }

  const pageNumbers = getPageNumbers()

  return (
    <nav
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-1)',
      }}
      className={clsx('pagination', className)}
      aria-label="Pagination"
    >
      {showFirstButton && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleChange(1)}
          disabled={disabled || page === 1}
          aria-label="First page"
        >
          ««
        </Button>
      )}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleChange(page - 1)}
        disabled={disabled || page === 1}
        aria-label="Previous page"
      >
        ‹
      </Button>
      {pageNumbers.map((pageNum, index) => {
        if (pageNum === '...') {
          return (
            <span
              key={`ellipsis-${index}`}
              style={{
                padding: 'var(--spacing-2) var(--spacing-3)',
                color: 'var(--color-text-secondary)',
              }}
            >
              ...
            </span>
          )
        }

        const pageNumber = pageNum as number
        const isSelected = pageNumber === page

        return (
          <Button
            key={pageNumber}
            variant={isSelected ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => handleChange(pageNumber)}
            disabled={disabled}
            aria-label={`Page ${pageNumber}`}
            aria-current={isSelected ? 'page' : undefined}
          >
            {pageNumber}
          </Button>
        )
      })}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleChange(page + 1)}
        disabled={disabled || page === count}
        aria-label="Next page"
      >
        ›
      </Button>
      {showLastButton && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleChange(count)}
          disabled={disabled || page === count}
          aria-label="Last page"
        >
          »»
        </Button>
      )}
    </nav>
  )
}
