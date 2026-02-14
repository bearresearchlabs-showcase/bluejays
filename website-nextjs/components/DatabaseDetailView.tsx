'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Container } from '@/components/design-system/layout/Container'
import { Grid, GridItem } from '@/components/design-system/layout/Grid'
import { Paper } from '@/components/design-system/layout/Paper'
import { Stack } from '@/components/design-system/layout/Stack'
import { Typography } from '@/components/design-system/data-display/Typography'
import { Tabs, TabList, Tab, TabPanel } from '@/components/design-system/navigation/Tabs'
import { Chip } from '@/components/design-system/data-display/Chip'
import StatsCard from '@/components/design-system/StatsCard'
import { Alert } from '@/components/design-system/feedback/Alert'
import { Loading } from '@/components/design-system/feedback/Loading'
import Button from '@/components/design-system/Button'
import { Breadcrumbs } from '@/components/design-system/navigation/Breadcrumbs'
import ClientScripts from './ClientScripts'

interface DatabaseDetail {
  id: string
  db_number: number
  name: string
  short_description: string
  full_description: string
  created_date: string
  version: string
  schema: {
    total_tables: number
    tables: Array<{
      name: string
      description: string
      column_count: number
    }>
  }
  queries: {
    total_queries: number
    preview: Array<{
      number: number
      title: string
      description: string
      complexity: string
    }>
  }
  files: {
    total_data_size_mb: string
    data_files: Array<{
      name: string
      size_mb: string
    }>
  }
}

interface DatabaseDetailViewProps {
  dbId: string
}

