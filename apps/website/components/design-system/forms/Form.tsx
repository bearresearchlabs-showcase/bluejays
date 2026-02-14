'use client'

import React from 'react'
import { clsx } from '../utils'

/**
 * Form Component
 * Form container component
 */

export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode
  noValidate?: boolean
}

export function Form({ children, noValidate = false, className, onSubmit, ...props }: FormProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!noValidate) {
      const form = e.currentTarget
      if (form.checkValidity()) {
        onSubmit?.(e)
      } else {
        form.reportValidity()
      }
    } else {
      onSubmit?.(e)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate={noValidate}
      className={clsx('form', className)}
      {...props}
    >
      {children}
    </form>
  )
}
