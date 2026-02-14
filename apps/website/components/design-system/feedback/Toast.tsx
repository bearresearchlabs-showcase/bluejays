'use client'

import React from 'react'
import { Snackbar, SnackbarProps } from './Snackbar'

/**
 * Toast Component
 * Alias for Snackbar component
 */

export interface ToastProps extends SnackbarProps {}

export function Toast(props: ToastProps) {
  return <Snackbar {...props} />
}
