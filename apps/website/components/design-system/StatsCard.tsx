'use client'

import React from 'react'
import { clsx } from './utils'

/**
 * Stats Card Component
 * Display key metrics and statistics.
 * Enhanced with variants, chart integration, and improved trend visualization.
 * Based on OpenAI Apps SDK UI guidelines.
 */

export interface StatsCardProps {
  value: string | number
  label: string
  trend?: {
    value: number
    direction: 'up' | 'down'
    label?: string
  }
  variant?: 'default' | 'elevated' | 'outlined' | 'filled'
  icon?: React.ReactNode
  chart?: React.ReactNode
  className?: string
}

export default function StatsCard({
  value,
  label,
  trend,
  variant = 'default',
  icon,
  chart,
  className = ''
}: StatsCardProps) {
  const variantStyles = {
    default: {
      background: 'var(--color-bg-elevated)',
      border: '1px solid var(--color-border-primary)',
      boxShadow: 'none'
    },
    elevated: {
      background: 'var(--color-bg-elevated)',
      border: 'none',
      boxShadow: 'var(--elevation-2)'
    },
    outlined: {
      background: 'transparent',
      border: '1px solid var(--color-border-primary)',
      boxShadow: 'none'
    },
    filled: {
      background: 'var(--color-bg-secondary)',
      border: 'none',
      boxShadow: 'none'
    }
  }

  return (
    <div
      className={clsx('stats-card', `stats-card-${variant}`, className)}
      style={{
        ...variantStyles[variant],
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--spacing-6)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--spacing-3)',
        transition: 'all var(--transition-base)'
      }}
      onMouseEnter={(e) => {
        if (variant === 'default' || variant === 'outlined') {
          e.currentTarget.style.boxShadow = 'var(--elevation-2)'
        }
      }}
      onMouseLeave={(e) => {
        if (variant === 'default' || variant === 'outlined') {
          e.currentTarget.style.boxShadow = 'none'
        }
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: 'var(--font-size-xs)',
              color: 'var(--color-text-secondary)',
              fontWeight: 'var(--font-weight-medium)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: 'var(--spacing-2)'
            }}
          >
            {label}
          </div>
          <div
            style={{
              fontSize: 'var(--font-size-3xl)',
              fontWeight: 'var(--font-weight-semibold)',
              color: 'var(--color-text-primary)',
              lineHeight: 'var(--line-height-tight)',
              display: 'flex',
              alignItems: 'baseline',
              gap: 'var(--spacing-2)'
            }}
          >
            {value}
            {trend && (
              <span
                style={{
                  fontSize: 'var(--font-size-sm)',
                  fontWeight: 'var(--font-weight-medium)',
                  color: trend.direction === 'up' ? 'var(--color-success-main)' : 'var(--color-error-main)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-1)'
                }}
              >
                <span>{trend.direction === 'up' ? '↑' : '↓'}</span>
                <span>{Math.abs(trend.value)}%</span>
                {trend.label && (
                  <span style={{ fontSize: 'var(--font-size-xs)', opacity: 0.8 }}>
                    {trend.label}
                  </span>
                )}
              </span>
            )}
          </div>
        </div>
        {icon && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '48px',
              height: '48px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-bg-secondary)',
              color: 'var(--color-text-secondary)'
            }}
          >
            {icon}
          </div>
        )}
      </div>
      {chart && (
        <div style={{ marginTop: 'var(--spacing-2)' }}>
          {chart}
        </div>
      )}
    </div>
  )
}
