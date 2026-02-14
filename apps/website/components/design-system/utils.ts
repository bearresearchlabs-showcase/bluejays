/**
 * Design System Utility Functions
 * Helper functions for theme manipulation, class names, and utilities
 */

import { Theme, ThemeOptions, Breakpoint } from './types'

/**
 * Class name utility (like clsx)
 */
export function clsx(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}

/**
 * Get contrast text color for a background color
 */
export function getContrastText(backgroundColor: string): string {
  // Simple contrast calculation - can be enhanced with proper color math
  const rgb = hexToRgb(backgroundColor)
  if (!rgb) return '#000000'
  
  const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255
  return luminance > 0.5 ? '#000000' : '#ffffff'
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null
}

/**
 * Darken a color by a percentage
 */
export function darken(color: string, amount: number): string {
  const rgb = hexToRgb(color)
  if (!rgb) return color
  
  const factor = 1 - amount / 100
  return `rgb(${Math.round(rgb.r * factor)}, ${Math.round(rgb.g * factor)}, ${Math.round(rgb.b * factor)})`
}

/**
 * Lighten a color by a percentage
 */
export function lighten(color: string, amount: number): string {
  const rgb = hexToRgb(color)
  if (!rgb) return color
  
  const factor = 1 + amount / 100
  return `rgb(${Math.min(255, Math.round(rgb.r * factor))}, ${Math.min(255, Math.round(rgb.g * factor))}, ${Math.min(255, Math.round(rgb.b * factor))})`
}

/**
 * Create a theme from options
 */
