'use client'

import React from 'react'
import Link from 'next/link'
import { clsx } from '../utils'

/**
 * Breadcrumbs Component
 * Navigation breadcrumb trail
 */

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: React.ReactNode
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  separator?: React.ReactNode
  maxItems?: number
  className?: string
  style?: React.CSSProperties
}

export function Breadcrumbs({
  items,
  separator = '/',
  maxItems,
  className,
  style,
}: BreadcrumbsProps) {
  const displayItems = maxItems && items.length > maxItems
    ? [
        items[0],
        { label: '...', href: undefined },
        ...items.slice(-(maxItems - 1)),
      ]
    : items

  return (
    <nav
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-2)',
        fontSize: 'var(--font-size-sm)',
        ...style,
      }}
      className={clsx('breadcrumbs', className)}
      aria-label="Breadcrumb"
    >
      {displayItems.map((item, index) => {
        const isLast = index === displayItems.length - 1

        return (
          <React.Fragment key={index}>
            {index > 0 && (
              <span
                style={{
                  color: 'var(--color-text-tertiary)',
                  margin: '0 var(--spacing-1)',
                }}
                aria-hidden="true"
              >
                {separator}
              </span>
            )}
            {item.href && !isLast ? (
              <Link
                href={item.href}
                style={{
                  color: 'var(--color-text-secondary)',
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: item.icon ? 'var(--spacing-1)' : 0,
                  transition: 'color var(--transition-base)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = 'var(--color-text-primary)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = 'var(--color-text-secondary)'
                }}
              >
                {item.icon && <span>{item.icon}</span>}
                <span>{item.label}</span>
              </Link>
            ) : (
              <span
                style={{
                  color: isLast ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                  fontWeight: isLast ? 'var(--font-weight-medium)' : 'var(--font-weight-normal)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: item.icon ? 'var(--spacing-1)' : 0,
                }}
                aria-current={isLast ? 'page' : undefined}
              >
                {item.icon && <span>{item.icon}</span>}
                <span>{item.label}</span>
              </span>
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}
