'use client'

import React from 'react'

/**
 * Inline Card Component
 * Lightweight, single-purpose widgets embedded directly in conversation.
 * Based on OpenAI Apps SDK UI guidelines.
 * 
 * When to use:
 * - A single action or decision
 * - Small amounts of structured data
 * - A fully self-contained widget or tool
 */

interface InlineCardProps {
  title?: string
  children: React.ReactNode
  expandable?: boolean
  onExpand?: () => void
  actions?: Array<{
    label: string
    onClick: () => void
    primary?: boolean
  }>
  className?: string
}

export default function InlineCard({
  title,
  children,
  expandable = false,
  onExpand,
  actions = [],
  className = ''
}: InlineCardProps) {
  return (
    <div
      className={`inline-card ${className}`}
      style={{
        background: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border-primary)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--card-padding)',
        marginBottom: 'var(--spacing-4)',
        maxWidth: '100%',
        transition: 'all var(--transition-base)'
      }}
    >
      {title && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 'var(--spacing-4)'
          }}
        >
          <h3 style={{
            fontSize: 'var(--font-size-lg)',
            fontWeight: 'var(--font-weight-semibold)',
            color: 'var(--color-text-primary)',
            margin: 0
          }}>
            {title}
          </h3>
          {expandable && onExpand && (
            <button
              onClick={onExpand}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--color-text-secondary)',
                cursor: 'pointer',
                padding: 'var(--spacing-2)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-medium)'
              }}
            >
              Expand →
            </button>
          )}
        </div>
      )}
      
      <div style={{ color: 'var(--color-text-primary)' }}>
        {children}
      </div>
      
      {actions.length > 0 && (
        <div
          style={{
            display: 'flex',
            gap: 'var(--spacing-3)',
            marginTop: 'var(--spacing-6)',
            paddingTop: 'var(--spacing-4)',
            borderTop: '1px solid var(--color-border-primary)'
          }}
        >
          {actions.slice(0, 2).map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              style={{
                flex: action.primary ? '1' : '0 1 auto',
                padding: 'var(--spacing-3) var(--spacing-5)',
                background: action.primary
                  ? 'var(--color-accent-primary)'
                  : 'transparent',
                color: action.primary
                  ? 'var(--color-bg-primary)'
                  : 'var(--color-accent-primary)',
                border: action.primary
                  ? 'none'
                  : '1px solid var(--color-border-primary)',
                borderRadius: 'var(--radius-md)',
                fontSize: 'var(--font-size-sm)',
                fontWeight: 'var(--font-weight-medium)',
                cursor: 'pointer',
                transition: 'all var(--transition-base)'
              }}
              onMouseEnter={(e) => {
                if (action.primary) {
                  e.currentTarget.style.background = 'var(--color-accent-primary-hover)'
                } else {
                  e.currentTarget.style.borderColor = 'var(--color-accent-primary)'
                }
              }}
              onMouseLeave={(e) => {
                if (action.primary) {
                  e.currentTarget.style.background = 'var(--color-accent-primary)'
                } else {
                  e.currentTarget.style.borderColor = 'var(--color-border-primary)'
                }
              }}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
