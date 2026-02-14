'use client'

import React, { createContext, useContext, useState, useMemo, ReactNode } from 'react'
import { Theme, ThemeOptions, createTheme } from './utils'

interface ThemeContextValue {
  theme: Theme
  setTheme: (theme: ThemeOptions) => void
  toggleDarkMode: () => void
  isDarkMode: boolean
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
  theme?: ThemeOptions
  defaultDarkMode?: boolean
}

export function ThemeProvider({ 
  children, 
  theme: themeOptions,
  defaultDarkMode = false 
}: ThemeProviderProps) {
  const [isDarkMode, setIsDarkMode] = useState(defaultDarkMode)
  const [customTheme, setCustomTheme] = useState<ThemeOptions | undefined>(themeOptions)

  const theme = useMemo(() => {
    const baseTheme = createTheme(customTheme)
    
    if (isDarkMode) {
      // Apply dark mode overrides
      return createTheme({
        ...customTheme,
        palette: {
          ...baseTheme.palette,
          text: {
            primary: '#ffffff',
            secondary: '#9ca3af',
            tertiary: '#6b7280',
            disabled: '#4b5563',
          },
          background: {
            primary: '#000000',
            secondary: '#111827',
            tertiary: '#1f2937',
            elevated: '#111827',
          },
          border: {
            primary: '#374151',
            secondary: '#4b5563',
            focus: '#ffffff',
          },
        },
      })
    }
    
    return baseTheme
  }, [customTheme, isDarkMode])

  const setTheme = (newTheme: ThemeOptions) => {
    setCustomTheme((prev) => ({ ...prev, ...newTheme }))
  }

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev)
  }

  const value: ThemeContextValue = useMemo(
    () => ({
      theme,
      setTheme,
      toggleDarkMode,
      isDarkMode,
    }),
    [theme, isDarkMode]
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

/**
 * Hook to check if current breakpoint matches
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  React.useEffect(() => {
    const media = window.matchMedia(query)
    if (media.matches !== matches) {
      setMatches(media.matches)
    }
    
    const listener = () => setMatches(media.matches)
    media.addEventListener('change', listener)
    return () => media.removeEventListener('change', listener)
  }, [matches, query])

  return matches
}

/**
 * Hook to get current breakpoint
 */
export function useBreakpoint(): 'xs' | 'sm' | 'md' | 'lg' | 'xl' {
  const isXs = useMediaQuery('(max-width: 599px)')
  const isSm = useMediaQuery('(min-width: 600px) and (max-width: 899px)')
  const isMd = useMediaQuery('(min-width: 900px) and (max-width: 1199px)')
  const isLg = useMediaQuery('(min-width: 1200px) and (max-width: 1535px)')
  const isXl = useMediaQuery('(min-width: 1536px)')

  if (isXl) return 'xl'
  if (isLg) return 'lg'
  if (isMd) return 'md'
  if (isSm) return 'sm'
  return 'xs'
}
