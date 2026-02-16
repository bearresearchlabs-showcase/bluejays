/**
 * Design System TypeScript Types
 * Type definitions for theme, components, and utilities
 */

export interface Theme {
  palette: {
    primary: {
      main: string
      light: string
      dark: string
      contrastText: string
    }
    secondary: {
      main: string
      light: string
      dark: string
      contrastText: string
    }
    error: {
      main: string
      light: string
      dark: string
      contrastText: string
    }
    warning: {
      main: string
      light: string
      dark: string
      contrastText: string
    }
    info: {
      main: string
      light: string
      dark: string
      contrastText: string
    }
    success: {
      main: string
      light: string
      dark: string
      contrastText: string
    }
    text: {
      primary: string
      secondary: string
      tertiary: string
      disabled: string
    }
    background: {
      primary: string
      secondary: string
      tertiary: string
      elevated: string
    }
    border: {
      primary: string
      secondary: string
      focus: string
    }
  }
  typography: {
    fontFamily: string
    fontFamilyMono: string
    h1: TypographyVariant
    h2: TypographyVariant
    h3: TypographyVariant
    h4: TypographyVariant
    h5: TypographyVariant
    h6: TypographyVariant
    body1: TypographyVariant
    body2: TypographyVariant
    button: TypographyVariant
    caption: TypographyVariant
    overline: TypographyVariant
  }
  spacing: {
    [key: number]: string
  }
  breakpoints: {
    xs: number
    sm: number
    md: number
    lg: number
    xl: number
  }
  zIndex: {
    mobileStepper: number
    speedDial: number
    appBar: number
    drawer: number
    modal: number
    snackbar: number
    tooltip: number
  }
  shadows: {
    [key: number]: string
  }
  transitions: {
    easing: {
      easeInOut: string
      easeOut: string
      easeIn: string
      sharp: string
    }
    duration: {
      shortest: number
      shorter: number
      short: number
      standard: number
      complex: number
      enteringScreen: number
      leavingScreen: number
    }
  }
}

export interface TypographyVariant {
  fontSize: string
  fontWeight: number
  lineHeight: number
  letterSpacing?: string
}

export interface ThemeOptions {
  palette?: Partial<Theme['palette']>
  typography?: Partial<Theme['typography']>
  spacing?: Partial<Theme['spacing']>
  breakpoints?: Partial<Theme['breakpoints']>
  zIndex?: Partial<Theme['zIndex']>
  shadows?: Partial<Theme['shadows']>
  transitions?: Partial<Theme['transitions']>
}

export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

export type ColorVariant = 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'

export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

export type Variant = 'default' | 'outlined' | 'filled' | 'text'
