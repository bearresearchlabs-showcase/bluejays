'use client'

import React, { createContext, useContext } from 'react'
import { clsx } from '../utils'

/**
 * FormControl Component
 * Context provider for form control state
 */

interface FormControlContextValue {
  error?: boolean
  disabled?: boolean
  required?: boolean
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
}

const FormControlContext = createContext<FormControlContextValue | undefined>(undefined)

export function useFormControl(): FormControlContextValue {
  const context = useContext(FormControlContext)
  return context || {}
}

export interface FormControlProps {
  children: React.ReactNode
  error?: boolean
  disabled?: boolean
  required?: boolean
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  className?: string
}

export function FormControl({
  children,
  error = false,
  disabled = false,
  required = false,
  size = 'md',
  fullWidth = false,
  className,
}: FormControlProps) {
  const contextValue: FormControlContextValue = {
    error,
    disabled,
    required,
    size,
    fullWidth,
  }

  return (
    <FormControlContext.Provider value={contextValue}>
      <div
        style={{
          width: fullWidth ? '100%' : 'auto',
        }}
        className={clsx('form-control', className)}
      >
        {children}
      </div>
    </FormControlContext.Provider>
  )
}
