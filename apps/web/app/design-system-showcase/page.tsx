'use client'

import React, { useState } from 'react'
import { 
  Container, Stack, Grid, GridItem, Paper, Typography, 
  Tabs, TabList, Tab, TabPanel,
  Button, ButtonGroup,
  TextField, Select, Checkbox, Radio, Switch, Slider,
  Alert, Dialog, DialogTitle, DialogContent, DialogActions, Snackbar,
  CircularProgress, LinearProgress, Skeleton, Loading,
  Table, TableHead, TableBody, TableRow, TableCell,
  List, ListItem, ListItemText, ListItemIcon, ListItemButton,
  Chip, Tooltip, Avatar,
  Accordion, AccordionSummary, AccordionDetails,
  Breadcrumbs, Pagination, Stepper,
  StatsCard, Badge,
  DatePicker, DataGrid,
  Icon, AddIcon, DeleteIcon, SearchIcon
} from '@/components/design-system'

export default function DesignSystemShowcase() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [tabValue, setTabValue] = useState('forms')
  const [accordionExpanded, setAccordionExpanded] = useState(false)

  const sampleData = [
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User' },
  ]

  const columns = [
    { field: 'name', headerName: 'Name', sortable: true },
    { field: 'email', headerName: 'Email', sortable: true },
    { field: 'role', headerName: 'Role' },
  ]

  return (
    <Container maxWidth="xl" style={{ paddingTop: 'var(--spacing-8)', paddingBottom: 'var(--spacing-8)' }}>
      <Typography variant="h1" gutterBottom>
        Design System Showcase
      </Typography>
      <Typography variant="body1" color="secondary" style={{ marginBottom: 'var(--spacing-6)' }}>
        Comprehensive component library with 50+ production-ready components
      </Typography>

      <Tabs value={tabValue} onChange={(value) => setTabValue(value as string)}>
        <TabList>
          <Tab value="forms" label="Forms" />
          <Tab value="navigation" label="Navigation" />
          <Tab value="layout" label="Layout" />
          <Tab value="feedback" label="Feedback" />
          <Tab value="data" label="Data Display" />
          <Tab value="advanced" label="Advanced" />
        </TabList>

        <TabPanel value="forms">
          <Stack spacing={4}>
            <Paper elevation={1}>
              <Typography variant="h3" gutterBottom>Form Components</Typography>
              
              <Stack spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
                <TextField label="Email" placeholder="Enter email" required helperText="Required field" />
                <TextField label="Password" type="password" error helperText="Invalid password" />
                <Select
                  options={[
                    { value: '1', label: 'Option 1' },
                    { value: '2', label: 'Option 2' },
                    { value: '3', label: 'Option 3' }
                  ]}
                  label="Select Option"
                  placeholder="Choose..."
                />
                <Checkbox label="Accept terms and conditions" />
                <Radio label="Option A" checked />
                <Radio label="Option B" />
                <Switch label="Enable notifications" />
                <Slider value={50} min={0} max={100} label="Volume" />
              </Stack>
            </Paper>
          </Stack>
        </TabPanel>

        <TabPanel value="navigation">
          <Stack spacing={4}>
            <Paper elevation={1}>
              <Typography variant="h3" gutterBottom>Navigation Components</Typography>
              
              <Stack spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
                <Accordion expanded={accordionExpanded} onChange={setAccordionExpanded}>
                  <AccordionSummary>Accordion Section</AccordionSummary>
                  <AccordionDetails expanded={accordionExpanded}>
                    This is the accordion content. It can contain any React components.
                  </AccordionDetails>
                </Accordion>

                <Breadcrumbs
                  items={[
                    { label: 'Home', href: '/' },
                    { label: 'Design System', href: '/design-system' },
                    { label: 'Showcase' }
                  ]}
                />

                <Pagination page={1} count={10} onChange={() => {}} />

                <Stepper
                  steps={[
                    { label: 'Step 1', description: 'Description 1' },
                    { label: 'Step 2', description: 'Description 2' },
                    { label: 'Step 3' }
                  ]}
                  activeStep={1}
                />
              </Stack>
            </Paper>
          </Stack>
        </TabPanel>

        <TabPanel value="layout">
          <Stack spacing={4}>
            <Paper elevation={1}>
              <Typography variant="h3" gutterBottom>Layout Components</Typography>
              
              <Grid container spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
                <GridItem xs={12} sm={6} md={4}>
                  <Paper elevation={2} style={{ padding: 'var(--spacing-4)' }}>
                    <Typography variant="h6">Grid Item 1</Typography>
                  </Paper>
                </GridItem>
                <GridItem xs={12} sm={6} md={4}>
                  <Paper elevation={2} style={{ padding: 'var(--spacing-4)' }}>
                    <Typography variant="h6">Grid Item 2</Typography>
                  </Paper>
                </GridItem>
                <GridItem xs={12} sm={6} md={4}>
                  <Paper elevation={2} style={{ padding: 'var(--spacing-4)' }}>
                    <Typography variant="h6">Grid Item 3</Typography>
                  </Paper>
                </GridItem>
              </Grid>

              <Stack direction="row" spacing={2} style={{ marginTop: 'var(--spacing-4)' }}>
                <Paper elevation={1} style={{ padding: 'var(--spacing-4)', flex: 1 }}>
                  Stack Item 1
                </Paper>
                <Paper elevation={1} style={{ padding: 'var(--spacing-4)', flex: 1 }}>
                  Stack Item 2
                </Paper>
              </Stack>
            </Paper>
          </Stack>
        </TabPanel>

        <TabPanel value="feedback">
          <Stack spacing={4}>
            <Paper elevation={1}>
              <Typography variant="h3" gutterBottom>Feedback Components</Typography>
              
              <Stack spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
                <Alert severity="success" onClose={() => {}}>Success message</Alert>
                <Alert severity="error">Error message</Alert>
                <Alert severity="warning">Warning message</Alert>
                <Alert severity="info">Info message</Alert>

                <Button onClick={() => setDialogOpen(true)}>Open Dialog</Button>
                <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
                  <DialogTitle onClose={() => setDialogOpen(false)}>Dialog Title</DialogTitle>
                  <DialogContent dividers>
                    <Typography>This is dialog content. It can contain any React components.</Typography>
                  </DialogContent>
                  <DialogActions>
                    <Button variant="ghost" onClick={() => setDialogOpen(false)}>Cancel</Button>
                    <Button variant="primary" onClick={() => setDialogOpen(false)}>Save</Button>
                  </DialogActions>
                </Dialog>

                <Button onClick={() => setSnackbarOpen(true)}>Show Snackbar</Button>
                <Snackbar open={snackbarOpen} onClose={() => setSnackbarOpen(false)}>
                  Snackbar message
                </Snackbar>

                <Stack direction="row" spacing={2} alignItems="center">
                  <CircularProgress size={40} />
                  <div style={{ flex: 1 }}>
                    <LinearProgress value={75} variant="determinate" />
                  </div>
                </Stack>

                <Stack direction="row" spacing={2}>
                  <Skeleton variant="text" width={200} />
                  <Skeleton variant="rectangular" width={100} height={50} />
                  <Skeleton variant="circular" width={40} height={40} />
                </Stack>
              </Stack>
            </Paper>
          </Stack>
        </TabPanel>

        <TabPanel value="data">
          <Stack spacing={4}>
            <Paper elevation={1}>
              <Typography variant="h3" gutterBottom>Data Display Components</Typography>
              
              <Stack spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell component="th">Name</TableCell>
                      <TableCell component="th">Email</TableCell>
                      <TableCell component="th">Role</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sampleData.map((row) => (
                      <TableRow key={row.id} hover>
                        <TableCell>{row.name}</TableCell>
                        <TableCell>{row.email}</TableCell>
                        <TableCell>{row.role}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                <List>
                  <ListItemButton>
                    <ListItemIcon><Icon>📁</Icon></ListItemIcon>
                    <ListItemText primary="List Item 1" secondary="Secondary text" />
                  </ListItemButton>
                  <ListItemButton>
                    <ListItemIcon><Icon>📄</Icon></ListItemIcon>
                    <ListItemText primary="List Item 2" secondary="Secondary text" />
                  </ListItemButton>
                </List>

                <Stack direction="row" spacing={2} flexWrap="wrap">
                  <Chip label="Default" />
                  <Chip label="Primary" color="primary" />
                  <Chip label="Success" color="success" onDelete={() => {}} />
                  <Chip label="With Avatar" avatar={<Avatar>JD</Avatar>} />
                </Stack>

                <Stack direction="row" spacing={2} alignItems="center">
                  <Tooltip title="Tooltip text">
                    <Button>Hover for tooltip</Button>
                  </Tooltip>
                  <Avatar src="/api/placeholder/40" alt="User" />
                  <Avatar size="lg">JD</Avatar>
                </Stack>

                <Typography variant="h1">Heading 1</Typography>
                <Typography variant="h2">Heading 2</Typography>
                <Typography variant="body1" gutterBottom>Body text with gutter bottom</Typography>
                <Typography variant="body2" color="secondary">Secondary body text</Typography>
                <Typography variant="caption">Caption text</Typography>
              </Stack>
            </Paper>
          </Stack>
        </TabPanel>

        <TabPanel value="advanced">
          <Stack spacing={4}>
            <Paper elevation={1}>
              <Typography variant="h3" gutterBottom>Advanced Components</Typography>
              
              <Stack spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
                <DataGrid
                  rows={sampleData}
                  columns={columns}
                  pageSize={10}
                  checkboxSelection
                />

                <DatePicker
                  label="Select Date"
                  value={new Date()}
                  onChange={() => {}}
                />
              </Stack>
            </Paper>
          </Stack>
        </TabPanel>
      </Tabs>

      <Paper elevation={1} style={{ marginTop: 'var(--spacing-6)', padding: 'var(--spacing-6)' }}>
        <Typography variant="h3" gutterBottom>Enhanced Components</Typography>
        
        <Stack spacing={3} style={{ marginTop: 'var(--spacing-4)' }}>
          <Stack direction="row" spacing={2} flexWrap="wrap">
            <Button variant="primary" startIcon={<AddIcon />}>Primary</Button>
            <Button variant="secondary" endIcon={<DeleteIcon />}>Secondary</Button>
            <Button variant="ghost" loading>Loading</Button>
            <Button variant="fab"><AddIcon /></Button>
          </Stack>

          <ButtonGroup variant="outlined">
            <Button>One</Button>
            <Button>Two</Button>
            <Button>Three</Button>
          </ButtonGroup>

          <Grid container spacing={2}>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={100}
                label="Total Users"
                trend={{ value: 5, direction: 'up', label: 'vs last month' }}
                variant="elevated"
                icon={<Icon>👥</Icon>}
              />
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={50}
                label="Active Sessions"
                trend={{ value: 10, direction: 'down' }}
                variant="outlined"
              />
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={250}
                label="Total Queries"
                variant="filled"
              />
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={12}
                label="Databases"
                icon={<Icon>DB</Icon>}
              />
            </GridItem>
          </Grid>
        </Stack>
      </Paper>
    </Container>
  )
}
