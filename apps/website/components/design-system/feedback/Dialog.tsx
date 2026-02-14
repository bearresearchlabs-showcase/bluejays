'use client'

import React, { useEffect, useRef } from 'react'
import { clsx } from '../utils'

/**
 * Dialog Component
 * Modal dialog component
 */

export interface DialogProps {
  open: boolean
  onClose: () => void
  children: React.ReactNode
  fullWidth?: boolean
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false
  fullScreen?: boolean
  className?: string
}

const maxWidthMap = {
  xs: '444px',
  sm: '600px',
  md: '900px',
  lg: '1200px',
  xl: '1536px',
}

export function Dialog({
  open,
  onClose,
  children,
  fullWidth = false,
  maxWidth = 'sm',
  fullScreen = false,
  className,
}: DialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
      
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose()
        }
      }

      document.addEventListener('keydown', handleEscape)
      return () => {
        document.removeEventListener('keydown', handleEscape)
        document.body.style.overflow = ''
      }
    }
  }, [open, onClose])

  useEffect(() => {
    if (open && dialogRef.current) {
      const focusableElements = dialogRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements[0] as HTMLElement
      firstElement?.focus()
    }
  }, [open])

  if (!open) return null

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          zIndex: 'var(--z-modal-backdrop)',
          animation: 'fadeIn 200ms ease-in-out',
        }}
        className="dialog-backdrop"
      />
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 'var(--z-modal)',
          padding: 'var(--spacing-4)',
          pointerEvents: 'none',
        }}
      >
        <div
          ref={dialogRef}
          onClick={(e) => e.stopPropagation()}
          style={{
            background: 'var(--color-bg-elevated)',
            borderRadius: fullScreen ? 0 : 'var(--radius-lg)',
            boxShadow: 'var(--elevation-24)',
            width: fullScreen ? '100%' : fullWidth ? '100%' : 'auto',
            maxWidth: fullScreen ? 'none' : maxWidth === false ? 'none' : maxWidthMap[maxWidth],
            maxHeight: fullScreen ? '100%' : '90vh',
            display: 'flex',
            flexDirection: 'column',
            pointerEvents: 'auto',
            animation: 'slideUp 200ms ease-out',
          }}
          className={clsx('dialog', className)}
          role="dialog"
          aria-modal="true"
        >
          {children}
        </div>
      </div>
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  )
}

export interface DialogTitleProps {
  children: React.ReactNode
  onClose?: () => void
  className?: string
}

export function DialogTitle({ children, onClose, className }: DialogTitleProps) {
  return (
    <div
      style={{
        padding: 'var(--spacing-6)',
        borderBottom: '1px solid var(--color-border-primary)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
      className={clsx('dialog-title', className)}
    >
      <h2
        style={{
          fontSize: 'var(--font-size-xl)',
          fontWeight: 'var(--font-weight-semibold)',
          color: 'var(--color-text-primary)',
          margin: 0,
        }}
      >
        {children}
      </h2>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            padding: 'var(--spacing-2)',
            color: 'var(--color-text-secondary)',
            fontSize: 'var(--font-size-xl)',
            lineHeight: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-label="Close dialog"
        >
          ×
        </button>
      )}
    </div>
  )
}

export interface DialogContentProps {
  children: React.ReactNode
  dividers?: boolean
  className?: string
}

export function DialogContent({ children, dividers = false, className }: DialogContentProps) {
  return (
    <div
      style={{
        padding: 'var(--spacing-6)',
        overflowY: 'auto',
        flex: 1,
        borderTop: dividers ? '1px solid var(--color-border-primary)' : 'none',
        borderBottom: dividers ? '1px solid var(--color-border-primary)' : 'none',
      }}
      className={clsx('dialog-content', className)}
    >
      {children}
    </div>
  )
}

export interface DialogActionsProps {
  children: React.ReactNode
  className?: string
}

export function DialogActions({ children, className }: DialogActionsProps) {
  return (
    <div
      style={{
        padding: 'var(--spacing-4) var(--spacing-6)',
        borderTop: '1px solid var(--color-border-primary)',
        display: 'flex',
        justifyContent: 'flex-end',
        gap: 'var(--spacing-2)',
      }}
      className={clsx('dialog-actions', className)}
    >
      {children}
    </div>
  )
}
