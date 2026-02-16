# Design System - Comprehensive Component Library

This design system is inspired by [OpenAI Apps SDK UI Guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines/) and provides a comprehensive MUI/Bootstrap-equivalent component library with 50+ production-ready components.

## Table of Contents

1. [Design Principles](#design-principles)
2. [Theme System](#theme-system)
3. [Utility Classes](#utility-classes)
4. [Form Components](#form-components)
5. [Navigation Components](#navigation-components)
6. [Layout Components](#layout-components)
7. [Feedback Components](#feedback-components)
8. [Data Display Components](#data-display-components)
9. [Advanced Components](#advanced-components)
10. [Icon System](#icon-system)
11. [Usage Examples](#usage-examples)
12. [Accessibility](#accessibility)

## Design Principles

### 1. System Colors
- **Text Colors**: Use system-defined text colors for consistency
- **Background Colors**: Minimal backgrounds that don't compete with content
- **Border Colors**: Subtle borders for spatial separation
- **Accent Colors**: Brand colors only on buttons, badges, and accents
- **Color Palette**: Expanded with primary, secondary, error, warning, info, success variants

### 2. Typography
- **System Fonts**: Platform-native fonts (SF Pro on iOS, Roboto on Android)
- **Typography Scale**: h1-h6, body1, body2, button, caption, overline variants
- **Readability**: Maintain WCAG AA contrast ratios

### 3. Spacing & Layout
- **System Grid**: Consistent spacing scale (0-24)
- **Padding**: Avoid edge-to-edge text
- **Corner Radius**: System-specified corner rounds
- **Breakpoints**: xs (0px), sm (600px), md (900px), lg (1200px), xl (1536px)

### 4. Elevation System
- **Shadows**: 0-24 elevation levels (MUI-style)
- **Z-index Scale**: Mobile stepper (1000) through tooltip (1500)

## Theme System

### ThemeProvider

React Context provider for theme customization and dark mode support.

```tsx
import { ThemeProvider, useTheme } from '@/components/design-system'

function App() {
  return (
    <ThemeProvider defaultDarkMode={false}>
      <YourApp />
    </ThemeProvider>
  )
}

function Component() {
  const { theme, toggleDarkMode } = useTheme()
  // Use theme.palette, theme.typography, etc.
}
```

### CSS Variables

All design tokens are available as CSS variables:

```css
/* Colors */
--color-primary-main
--color-primary-light
--color-primary-dark
--color-text-primary
--color-text-secondary
--color-bg-primary
--color-bg-secondary

/* Typography */
--font-family-system
--font-size-xs through --font-size-6xl
--typography-h1-size through --typography-overline-size

/* Spacing */
--spacing-0 through --spacing-24

/* Elevation */
--elevation-0 through --elevation-24

/* Breakpoints */
--breakpoint-xs through --breakpoint-xl

/* Z-index */
--z-mobile-stepper through --z-tooltip
```

## Utility Classes

Bootstrap-style utility classes for rapid development:

### Spacing
- `m-*`, `mt-*`, `mb-*`, `ml-*`, `mr-*`, `mx-*`, `my-*` (margin)
- `p-*`, `pt-*`, `pb-*`, `pl-*`, `pr-*`, `px-*`, `py-*` (padding)
- `gap-*` (gap)

### Display
- `d-none`, `d-block`, `d-flex`, `d-grid`, `d-inline`, `d-inline-block`

### Flexbox
- `flex-row`, `flex-col`, `justify-*`, `items-*`, `flex-grow`, `flex-shrink`

### Grid
- `grid-cols-*`, `grid-rows-*`, `col-span-*`

### Typography
- `text-xs` through `text-4xl`
- `font-normal`, `font-medium`, `font-semibold`, `font-bold`
- `text-left`, `text-center`, `text-right`
- `text-primary`, `text-secondary`, `text-tertiary`

### Responsive
- `sm:*`, `md:*`, `lg:*` prefixes for responsive utilities

## Form Components

### Input

Base input component with variants and states.

```tsx
import { Input } from '@/components/design-system/forms'

<Input
  variant="outlined"
  size="md"
  error={false}
  helperText="Helper text"
  startAdornment={<Icon />}
  endAdornment={<Icon />}
  fullWidth
/>
```

**Props:**
- `variant?: 'outlined' | 'filled' | 'standard'`
- `size?: 'sm' | 'md' | 'lg'`
- `error?: boolean`
- `helperText?: string`
- `startAdornment?: React.ReactNode`
- `endAdornment?: React.ReactNode`
- `fullWidth?: boolean`

### TextField

Enhanced input with label and helper text.

```tsx
import { TextField } from '@/components/design-system/forms'

<TextField
  label="Email"
  placeholder="Enter email"
  required
  error={hasError}
  helperText="Enter a valid email address"
  multiline={false}
  rows={4}
/>
```

### Select

Dropdown select component.

```tsx
import { Select } from '@/components/design-system/forms'

<Select
  options={[
    { value: '1', label: 'Option 1' },
    { value: '2', label: 'Option 2' }
  ]}
  label="Choose option"
  variant="outlined"
  native={true}
/>
```

### Checkbox, Radio, Switch

Form control components.

```tsx
import { Checkbox, Radio, Switch } from '@/components/design-system/forms'

<Checkbox label="Accept terms" checked={checked} onChange={handleChange} />
<Radio label="Option 1" checked={selected === '1'} onChange={handleChange} />
<Switch label="Enable notifications" checked={enabled} onChange={handleChange} />
```

### Slider

Range slider input.

```tsx
import { Slider } from '@/components/design-system/forms'

<Slider
  value={value}
  onChange={handleChange}
  min={0}
  max={100}
  marks={true}
  valueLabelDisplay="auto"
/>
```

### Form Controls

Form layout components.

```tsx
import { FormControl, FormLabel, FormHelperText, FormGroup, Form } from '@/components/design-system/forms'

<Form onSubmit={handleSubmit}>
  <FormControl error={hasError} required>
    <FormLabel>Email</FormLabel>
    <TextField />
    <FormHelperText>Enter a valid email</FormHelperText>
  </FormControl>
</Form>
```

## Navigation Components

### Tabs

Tab navigation component.

```tsx
import { Tabs, TabList, Tab, TabPanel } from '@/components/design-system/navigation'

<Tabs value={value} onChange={setValue}>
  <TabList>
    <Tab value="1" label="Tab 1" />
    <Tab value="2" label="Tab 2" />
  </TabList>
  <TabPanel value="1">Content 1</TabPanel>
  <TabPanel value="2">Content 2</TabPanel>
</Tabs>
```

### Accordion

Expandable/collapsible content sections.

```tsx
import { Accordion, AccordionSummary, AccordionDetails } from '@/components/design-system/navigation'

<Accordion>
  <AccordionSummary>Section Title</AccordionSummary>
  <AccordionDetails>Content here</AccordionDetails>
</Accordion>
```

### Menu & Dropdown

Dropdown menu components.

```tsx
import { Menu, MenuItem, Dropdown } from '@/components/design-system/navigation'

<Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
  <MenuItem onClick={handleClick}>Option 1</MenuItem>
  <MenuItem divider>Option 2</MenuItem>
</Menu>

<Dropdown
  options={options}
  onSelect={handleSelect}
  trigger={<Button>Open Menu</Button>}
/>
```

### Breadcrumbs

Navigation breadcrumb trail.

```tsx
import { Breadcrumbs } from '@/components/design-system/navigation'

<Breadcrumbs
  items={[
    { label: 'Home', href: '/' },
    { label: 'Databases', href: '/databases' },
    { label: 'Current' }
  ]}
/>
```

### Pagination

Page navigation component.

```tsx
import { Pagination } from '@/components/design-system/navigation'

<Pagination
  page={page}
  count={100}
  onChange={handlePageChange}
  showFirstButton
  showLastButton
/>
```

### Stepper

Step-by-step navigation.

```tsx
import { Stepper } from '@/components/design-system/navigation'

<Stepper
  steps={[
    { label: 'Step 1', description: 'Description' },
    { label: 'Step 2' }
  ]}
  activeStep={1}
/>
```

### AppBar & Drawer

Application bar and side navigation.

```tsx
import { AppBar, Drawer } from '@/components/design-system/navigation'

<AppBar position="fixed" color="primary" elevation={4}>
  <div>Content</div>
</AppBar>

<Drawer open={open} onClose={handleClose} anchor="left">
  <div>Navigation</div>
</Drawer>
```

## Layout Components

### Container

Responsive container with max-width constraints.

```tsx
import { Container } from '@/components/design-system/layout'

<Container maxWidth="lg" disableGutters={false}>
  Content
</Container>
```

### Grid

12-column grid system.

```tsx
import { Grid, GridItem } from '@/components/design-system/layout'

<Grid container spacing={2}>
  <GridItem xs={12} sm={6} md={4}>
    Item 1
  </GridItem>
  <GridItem xs={12} sm={6} md={4}>
    Item 2
  </GridItem>
</Grid>
```

### Stack

Flexbox-based layout component.

```tsx
import { Stack } from '@/components/design-system/layout'

<Stack direction="row" spacing={2} justifyContent="center">
  <div>Item 1</div>
  <div>Item 2</div>
</Stack>
```

### Box

Generic container with flexible styling.

```tsx
import { Box } from '@/components/design-system/layout'

<Box component="section" sx={{ padding: 2, background: 'red' }}>
  Content
</Box>
```

### Paper

Elevated surface component.

```tsx
import { Paper } from '@/components/design-system/layout'

<Paper elevation={2} variant="elevation">
  Content
</Paper>
```

## Feedback Components

### Alert

Alert message component.

```tsx
import { Alert } from '@/components/design-system/feedback'

<Alert
  severity="success"
  variant="standard"
  onClose={handleClose}
  action={<Button>Action</Button>}
>
  Success message
</Alert>
```

### Dialog

Modal dialog component.

```tsx
import { Dialog, DialogTitle, DialogContent, DialogActions } from '@/components/design-system/feedback'

<Dialog open={open} onClose={handleClose} maxWidth="sm">
  <DialogTitle onClose={handleClose}>Title</DialogTitle>
  <DialogContent dividers>Content</DialogContent>
  <DialogActions>
    <Button onClick={handleClose}>Cancel</Button>
    <Button onClick={handleSave}>Save</Button>
  </DialogActions>
</Dialog>
```

### Snackbar & Toast

Temporary notifications.

```tsx
import { Snackbar, Toast } from '@/components/design-system/feedback'

<Snackbar
  open={open}
  onClose={handleClose}
  autoHideDuration={6000}
  anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
>
  Notification message
</Snackbar>
```

### Progress Indicators

Circular and linear progress.

```tsx
import { CircularProgress, LinearProgress } from '@/components/design-system/feedback'

<CircularProgress size={40} variant="indeterminate" />
<LinearProgress value={75} variant="determinate" />
```

### Skeleton

Loading placeholder.

```tsx
import { Skeleton } from '@/components/design-system/feedback'

<Skeleton variant="text" width="100%" />
<Skeleton variant="rectangular" width={200} height={100} />
<Skeleton variant="circular" width={40} height={40} />
```

### Loading

Loading state component.

```tsx
import { Loading } from '@/components/design-system/feedback'

<Loading variant="circular" overlay message="Loading..." />
```

## Data Display Components

### Table

Data table with sorting and pagination.

```tsx
import { Table, TableHead, TableBody, TableRow, TableCell, TablePagination } from '@/components/design-system/data-display'

<Table>
  <TableHead>
    <TableRow>
      <TableCell>Name</TableCell>
      <TableCell>Email</TableCell>
    </TableRow>
  </TableHead>
  <TableBody>
    <TableRow hover>
      <TableCell>John</TableCell>
      <TableCell>john@example.com</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### List

List components.

```tsx
import { List, ListItem, ListItemText, ListItemIcon, ListItemButton } from '@/components/design-system/data-display'

<List dense>
  <ListItemButton onClick={handleClick}>
    <ListItemIcon><Icon /></ListItemIcon>
    <ListItemText primary="Primary" secondary="Secondary" />
  </ListItemButton>
</List>
```

### Chip

Small label component (enhanced Badge).

```tsx
import { Chip } from '@/components/design-system/data-display'

<Chip
  label="Label"
  variant="outlined"
  color="primary"
  onDelete={handleDelete}
  onClick={handleClick}
  avatar={<Avatar />}
/>
```

### Tooltip & Popover

Tooltip and popover components.

```tsx
import { Tooltip, Popover } from '@/components/design-system/data-display'

<Tooltip title="Tooltip text" placement="top">
  <Button>Hover me</Button>
</Tooltip>

<Popover anchorEl={anchorEl} open={open} onClose={handleClose}>
  Popover content
</Popover>
```

### Avatar

Avatar component.

```tsx
import { Avatar } from '@/components/design-system/data-display'

<Avatar src="/image.jpg" alt="User" size="md" variant="circular" />
<Avatar size="lg">JD</Avatar>
```

### Typography

Typography component with variants.

```tsx
import { Typography } from '@/components/design-system/data-display'

<Typography variant="h1" component="h1" color="primary">
  Heading
</Typography>
<Typography variant="body1" gutterBottom>
  Body text
</Typography>
```

## Advanced Components

### DataGrid

Basic data grid with sorting, filtering, and pagination.

```tsx
import { DataGrid } from '@/components/design-system/advanced'

<DataGrid
  rows={data}
  columns={[
    { field: 'name', headerName: 'Name', sortable: true },
    { field: 'email', headerName: 'Email' }
  ]}
  pageSize={10}
  checkboxSelection
/>
```

### DatePicker, TimePicker, DateTimePicker

Date and time picker components.

```tsx
import { DatePicker, TimePicker, DateTimePicker } from '@/components/design-system/advanced'

<DatePicker
  value={date}
  onChange={setDate}
  label="Select date"
  minDate={minDate}
  maxDate={maxDate}
/>

<DateTimePicker value={dateTime} onChange={setDateTime} />
```

### TransferList

Dual list transfer component.

```tsx
import { TransferList } from '@/components/design-system/advanced'

<TransferList
  leftItems={availableItems}
  rightItems={selectedItems}
  onTransfer={handleTransfer}
  searchable
/>
```

## Icon System

Icon component wrapper.

```tsx
import { Icon, AddIcon, DeleteIcon, SearchIcon } from '@/components/design-system'

<Icon fontSize="md" color="primary">
  <svg>...</svg>
</Icon>

<AddIcon />
<DeleteIcon />
<SearchIcon />
```

## Enhanced Components

### Button (Enhanced)

Enhanced with loading state, icon support, and FAB variant.

```tsx
import { Button } from '@/components/design-system'

<Button
  variant="primary"
  size="md"
  loading={isLoading}
  startIcon={<Icon />}
  endIcon={<Icon />}
  onClick={handleClick}
>
  Click me
</Button>

<Button variant="fab" size="md">
  <AddIcon />
</Button>
```

### ButtonGroup

Group of buttons displayed together.

```tsx
import { ButtonGroup } from '@/components/design-system'

<ButtonGroup variant="outlined" orientation="horizontal">
  <Button>One</Button>
  <Button>Two</Button>
  <Button>Three</Button>
</ButtonGroup>
```

### StatsCard (Enhanced)

Enhanced with variants, chart integration, and improved trend visualization.

```tsx
import { StatsCard } from '@/components/design-system'

<StatsCard
  value={100}
  label="Total Users"
  trend={{ value: 5, direction: 'up', label: 'vs last month' }}
  variant="elevated"
  icon={<Icon />}
  chart={<ChartComponent />}
/>
```

## Usage Examples

### Complete Form Example

```tsx
import { Form, FormControl, FormLabel, TextField, Select, Button } from '@/components/design-system'

<Form onSubmit={handleSubmit}>
  <FormControl fullWidth>
    <FormLabel>Email</FormLabel>
    <TextField
      type="email"
      required
      error={hasError}
      helperText="Enter your email"
    />
  </FormControl>
  
  <FormControl fullWidth>
    <FormLabel>Country</FormLabel>
    <Select
      options={countries}
      placeholder="Select country"
    />
  </FormControl>
  
  <Button type="submit" variant="primary">
    Submit
  </Button>
</Form>
```

### Complete Layout Example

```tsx
import { Container, Grid, Stack, Paper, Typography } from '@/components/design-system'

<Container maxWidth="lg">
  <Grid container spacing={3}>
    <GridItem xs={12} md={8}>
      <Paper elevation={2}>
        <Typography variant="h4">Main Content</Typography>
      </Paper>
    </GridItem>
    <GridItem xs={12} md={4}>
      <Stack spacing={2}>
        <Paper>Sidebar 1</Paper>
        <Paper>Sidebar 2</Paper>
      </Stack>
    </GridItem>
  </Grid>
</Container>
```

## Accessibility

- **WCAG AA Contrast**: All text meets minimum contrast ratios
- **Focus States**: Visible focus indicators for keyboard navigation
- **ARIA Attributes**: Proper ARIA labels and roles
- **Keyboard Navigation**: Full keyboard support for all interactive components
- **Screen Reader Support**: Semantic HTML and ARIA attributes

## Component Count

**Total Components: 50+**

- **Form Components**: 13 (Input, TextField, Textarea, Select, Checkbox, Radio, Switch, Slider, Form, FormControl, FormLabel, FormHelperText, FormGroup)
- **Navigation Components**: 9 (Tabs, Accordion, Menu, Dropdown, Breadcrumbs, Pagination, Stepper, AppBar, Drawer)
- **Layout Components**: 5 (Container, Grid, Stack, Box, Paper)
- **Feedback Components**: 9 (Alert, Dialog, Modal, Snackbar, Toast, Progress, CircularProgress, LinearProgress, Skeleton, Loading)
- **Data Display Components**: 7 (Table, List, Chip, Tooltip, Popover, Avatar, Typography)
- **Advanced Components**: 5 (DataGrid, DatePicker, TimePicker, DateTimePicker, TransferList)
- **Core Components**: 7 (Button, ButtonGroup, Badge, Chip, StatsCard, Icon, ThemeProvider)
- **Display Mode Components**: 3 (InlineCard, InlineCarousel, FullscreenView, PictureInPicture)

## Integration

The design system is automatically loaded via `app/layout.tsx`:

```tsx
import './design-system.css'
import './design-system-utilities.css'
```

All components can be imported from:

```tsx
import {
  // Forms
  Input, TextField, Select, Checkbox, Radio, Switch,
  // Navigation
  Tabs, Accordion, Menu, Dropdown, Breadcrumbs, Pagination,
  // Layout
  Container, Grid, Stack, Box, Paper,
  // Feedback
  Alert, Dialog, Snackbar, Progress, Loading,
  // Data Display
  Table, List, Chip, Tooltip, Avatar, Typography,
  // Advanced
  DataGrid, DatePicker, TransferList,
  // Core
  Button, ButtonGroup, Icon, ThemeProvider
} from '@/components/design-system'
```

## References

- [OpenAI Apps SDK UI Guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines/)
- [OpenAI Apps SDK Examples](https://github.com/openai/openai-apps-sdk-examples)
- [Material-UI Documentation](https://mui.com/)
- [Bootstrap Documentation](https://getbootstrap.com/)