export function createTheme(options: ThemeOptions = {}): Theme {
  const defaultTheme: Theme = {
    palette: {
      primary: {
        main: '#000000',
        light: '#1f2937',
        dark: '#000000',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#6b7280',
        light: '#9ca3af',
        dark: '#4b5563',
        contrastText: '#ffffff',
      },
      error: {
        main: '#ef4444',
        light: '#f87171',
        dark: '#dc2626',
        contrastText: '#ffffff',
      },
      warning: {
        main: '#f59e0b',
        light: '#fbbf24',
        dark: '#d97706',
        contrastText: '#000000',
      },
      info: {
        main: '#3b82f6',
        light: '#60a5fa',
        dark: '#2563eb',
        contrastText: '#ffffff',
      },
      success: {
        main: '#10b981',
        light: '#34d399',
        dark: '#059669',
        contrastText: '#ffffff',
      },
      text: {
        primary: '#000000',
        secondary: '#6b7280',
        tertiary: '#9ca3af',
        disabled: '#d1d5db',
      },
      background: {
        primary: '#ffffff',
        secondary: '#f9fafb',
        tertiary: '#f3f4f6',
        elevated: '#ffffff',
      },
      border: {
        primary: '#e5e7eb',
        secondary: '#d1d5db',
        focus: '#000000',
      },
    },
    typography: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      fontFamilyMono: 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace',
      h1: { fontSize: '2.25rem', fontWeight: 600, lineHeight: 1.25 },
      h2: { fontSize: '1.875rem', fontWeight: 600, lineHeight: 1.25 },
      h3: { fontSize: '1.5rem', fontWeight: 600, lineHeight: 1.25 },
      h4: { fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.25 },
      h5: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.5 },
      h6: { fontSize: '1rem', fontWeight: 600, lineHeight: 1.5 },
      body1: { fontSize: '1rem', fontWeight: 400, lineHeight: 1.5 },
      body2: { fontSize: '0.875rem', fontWeight: 400, lineHeight: 1.5 },
      button: { fontSize: '0.875rem', fontWeight: 500, lineHeight: 1.5 },
      caption: { fontSize: '0.75rem', fontWeight: 400, lineHeight: 1.5 },
      overline: { fontSize: '0.75rem', fontWeight: 500, lineHeight: 1.5 },
    },
    spacing: {
      0: '0',
      1: '0.25rem',
      2: '0.5rem',
      3: '0.75rem',
      4: '1rem',
      5: '1.25rem',
      6: '1.5rem',
      7: '1.75rem',
      8: '2rem',
      9: '2.25rem',
      10: '2.5rem',
      11: '2.75rem',
      12: '3rem',
      14: '3.5rem',
      16: '4rem',
      20: '5rem',
      24: '6rem',
    },
    breakpoints: {
      xs: 0,
      sm: 600,
      md: 900,
      lg: 1200,
      xl: 1536,
    },
    zIndex: {
      mobileStepper: 1000,
      speedDial: 1050,
      appBar: 1100,
      drawer: 1200,
      modal: 1300,
      snackbar: 1400,
      tooltip: 1500,
    },
    shadows: {
      0: 'none',
      1: '0px 2px 1px -1px rgba(0,0,0,0.2), 0px 1px 1px 0px rgba(0,0,0,0.14), 0px 1px 3px 0px rgba(0,0,0,0.12)',
      2: '0px 3px 1px -2px rgba(0,0,0,0.2), 0px 2px 2px 0px rgba(0,0,0,0.14), 0px 1px 5px 0px rgba(0,0,0,0.12)',
      3: '0px 3px 3px -2px rgba(0,0,0,0.2), 0px 3px 4px 0px rgba(0,0,0,0.14), 0px 1px 8px 0px rgba(0,0,0,0.12)',
      4: '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
      5: '0px 3px 5px -1px rgba(0,0,0,0.2), 0px 5px 8px 0px rgba(0,0,0,0.14), 0px 1px 14px 0px rgba(0,0,0,0.12)',
      6: '0px 3px 5px -1px rgba(0,0,0,0.2), 0px 6px 10px 0px rgba(0,0,0,0.14), 0px 1px 18px 0px rgba(0,0,0,0.12)',
      8: '0px 5px 5px -3px rgba(0,0,0,0.2), 0px 8px 10px 1px rgba(0,0,0,0.14), 0px 3px 14px 2px rgba(0,0,0,0.12)',
      12: '0px 7px 8px -4px rgba(0,0,0,0.2), 0px 12px 17px 2px rgba(0,0,0,0.14), 0px 5px 22px 4px rgba(0,0,0,0.12)',
      16: '0px 8px 10px -5px rgba(0,0,0,0.2), 0px 16px 24px 2px rgba(0,0,0,0.14), 0px 6px 30px 5px rgba(0,0,0,0.12)',
      24: '0px 11px 15px -7px rgba(0,0,0,0.2), 0px 24px 38px 3px rgba(0,0,0,0.14), 0px 9px 46px 8px rgba(0,0,0,0.12)',
    },
    transitions: {
      easing: {
        easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
        easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
        sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
      },
      duration: {
        shortest: 150,
        shorter: 200,
        short: 250,
        standard: 300,
        complex: 375,
        enteringScreen: 225,
        leavingScreen: 195,
      },
    },
  }

  // Deep merge options with default theme
  return deepMerge(defaultTheme, options) as Theme
}

/**
 * Deep merge utility
 */
function deepMerge<T>(target: T, source: Partial<T>): T {
  const output = { ...target }
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach((key) => {
      const sourceValue = source[key as keyof T]
      const targetValue = target[key as keyof T]
      
      if (isObject(sourceValue) && isObject(targetValue)) {
        output[key as keyof T] = deepMerge(targetValue, sourceValue as Partial<typeof targetValue>) as T[keyof T]
      } else {
        output[key as keyof T] = sourceValue as T[keyof T]
      }
    })
  }
  
  return output
}

function isObject(item: any): item is Record<string, any> {
  return item && typeof item === 'object' && !Array.isArray(item)
}

/**
 * Get spacing value from theme
 */
export function spacing(theme: Theme, value: number): string {
  return theme.spacing[value] || `${value * 0.25}rem`
}
