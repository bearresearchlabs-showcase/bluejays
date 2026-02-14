'use client'

import React, { useState } from 'react'
import { DatePicker } from './DatePicker'
import { TimePicker } from './TimePicker'
import { Stack } from '../layout/Stack'
import { clsx } from '../utils'

/**
 * DateTimePicker Component
 * Combined date and time picker
 */

export interface DateTimePickerProps {
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

export function DateTimePicker({
  value,
  onChange,
  label,
  error,
  helperText,
  disabled,
  minDate,
  maxDate,
  className,
}: DateTimePickerProps) {
  const [selectedDate, setSelectedDate] = useState<Date | null>(value || null)

  const handleDateChange = (date: Date | null) => {
    if (date) {
      const newDate = selectedDate ? new Date(selectedDate) : new Date()
      newDate.setFullYear(date.getFullYear())
      newDate.setMonth(date.getMonth())
      newDate.setDate(date.getDate())
      setSelectedDate(newDate)
      onChange?.(newDate)
    } else {
      setSelectedDate(null)
      onChange?.(null)
    }
  }

  const handleTimeChange = (date: Date | null) => {
    if (date) {
      const newDate = selectedDate ? new Date(selectedDate) : new Date()
      newDate.setHours(date.getHours())
      newDate.setMinutes(date.getMinutes())
      newDate.setSeconds(date.getSeconds())
      setSelectedDate(newDate)
      onChange?.(newDate)
    }
  }

  return (
    <Stack direction="row" spacing={2} className={clsx('date-time-picker', className)}>
      <DatePicker
        value={selectedDate}
        onChange={handleDateChange}
        label={label ? `${label} (Date)` : 'Date'}
        error={error}
        disabled={disabled}
        minDate={minDate}
        maxDate={maxDate}
      />
      <TimePicker
        value={selectedDate}
        onChange={handleTimeChange}
        label={label ? `${label} (Time)` : 'Time'}
        error={error}
        disabled={disabled}
      />
    </Stack>
  )
}
