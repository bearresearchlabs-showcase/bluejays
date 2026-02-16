'use client'

import React from 'react'
import { Dialog, DialogProps } from './Dialog'

/**
 * Modal Component
 * Alias for Dialog component (backward compatibility)
 */

export interface ModalProps extends DialogProps {}

export function Modal(props: ModalProps) {
  return <Dialog {...props} />
}
