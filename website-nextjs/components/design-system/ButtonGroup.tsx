'use client'

import React from 'react'
import Button, { ButtonProps } from './Button'
import { clsx } from './utils'

/**
 * ButtonGroup Component
 * Group of buttons displayed together
 */

export interface ButtonGroupProps {
  children: React.ReactElement<ButtonProps>[]
  orientation?: 'horizontal' | 'vertical'
  variant?: 'outlined' | 'text' | 'contained'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  className?: string
}

export function ButtonGroup({
  children,
  orientation = 'horizontal',
  variant = 'outlined',
  size = 'md',
  fullWidth = false,
  className,
}: ButtonGroupProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: orientation === 'vertical' ? 'column' : 'row',
        width: fullWidth ? '100%' : 'auto',
      }}
      className={clsx('button-group', className)}
    >
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child

        const isFirst = index === 0
        const isLast = index === children.length - 1

        const borderRadius = {
          horizontal: {
            first: 'var(--radius-md) 0 0 var(--radius-md)',
            middle: '0',
            last: '0 var(--radius-md) var(--radius-md) 0',
          },
          vertical: {
            first: 'var(--radius-md) var(--radius-md) 0 0',
            middle: '0',
            last: '0 0 var(--radius-md) var(--radius-md)',
          },
        }

        return React.cloneElement(child, {
          ...child.props,
          size,
          variant: variant === 'contained' ? 'primary' : variant === 'outlined' ? 'secondary' : 'ghost',
          style: {
            ...child.props.style,
            borderRadius: isFirst
              ? borderRadius[orientation].first
              : isLast
              ? borderRadius[orientation].last
              : borderRadius[orientation].middle,
            borderRightWidth: orientation === 'horizontal' && !isLast ? 0 : undefined,
            borderBottomWidth: orientation === 'vertical' && !isLast ? 0 : undefined,
          },
        })
      })}
    </div>
  )
}
