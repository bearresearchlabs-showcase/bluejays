'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Stepper Component
 * Step-by-step navigation component
 */

export interface Step {
  label: string
  description?: string
  icon?: React.ReactNode
  optional?: boolean
}

export interface StepperProps {
  steps: Step[]
  activeStep: number
  orientation?: 'horizontal' | 'vertical'
  alternativeLabel?: boolean
  className?: string
}

export function Stepper({
  steps,
  activeStep,
  orientation = 'horizontal',
  alternativeLabel = false,
  className,
}: StepperProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: orientation === 'vertical' ? 'column' : 'row',
        width: '100%',
      }}
      className={clsx('stepper', className)}
    >
      {steps.map((step, index) => {
        const isActive = index === activeStep
        const isCompleted = index < activeStep
        const isLast = index === steps.length - 1

        return (
          <React.Fragment key={index}>
            <div
              style={{
                display: 'flex',
                flexDirection: orientation === 'vertical' ? 'row' : 'column',
                alignItems: orientation === 'vertical' ? 'flex-start' : 'center',
                flex: orientation === 'horizontal' ? 1 : 'none',
                position: 'relative',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 'var(--spacing-2)',
                }}
              >
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: 'var(--radius-full)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: isCompleted
                      ? 'var(--color-success-main)'
                      : isActive
                      ? 'var(--color-primary-main)'
                      : 'var(--color-bg-secondary)',
                    color: isCompleted || isActive ? 'var(--color-bg-primary)' : 'var(--color-text-secondary)',
                    fontSize: 'var(--font-size-sm)',
                    fontWeight: 'var(--font-weight-medium)',
                    border: isActive ? '2px solid var(--color-primary-main)' : 'none',
                    transition: 'all var(--transition-base)',
                  }}
                >
                  {step.icon || (isCompleted ? '✓' : index + 1)}
                </div>
                {(!alternativeLabel || orientation === 'vertical') && (
                  <div
                    style={{
                      textAlign: 'center',
                      fontSize: 'var(--font-size-sm)',
                      fontWeight: isActive ? 'var(--font-weight-medium)' : 'var(--font-weight-normal)',
                      color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                    }}
                  >
                    {step.label}
                  </div>
                )}
                {step.description && orientation === 'vertical' && (
                  <div
                    style={{
                      fontSize: 'var(--font-size-xs)',
                      color: 'var(--color-text-tertiary)',
                      marginTop: 'var(--spacing-1)',
                    }}
                  >
                    {step.description}
                  </div>
                )}
              </div>
              {orientation === 'horizontal' && alternativeLabel && (
                <div
                  style={{
                    marginTop: 'var(--spacing-2)',
                    textAlign: 'center',
                    fontSize: 'var(--font-size-sm)',
                    fontWeight: isActive ? 'var(--font-weight-medium)' : 'var(--font-weight-normal)',
                    color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                  }}
                >
                  {step.label}
                </div>
              )}
            </div>
            {!isLast && (
              <div
                style={{
                  flex: orientation === 'horizontal' ? 1 : 'none',
                  height: orientation === 'horizontal' ? '2px' : '40px',
                  width: orientation === 'horizontal' ? 'auto' : '2px',
                  background: isCompleted
                    ? 'var(--color-success-main)'
                    : 'var(--color-border-primary)',
                  margin: orientation === 'horizontal' ? '0 var(--spacing-2)' : 'var(--spacing-2) 0',
                  alignSelf: orientation === 'horizontal' ? 'center' : 'stretch',
                  transition: 'background-color var(--transition-base)',
                }}
              />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}
