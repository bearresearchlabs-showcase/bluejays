'use client'

import React from 'react'

/**
 * Fullscreen View Component
 * Immersive experiences for multi-step workflows or deeper exploration.
 * Based on OpenAI Apps SDK UI guidelines.
 * 
 * When to use:
 * - Rich tasks that cannot be reduced to a single card
 * - Browsing detailed content
 * - Interactive diagrams or maps
 */

interface FullscreenViewProps {
  title: string
  children: React.ReactNode
  onClose: () => void
  className?: string
}

export default function FullscreenView({
  title,
  children,
  onClose,
  className = ''
}: FullscreenViewProps) {
  return (
    <div
      className={`fullscreen-view ${className}`}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'var(--color-bg-primary)',
        zIndex: 'var(--z-modal)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: 'var(--spacing-6)',
          borderBottom: '1px solid var(--color-border-primary)'
        }}
      >
        <h2 style={{
          fontSize: 'var(--font-size-2xl)',
          fontWeight: 'var(--font-weight-semibold)',
          color: 'var(--color-text-primary)',
          margin: 0
        }}>
          {title}
        </h2>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--color-text-secondary)',
            cursor: 'pointer',
            padding: 'var(--spacing-2)',
            fontSize: 'var(--font-size-lg)',
            lineHeight: 1
          }}
          aria-label="Close"
        >
          ×
        </button>
      </div>
      
      {/* Content */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--spacing-6)'
        }}
      >
        {children}
      </div>
    </div>
  )
}
