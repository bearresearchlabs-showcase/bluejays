'use client'

import React, { forwardRef, useState } from 'react'
import { clsx } from '../utils'

/**
 * Slider Component
 * Range slider input component
 */

export interface SliderProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'size'> {
  label?: string
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
  marks?: boolean | Array<{ value: number; label?: string }>
  valueLabelDisplay?: 'auto' | 'on' | 'off'
  orientation?: 'horizontal' | 'vertical'
  step?: number
  min?: number
  max?: number
}

const Slider = forwardRef<HTMLInputElement, SliderProps>(
  (
    {
      label,
      size = 'md',
      color = 'primary',
      marks = false,
      valueLabelDisplay = 'auto',
      orientation = 'horizontal',
      step = 1,
      min = 0,
      max = 100,
      className,
      value,
      onChange,
      disabled,
      ...props
    },
    ref
  ) => {
    const [localValue, setLocalValue] = useState<number>(
      typeof value === 'number' ? value : Number(value) || min
    )

    const currentValue = typeof value === 'number' ? value : localValue

    const sizeStyles = {
      sm: { height: '4px' },
      md: { height: '6px' },
      lg: { height: '8px' },
    }

    const colorStyles = {
      primary: 'var(--color-primary-main)',
      secondary: 'var(--color-secondary-main)',
      error: 'var(--color-error-main)',
      warning: 'var(--color-warning-main)',
      info: 'var(--color-info-main)',
      success: 'var(--color-success-main)',
    }

    const percentage = ((currentValue - min) / (max - min)) * 100

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = Number(e.target.value)
      setLocalValue(newValue)
      onChange?.(e)
    }

    const showValueLabel = valueLabelDisplay === 'on' || (valueLabelDisplay === 'auto' && currentValue !== min && currentValue !== max)

    return (
      <div
        style={{
          width: orientation === 'horizontal' ? '100%' : 'auto',
          height: orientation === 'vertical' ? '200px' : 'auto',
          display: 'flex',
          flexDirection: orientation === 'vertical' ? 'column' : 'row',
          alignItems: 'center',
          gap: 'var(--spacing-2)',
        }}
      >
        {label && (
          <label
            style={{
              fontSize: 'var(--font-size-sm)',
              fontWeight: 'var(--font-weight-medium)',
              color: disabled ? 'var(--color-text-disabled)' : 'var(--color-text-primary)',
              minWidth: orientation === 'horizontal' ? '80px' : 'auto',
            }}
          >
            {label}
          </label>
        )}
        <div
          style={{
            flex: 1,
            position: 'relative',
            width: orientation === 'horizontal' ? '100%' : 'auto',
            height: orientation === 'vertical' ? '100%' : 'auto',
            display: 'flex',
            flexDirection: orientation === 'vertical' ? 'column' : 'row',
            alignItems: 'center',
          }}
        >
          <div
            style={{
              position: 'relative',
              width: orientation === 'horizontal' ? '100%' : 'auto',
              height: orientation === 'vertical' ? '100%' : 'auto',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <input
              ref={ref}
              type="range"
              min={min}
              max={max}
              step={step}
              value={currentValue}
              onChange={handleChange}
              disabled={disabled}
              style={{
                width: orientation === 'horizontal' ? '100%' : 'auto',
                height: orientation === 'vertical' ? '100%' : sizeStyles[size].height,
                ...sizeStyles[size],
                cursor: disabled ? 'not-allowed' : 'pointer',
                opacity: disabled ? 0.5 : 1,
                accentColor: colorStyles[color],
                WebkitAppearance: 'none',
                appearance: 'none',
                background: 'transparent',
              }}
              className={clsx('slider', className)}
              {...props}
            />
            {showValueLabel && (
              <div
                style={{
                  position: 'absolute',
                  left: orientation === 'horizontal' ? `${percentage}%` : '50%',
                  top: orientation === 'vertical' ? `${100 - percentage}%` : 'auto',
                  transform: orientation === 'horizontal' ? 'translateX(-50%)' : 'translate(-50%, 50%)',
                  marginTop: orientation === 'horizontal' ? 'var(--spacing-4)' : 0,
                  marginLeft: orientation === 'vertical' ? 'var(--spacing-4)' : 0,
                  padding: 'var(--spacing-1) var(--spacing-2)',
                  background: 'var(--color-bg-elevated)',
                  border: '1px solid var(--color-border-primary)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-text-primary)',
                  whiteSpace: 'nowrap',
                  zIndex: 1,
                }}
              >
                {currentValue}
              </div>
            )}
          </div>
          {marks && (
            <div
              style={{
                position: 'absolute',
                width: orientation === 'horizontal' ? '100%' : 'auto',
                height: orientation === 'vertical' ? '100%' : 'auto',
                pointerEvents: 'none',
                display: 'flex',
                flexDirection: orientation === 'vertical' ? 'column' : 'row',
                justifyContent: 'space-between',
              }}
            >
              {Array.isArray(marks)
                ? marks.map((mark, index) => (
                    <div
                      key={index}
                      style={{
                        position: 'absolute',
                        left: orientation === 'horizontal' ? `${((mark.value - min) / (max - min)) * 100}%` : '50%',
                        top: orientation === 'vertical' ? `${100 - ((mark.value - min) / (max - min)) * 100}%` : 'auto',
                        transform: orientation === 'horizontal' ? 'translateX(-50%)' : 'translate(-50%, 50%)',
                        width: '4px',
                        height: '4px',
                        background: 'var(--color-text-secondary)',
                        borderRadius: 'var(--radius-full)',
                        marginTop: orientation === 'horizontal' ? 'var(--spacing-2)' : 0,
                      }}
                    />
                  ))
                : [min, max].map((val, index) => (
                    <div
                      key={index}
                      style={{
                        position: 'absolute',
                        left: orientation === 'horizontal' ? `${index * 100}%` : '50%',
                        top: orientation === 'vertical' ? `${100 - index * 100}%` : 'auto',
                        transform: orientation === 'horizontal' ? 'translateX(-50%)' : 'translate(-50%, 50%)',
                        width: '4px',
                        height: '4px',
                        background: 'var(--color-text-secondary)',
                        borderRadius: 'var(--radius-full)',
                        marginTop: orientation === 'horizontal' ? 'var(--spacing-2)' : 0,
                      }}
                    />
                  ))}
            </div>
          )}
        </div>
      </div>
    )
  }
)

Slider.displayName = 'Slider'

export default Slider
