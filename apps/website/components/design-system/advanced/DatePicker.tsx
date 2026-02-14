'use client'

import React, { useState, useRef, useEffect } from 'react'
import TextField from '../forms/TextField'
import { clsx } from '../utils'

/**
 * DatePicker Component
 * Date picker component (simplified implementation)
 */

export interface DatePickerProps {
  value?: Date | null
  onChange?: (date: Date | null) => void
  label?: string
  error?: boolean
  helperText?: string
  disabled?: boolean
  minDate?: Date
  maxDate?: Date
  className?: string
}

export function DatePicker({
  value,
  onChange,
  label,
  error,
  helperText,
  disabled,
  minDate,
  maxDate,
  className,
}: DatePickerProps) {
  const [open, setOpen] = useState(false)
  const [selectedDate, setSelectedDate] = useState<Date | null>(value || null)
  const pickerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setSelectedDate(value || null)
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

  const formatDate = (date: Date | null): string => {
    if (!date) return ''
    return date.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' })
  }

  const handleDateSelect = (year: number, month: number, day: number) => {
    const newDate = new Date(year, month, day)
    setSelectedDate(newDate)
    onChange?.(newDate)
    setOpen(false)
  }

  const currentDate = selectedDate || new Date()
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth()

  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate()
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1).getDay()

  const days = []
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push(null)
  }
  for (let day = 1; day <= daysInMonth; day++) {
    days.push(day)
  }

  return (
    <div ref={pickerRef} style={{ position: 'relative' }} className={clsx('date-picker', className)}>
      <TextField
        label={label}
        value={formatDate(selectedDate)}
        onClick={() => !disabled && setOpen(!open)}
        readOnly
        error={error}
        helperText={helperText}
        disabled={disabled}
        endAdornment={
          <span style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}>📅</span>
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
            minWidth: '280px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-4)' }}>
            <button
              onClick={() => {
                const newDate = new Date(currentYear, currentMonth - 1, 1)
                setSelectedDate(newDate)
              }}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: 'var(--spacing-2)',
              }}
            >
              ‹
            </button>
            <div style={{ fontWeight: 'var(--font-weight-medium)' }}>
              {new Date(currentYear, currentMonth).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </div>
            <button
              onClick={() => {
                const newDate = new Date(currentYear, currentMonth + 1, 1)
                setSelectedDate(newDate)
              }}
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: 'var(--spacing-2)',
              }}
            >
              ›
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 'var(--spacing-1)' }}>
            {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
              <div
                key={day}
                style={{
                  textAlign: 'center',
                  fontSize: 'var(--font-size-xs)',
                  fontWeight: 'var(--font-weight-medium)',
                  color: 'var(--color-text-secondary)',
                  padding: 'var(--spacing-2)',
                }}
              >
                {day}
              </div>
            ))}
            {days.map((day, index) => {
              if (day === null) {
                return <div key={`empty-${index}`} />
              }

              const isSelected =
                selectedDate &&
                selectedDate.getDate() === day &&
                selectedDate.getMonth() === currentMonth &&
                selectedDate.getFullYear() === currentYear

              const isDisabled =
                (minDate && new Date(currentYear, currentMonth, day) < minDate) ||
                (maxDate && new Date(currentYear, currentMonth, day) > maxDate)

              return (
                <button
                  key={day}
                  onClick={() => !isDisabled && handleDateSelect(currentYear, currentMonth, day)}
                  disabled={isDisabled}
                  style={{
                    background: isSelected ? 'var(--color-primary-main)' : 'transparent',
                    color: isSelected ? 'var(--color-primary-contrast-text)' : 'var(--color-text-primary)',
                    border: 'none',
                    borderRadius: 'var(--radius-sm)',
                    padding: 'var(--spacing-2)',
                    cursor: isDisabled ? 'not-allowed' : 'pointer',
                    opacity: isDisabled ? 0.3 : 1,
                    fontSize: 'var(--font-size-sm)',
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected && !isDisabled) {
                      e.currentTarget.style.background = 'var(--color-bg-secondary)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = 'transparent'
                    }
                  }}
                >
                  {day}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
