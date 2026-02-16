'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ClientScripts from './ClientScripts'
import { Container } from '@/components/design-system/layout/Container'
import { Box } from '@/components/design-system/layout/Box'
import { Grid, GridItem } from '@/components/design-system/layout/Grid'
import { Paper } from '@/components/design-system/layout/Paper'
import { Stack } from '@/components/design-system/layout/Stack'
import { Typography } from '@/components/design-system/data-display/Typography'
import { Tabs, TabList, Tab, TabPanel } from '@/components/design-system/navigation/Tabs'
import { Chip } from '@/components/design-system/data-display/Chip'
import StatsCard from '@/components/design-system/StatsCard'
import Button from '@/components/design-system/Button'
import { Loading } from '@/components/design-system/feedback/Loading'
import { Alert } from '@/components/design-system/feedback/Alert'

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
      intent_display?: string
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

interface DatabaseDetailProps {
  dbId: string
}

export default function DatabaseDetail({ dbId }: DatabaseDetailProps) {
  const [db, setDb] = useState<DatabaseDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'schema' | 'queries' | 'files'>('overview')

  useEffect(() => {
    fetch(`/api/databases/${dbId}`)
      .then(res => res.json())
      .then((data: DatabaseDetail) => {
        setDb(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load database:', err)
        setLoading(false)
      })
  }, [dbId])

  if (loading) {
    return (
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Stack spacing={4} alignItems="center">
            <Loading />
            <Typography variant="body1">Loading database...</Typography>
          </Stack>
        </Container>
      </Box>
    )
  }

  if (!db) {
    return (
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Stack spacing={4} alignItems="center">
            <Alert severity="error">Database not found</Alert>
            <Link href="/databases" style={{ textDecoration: 'none' }}>
              <Button variant="secondary">← Back to Databases</Button>
            </Link>
          </Stack>
        </Container>
      </Box>
    )
  }

  return (
    <>
      <ClientScripts />
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Stack spacing={4}>
            {/* Header */}
            <Box component="header" style={{ paddingBottom: 'var(--spacing-4)', borderBottom: '2px solid var(--color-border-primary)' }}>
              <Stack direction="row" justifyContent="space-between" alignItems="flex-start" style={{ marginBottom: 'var(--spacing-4)' }}>
                <Stack spacing={1}>
                  <Typography variant="h1">{db.name}</Typography>
                  <Typography variant="body1" color="secondary">
                    {db.id.toUpperCase()} · Version {db.version} · Created {db.created_date}
                  </Typography>
                </Stack>
                <Link href="/databases" style={{ textDecoration: 'none' }}>
                  <Button variant="secondary" size="sm">← All Databases</Button>
                </Link>
              </Stack>
              <Typography variant="body1" color="secondary" style={{ lineHeight: '1.6' }}>
                {db.short_description}
              </Typography>
            </Box>

            {/* Tabs */}
            <Tabs value={activeTab} onChange={(value) => setActiveTab(value as typeof activeTab)}>
              <TabList>
                <Tab value="overview" label="Overview" />
                <Tab value="schema" label="Schema" />
                <Tab value="queries" label="Queries" />
                <Tab value="files" label="Files" />
              </TabList>

              {/* Tab Content */}
              <TabPanel value="overview">
                <Stack spacing={4}>
                  <Typography variant="h2">Overview</Typography>
                  <Box style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8' }}>
                    {db.full_description.split('\n\n').map((para, i) => {
                      const parts = para.split(/(\*\*.*?\*\*)/g)
                      return (
                        <Typography key={i} variant="body1" style={{ marginBottom: 'var(--spacing-4)' }}>
                          {parts.map((part, j) => {
                            if (part.startsWith('**') && part.endsWith('**')) {
                              return <strong key={j}>{part.slice(2, -2)}</strong>
                            }
                            return <span key={j}>{part}</span>
                          })}
                        </Typography>
                      )
                    })}
                  </Box>
                  <Grid container spacing={3}>
                    <GridItem xs={12} sm={4}>
                      <StatsCard
                        label="Tables"
                        value={db.schema.total_tables.toString()}
                      />
                    </GridItem>
                    <GridItem xs={12} sm={4}>
                      <StatsCard
                        label="Queries"
                        value={db.queries.total_queries.toString()}
                      />
                    </GridItem>
                    <GridItem xs={12} sm={4}>
                      <StatsCard
                        label="Data Size"
                        value={`${parseFloat(db.files.total_data_size_mb).toLocaleString()} MB`}
                      />
                    </GridItem>
                  </Grid>
                </Stack>
              </TabPanel>

              <TabPanel value="schema">
                <Stack spacing={3}>
                  <Typography variant="h2">Database Schema</Typography>
                  <Typography variant="body1" color="secondary">
                    {db.schema.total_tables} tables with detailed column information
                  </Typography>
                  <Grid container spacing={3}>
                    {db.schema.tables.map(table => (
                      <GridItem key={table.name} xs={12} sm={6} md={4}>
                        <Paper elevation={1} style={{ padding: 'var(--spacing-4)' }}>
                          <Stack spacing={2}>
                            <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                              <Typography variant="h6" style={{ fontFamily: 'monospace' }}>
                                {table.name}
                              </Typography>
                              <Chip label={`${table.column_count} columns`} size="sm" />
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

              <TabPanel value="queries">
                <Stack spacing={3}>
                  <Typography variant="h2">SQL Queries</Typography>
                  <Typography variant="body1" color="secondary">
                    {db.queries.total_queries} complex SQL queries with intent-focused natural language descriptions
                  </Typography>
                  <Grid container spacing={3}>
                    {db.queries.preview.map(query => {
                      const intentText = query.intent_display || query.description
                      return (
                      <GridItem key={query.number} xs={12}>
                        <Paper elevation={1} style={{ padding: 'var(--spacing-6)' }}>
                          <Stack spacing={2}>
                            <Typography variant="h6">
                              Query {query.number}: {query.title}
                            </Typography>
                            {intentText && (
                              <>
                                <Typography variant="caption" color="secondary" style={{ fontWeight: 600, textTransform: 'uppercase' }}>
                                  Intent
                                </Typography>
                                <Typography variant="body2" color="secondary" style={{ lineHeight: '1.6' }}>
                                  {intentText}
                                </Typography>
                              </>
                            )}
                            {query.complexity && (
                              <Chip
                                label={`Complexity: ${query.complexity}`}
                                size="sm"
                                color="secondary"
                              />
                            )}
                          </Stack>
                        </Paper>
                      </GridItem>
                    )})}
                  </Grid>
                  {db.queries.total_queries > db.queries.preview.length && (
                    <Typography variant="body1" color="secondary" align="center" style={{ marginTop: 'var(--spacing-4)' }}>
                      View all {db.queries.total_queries} queries in the full documentation →
                    </Typography>
                  )}
                </Stack>
              </TabPanel>

              <TabPanel value="files">
                <Stack spacing={3}>
                  <Typography variant="h2">Data Files</Typography>
                  <Typography variant="body1" color="secondary">
                    Total size: {parseFloat(db.files.total_data_size_mb).toLocaleString()} MB
                  </Typography>
                  <Stack spacing={2}>
                    {db.files.data_files.map(file => (
                      <Paper key={file.name} elevation={1} variant="outlined" style={{ padding: 'var(--spacing-3) var(--spacing-4)' }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" style={{ fontFamily: 'monospace' }}>
                            {file.name}
                          </Typography>
                          <Typography variant="body2" color="secondary">
                            {parseFloat(file.size_mb).toLocaleString()} MB
                          </Typography>
                        </Stack>
                      </Paper>
                    ))}
                  </Stack>
                </Stack>
              </TabPanel>
            </Tabs>
          </Stack>
        </Container>
      </Box>
    </>
  )
}