export default function DatabaseDetailView({ dbId }: DatabaseDetailViewProps) {
  const [db, setDb] = useState<DatabaseDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'schema' | 'queries' | 'files'>('overview')

  useEffect(() => {
    fetch(`/api/databases/${dbId}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data: DatabaseDetail) => {
        setDb(data)
        setLoading(false)
        
        // Handle hash fragment after content loads
        if (typeof window !== 'undefined') {
          const hash = window.location.hash.replace('#', '')
          if (hash) {
            // Wait for DOM to update, then scroll to element
            setTimeout(() => {
              const element = document.getElementById(hash)
              if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' })
              }
            }, 100)
          }
        }
      })
      .catch(err => {
        console.error('Failed to load database:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [dbId])
  
  // Also handle hash changes (e.g., when navigating within the same page)
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '')
      if (hash) {
        setTimeout(() => {
          const element = document.getElementById(hash)
          if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
      }
    }
    
    if (typeof window !== 'undefined') {
      window.addEventListener('hashchange', handleHashChange)
      return () => window.removeEventListener('hashchange', handleHashChange)
    }
  }, [])

  if (loading) {
    return (
      <>
        <ClientScripts />
        <main className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Loading />
          </Container>
        </main>
      </>
    )
  }

  if (error || !db) {
    return (
      <>
        <ClientScripts />
        <main className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Stack spacing={4} alignItems="center">
              <Alert severity="error">
                Error Loading Database: {error || 'Database not found'}
              </Alert>
              <Link href="/databases" style={{ textDecoration: 'none' }}>
                <Button variant="secondary">
                  ← Back to Databases
                </Button>
              </Link>
            </Stack>
          </Container>
        </main>
      </>
    )
  }

  return (
    <>
      <ClientScripts />
      <main className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          {/* Breadcrumbs */}
          <Breadcrumbs
            items={[
              { label: 'Databases', href: '/databases' },
              { label: db.id.toUpperCase() },
            ]}
            style={{ marginBottom: 'var(--spacing-4)' }}
          />

          {/* Header */}
          <Stack spacing={2} style={{ marginBottom: 'var(--spacing-8)', paddingBottom: 'var(--spacing-6)', borderBottom: '2px solid var(--color-border-primary)' }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
              <Stack spacing={1}>
                <Typography variant="h1">
                  {db.name}
                </Typography>
                <Typography variant="body1" color="secondary">
                  {db.id.toUpperCase()} • Version {db.version} • Created {db.created_date}
                </Typography>
              </Stack>
              <Link href="/databases" style={{ textDecoration: 'none' }}>
                <Button variant="secondary" size="sm">
                  ← All Databases
                </Button>
              </Link>
            </Stack>
            <Typography variant="body1" color="secondary">
              {db.short_description}
            </Typography>
          </Stack>

          {/* Tabs */}
          <Tabs value={activeTab} onChange={(value) => setActiveTab(value as any)}>
            <TabList>
              <Tab value="overview" label="Overview" />
              <Tab value="schema" label="Schema" />
              <Tab value="queries" label="Queries" />
              <Tab value="files" label="Files" />
            </TabList>

            {/* Overview Tab */}
            <TabPanel value="overview">
              <Stack spacing={4}>
                <Typography variant="h2">Overview</Typography>
                <Paper elevation={0} variant="outlined">
                  <Typography variant="body1" style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8' }}>
                    {db.full_description.split('\n\n').map((para, i) => {
                      const parts = para.split(/(\*\*.*?\*\*)/g)
                      return (
                        <p key={i} style={{ marginBottom: 'var(--spacing-4)' }}>
                          {parts.map((part, j) => {
                            if (part.startsWith('**') && part.endsWith('**')) {
                              return <strong key={j}>{part.slice(2, -2)}</strong>
                            }
                            return <span key={j}>{part}</span>
                          })}
                        </p>
                      )
                    })}
                  </Typography>
                </Paper>
                <Grid container spacing={3}>
                  <GridItem xs={12} sm={4}>
                    <StatsCard
                      value={db.schema.total_tables}
                      label="Tables"
                      variant="elevated"
                    />
                  </GridItem>
                  <GridItem xs={12} sm={4}>
                    <StatsCard
                      value={db.queries.total_queries}
                      label="Queries"
                      variant="elevated"
                    />
                  </GridItem>
                  <GridItem xs={12} sm={4}>
                    <StatsCard
                      value={`${(parseFloat(db.files.total_data_size_mb) / 1024).toFixed(1)} GB`}
                      label="Data Size"
                      variant="elevated"
                    />
                  </GridItem>
                </Grid>
              </Stack>
            </TabPanel>

            {/* Schema Tab */}
            <TabPanel value="schema">
              <Stack spacing={4}>
                <Stack spacing={1}>
                  <Typography variant="h2">Database Schema</Typography>
                  <Typography variant="body2" color="secondary">
                    {db.schema.total_tables} tables with detailed column information
                  </Typography>
                </Stack>
                <Grid container spacing={3}>
                  {db.schema.tables.map(table => (
                    <GridItem xs={12} sm={6} md={4} key={table.name}>
                      <Paper elevation={1} variant="outlined">
                        <Stack spacing={2}>
                          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                            <Typography variant="h6" style={{ fontFamily: 'monospace' }}>
                              {table.name}
                            </Typography>
                            <Chip
                              label={`${table.column_count} columns`}
                              size="sm"
                              variant="outlined"
                            />
                          </Stack>
                          {table.description && (
                            <Typography variant="body2" color="secondary">
                              {table.description}
                            </Typography>
                          )}
                        </Stack>
                      </Paper>
                    </GridItem>
                  ))}
                </Grid>
              </Stack>
            </TabPanel>

            {/* Queries Tab */}
            <TabPanel value="queries">
              <Stack spacing={4}>
                <Stack spacing={1}>
                  <Typography variant="h2">SQL Queries</Typography>
                  <Typography variant="body2" color="secondary">
                    {db.queries.total_queries} complex SQL queries with business context
                  </Typography>
                </Stack>
                <Grid container spacing={3}>
                  {db.queries.preview.map(query => (
                    <GridItem xs={12} key={query.number}>
                      <Paper elevation={1} variant="outlined">
                        <Stack spacing={2}>
                          <Typography variant="h6">
                            Query {query.number}: {query.title}
                          </Typography>
                          <Typography variant="body2" color="secondary">
                            {query.description}
                          </Typography>
                          {query.complexity && (
                            <Chip
                              label={`Complexity: ${query.complexity}`}
                              variant="filled"
                              color="info"
                              size="sm"
                            />
                          )}
                        </Stack>
                      </Paper>
                    </GridItem>
                  ))}
                </Grid>
                {db.queries.total_queries > db.queries.preview.length && (
                  <Paper elevation={0} variant="outlined" style={{ textAlign: 'center', padding: 'var(--spacing-6)' }}>
                    <Typography variant="body2" color="secondary">
                      View all {db.queries.total_queries} queries in the full documentation below ↓
                    </Typography>
                  </Paper>
                )}
              </Stack>
            </TabPanel>

            {/* Files Tab */}
            <TabPanel value="files">
              <Stack spacing={4}>
                <Stack spacing={1}>
                  <Typography variant="h2">Data Files</Typography>
                  <Typography variant="body2" color="secondary">
                    Total size: {(parseFloat(db.files.total_data_size_mb) / 1024).toFixed(2)} GB
                  </Typography>
                </Stack>
                <Stack spacing={2}>
                  {db.files.data_files.map(file => (
                    <Paper key={file.name} elevation={1} variant="outlined">
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" style={{ fontFamily: 'monospace' }}>
                          {file.name}
                        </Typography>
                        <Typography variant="body2" color="secondary">
                          {(parseFloat(file.size_mb) / 1024).toFixed(2)} GB
                        </Typography>
                      </Stack>
                    </Paper>
                  ))}
                </Stack>
              </Stack>
            </TabPanel>
          </Tabs>
        </Container>
      </main>
    </>
  )
}
