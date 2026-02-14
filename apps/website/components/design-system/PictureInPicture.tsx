'use client'

import React, { useState, useEffect } from 'react'

/**
 * Picture-in-Picture Component
 * Persistent floating window for ongoing sessions.
 * Based on OpenAI Apps SDK UI guidelines.
 * 
 * When to use:
 * - Activities running in parallel with conversation
 * - Live collaboration or games
 * - Widgets that react to chat input
 */

interface PictureInPictureProps {
  title: string
  children: React.ReactNode
  onClose: () => void
  pinned?: boolean
  className?: string
}

export default function PictureInPicture({
  title,
  children,
  onClose,
  pinned = false,
  className = ''
}: PictureInPictureProps) {
  const [isPinned, setIsPinned] = useState(pinned)

  useEffect(() => {
    if (isPinned) {
      // Pin to top on scroll
      const handleScroll = () => {
        // PiP stays fixed when pinned
      }
      window.addEventListener('scroll', handleScroll)
      return () => window.removeEventListener('scroll', handleScroll)
    }
  }, [isPinned])

  return (
    <div
      className={`pip-widget ${className}`}
      style={{
        position: isPinned ? 'fixed' : 'relative',
        top: isPinned ? 'var(--spacing-4)' : 'auto',
        right: isPinned ? 'var(--spacing-4)' : 'auto',
        width: '320px',
        maxHeight: '480px',
        background: 'var(--color-bg-elevated)',
        border: '1px solid var(--color-border-primary)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-lg)',
        zIndex: isPinned ? 'var(--z-fixed)' : 'var(--z-base)',
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
          padding: 'var(--spacing-4)',
          borderBottom: '1px solid var(--color-border-primary)'
        }}
      >
        <h3 style={{
          fontSize: 'var(--font-size-base)',
          fontWeight: 'var(--font-weight-semibold)',
          color: 'var(--color-text-primary)',
          margin: 0
        }}>
          {title}
        </h3>
        <div style={{ display: 'flex', gap: 'var(--spacing-2)' }}>
          <button
            onClick={() => setIsPinned(!isPinned)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
              padding: 'var(--spacing-1)',
              fontSize: 'var(--font-size-sm)'
            }}
            aria-label={isPinned ? 'Unpin' : 'Pin'}
          >
            📌
          </button>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
              padding: 'var(--spacing-1)',
              fontSize: 'var(--font-size-lg)',
              lineHeight: 1
            }}
            aria-label="Close"
          >
            ×
          </button>
        </div>
      </div>
      
      {/* Content */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--spacing-4)'
        }}
      >
        {children}
      </div>
    </div>
  )
}
