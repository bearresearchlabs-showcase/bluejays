/**
 * Design System Components
 * OpenAI Apps SDK Inspired UI Components
 * 
 * Export all design system components for easy importing
 */

// Theme & Utilities
export { ThemeProvider, useTheme, useMediaQuery, useBreakpoint } from './ThemeProvider'
export { createTheme, clsx, getContrastText, darken, lighten, spacing } from './utils'
export type { Theme, ThemeOptions, TypographyVariant, Breakpoint, ColorVariant, Size, Variant } from './types'

// Form Components
export * from './forms'

// Navigation Components
export * from './navigation'

// Layout Components
export * from './layout'

// Feedback Components
export * from './feedback'

// Data Display Components
export * from './data-display'

// Advanced Components
export * from './advanced'

// Existing Components
export { default as InlineCard } from './InlineCard'
export { default as InlineCarousel } from './InlineCarousel'
export { default as Badge } from './Badge' // Deprecated: Use Chip instead
export { default as Button } from './Button'
export { ButtonGroup } from './ButtonGroup'
export type { ButtonGroupProps } from './ButtonGroup'
export { default as StatsCard } from './StatsCard'
export { default as FullscreenView } from './FullscreenView'
export { default as PictureInPicture } from './PictureInPicture'

// Icon System
export { Icon, AddIcon, DeleteIcon, EditIcon, SearchIcon, CloseIcon, CheckIcon, ArrowUpIcon, ArrowDownIcon, ArrowLeftIcon, ArrowRightIcon, MenuIcon, MoreVertIcon, MoreHorizIcon } from './Icon'
export type { IconProps } from './Icon'
