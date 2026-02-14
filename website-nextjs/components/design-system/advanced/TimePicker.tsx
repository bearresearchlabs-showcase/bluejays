'use client'

import React, { useState, useRef, useEffect } from 'react'
import TextField from '../forms/TextField'
import { clsx } from '../utils'

/**
 * TimePicker Component
 * Time picker component (simplified implementation)
 */

export interface TimePickerProps {
  value?: Date | null
  onChange?: (date: Date | null) => void
  label?: string
  error?: boolean
  helperText?: string
  disabled?: boolean
  className?: string
}

export function TimePicker({
  value,
  onChange,
  label,
  error,
  helperText,
  disabled,
  className,
}: TimePickerProps) {
  const [open, setOpen] = useState(false)
  const [selectedTime, setSelectedTime] = useState<Date | null>(value || null)
  const pickerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setSelectedTime(value || null)
  }, [value])

  useEffect(() => {
    if (!open) return

    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  const formatTime = (date: Date | null): string => {
    if (!date) return ''
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
  }

  const handleTimeSelect = (hours: number, minutes: number) => {
    const newDate = selectedTime ? new Date(selectedTime) : new Date()
    newDate.setHours(hours)
    newDate.setMinutes(minutes)
    setSelectedTime(newDate)
    onChange?.(newDate)
    setOpen(false)
  }

  const currentHours = selectedTime ? selectedTime.getHours() : 12
  const currentMinutes = selectedTime ? selectedTime.getMinutes() : 0

  return (
    <div ref={pickerRef} style={{ position: 'relative' }} className={clsx('time-picker', className)}>
      <TextField
        label={label}
        value={formatTime(selectedTime)}
        onClick={() => !disabled && setOpen(!open)}
        readOnly
        error={error}
        helperText={helperText}
        disabled={disabled}
        endAdornment={
          <span style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}>🕐</span>
        }
      />
      {open && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            marginTop: 'var(--spacing-2)',
            background: 'var(--color-bg-elevated)',
            border: '1px solid var(--color-border-primary)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-lg)',
            padding: 'var(--spacing-4)',
            zIndex: 'var(--z-popover)',
            minWidth: '200px',
          }}
        >
          <div style={{ display: 'flex', gap: 'var(--spacing-4)', justifyContent: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--spacing-2)' }}>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>Hours</div>
              <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-1)' }}>
                {Array.from({ length: 24 }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => handleTimeSelect(i, currentMinutes)}
                    style={{
                      background: currentHours === i ? 'var(--color-primary-main)' : 'transparent',
                      color: currentHours === i ? 'var(--color-primary-contrast-text)' : 'var(--color-text-primary)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: 'var(--spacing-2)',
                      cursor: 'pointer',
                      fontSize: 'var(--font-size-sm)',
                      minWidth: '40px',
                    }}
                  >
                    {i.toString().padStart(2, '0')}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--spacing-2)' }}>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-secondary)' }}>Minutes</div>
              <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-1)' }}>
                {Array.from({ length: 60 }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => handleTimeSelect(currentHours, i)}
                    style={{
                      background: currentMinutes === i ? 'var(--color-primary-main)' : 'transparent',
                      color: currentMinutes === i ? 'var(--color-primary-contrast-text)' : 'var(--color-text-primary)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: 'var(--spacing-2)',
                      cursor: 'pointer',
                      fontSize: 'var(--font-size-sm)',
                      minWidth: '40px',
                    }}
                  >
                    {i.toString().padStart(2, '0')}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
