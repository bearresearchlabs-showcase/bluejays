'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Container } from '@/components/design-system/layout/Container'
import { Grid, GridItem } from '@/components/design-system/layout/Grid'
import { Paper } from '@/components/design-system/layout/Paper'
import { Stack } from '@/components/design-system/layout/Stack'
import { Box } from '@/components/design-system/layout/Box'
import { Typography } from '@/components/design-system/data-display/Typography'
import TextField from '@/components/design-system/forms/TextField'
import Select from '@/components/design-system/forms/Select'
import Button from '@/components/design-system/Button'
import { Chip } from '@/components/design-system/data-display/Chip'
import StatsCard from '@/components/design-system/StatsCard'
import { Alert } from '@/components/design-system/feedback/Alert'
import { Loading } from '@/components/design-system/feedback/Loading'
import ClientScripts from './ClientScripts'

interface Database {
  id: string
  db_number: number
  name: string
  short_description: string
  schema: {
    total_tables: number
    tables: Array<{ name: string; column_count: number }>
  }
  queries: {
    total_queries: number
  }
  files: {
    total_data_size_mb: string
  }
}

interface ComprehensiveData {
  statistics: {
    total_databases: number
    total_tables: number
    total_queries: number
    total_data_size_mb: string
  }
  databases: Database[]
}

export default function DatabasesCatalog() {
  const [data, setData] = useState<ComprehensiveData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState<'all' | 'small' | 'medium' | 'large'>('all')

  useEffect(() => {
    fetch('/api/databases')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data: ComprehensiveData) => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load databases:', err)
        setError(err.message)
        setLoading(false)
      })
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

  if (error || !data) {
    return (
      <>
        <ClientScripts />
        <main className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Box style={{ marginBottom: 'var(--spacing-4)' }}>
              <Alert severity="error">
                Error Loading Databases: {error || 'Failed to load database catalog'}
              </Alert>
            </Box>
            <Button onClick={() => window.location.reload()}>
              Retry
            </Button>
          </Container>
        </main>
      </>
    )
  }

  const filteredDatabases = data.databases.filter(db => {
    const matchesSearch = 
      db.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      db.short_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      db.id.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = 
      filterBy === 'all' ||
      (filterBy === 'small' && db.schema.total_tables < 12) ||
      (filterBy === 'medium' && db.schema.total_tables >= 12 && db.schema.total_tables < 15) ||
      (filterBy === 'large' && db.schema.total_tables >= 15)
    
    return matchesSearch && matchesFilter
  })

  const getSizeColor = (tables: number): 'primary' | 'warning' | 'info' => {
    if (tables >= 15) return 'info'
    if (tables >= 12) return 'warning'
    return 'primary'
  }

  return (
    <>
      <ClientScripts />
      <main className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          {/* Header */}
          <Stack spacing={2} style={{ marginBottom: 'var(--spacing-8)' }}>
            <Typography variant="h1">
              Database Catalog
            </Typography>
            <Typography variant="body1" color="secondary">
              Production databases from client/db/ • {data.statistics.total_databases} databases, {data.statistics.total_tables} tables, {data.statistics.total_queries} queries
            </Typography>
          </Stack>

          {/* Statistics Dashboard */}
          <Grid container spacing={4} style={{ marginBottom: 'var(--spacing-8)' }}>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={data.statistics.total_databases}
                label="Databases"
                variant="elevated"
              />
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={data.statistics.total_tables}
                label="Total Tables"
                variant="elevated"
              />
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={data.statistics.total_queries}
                label="SQL Queries"
                variant="elevated"
              />
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <StatsCard
                value={`${(parseFloat(data.statistics.total_data_size_mb) / 1024).toFixed(1)} GB`}
                label="Data Size"
                variant="elevated"
              />
            </GridItem>
          </Grid>

          {/* Search and Filter */}
          <Stack direction="row" spacing={2} alignItems="center" style={{ marginBottom: 'var(--spacing-8)' }} flexWrap="wrap">
            <TextField
              placeholder="Search databases by name, description, or ID..."
              value={searchTerm}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
              fullWidth
              style={{ minWidth: '250px', flex: 1 }}
            />
            <Select
              value={filterBy}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFilterBy(e.target.value as 'all' | 'small' | 'medium' | 'large')}
              options={[
                { value: 'all', label: 'All Sizes' },
                { value: 'small', label: 'Small (<12 tables)' },
                { value: 'medium', label: 'Medium (12-14 tables)' },
                { value: 'large', label: 'Large (15+ tables)' },
              ]}
              style={{ minWidth: '200px' }}
            />
            <Typography variant="body2" color="secondary" style={{ whiteSpace: 'nowrap' }}>
              {filteredDatabases.length} of {data.databases.length}
            </Typography>
          </Stack>

          {/* Database Grid */}
          {filteredDatabases.length > 0 ? (
            <Grid container spacing={4}>
              {filteredDatabases.map((db) => (
                <GridItem xs={12} sm={6} md={4} key={db.id}>
                  <Link href={`/db/${db.id}`} style={{ textDecoration: 'none', display: 'block', height: '100%' }}>
                    <Box
                      onMouseEnter={(e: React.MouseEvent<HTMLDivElement>) => {
                        const paper = e.currentTarget.querySelector('.paper-card') as HTMLElement
                        if (paper) {
                          paper.style.boxShadow = 'var(--elevation-4)'
                          paper.style.transform = 'translateY(-2px)'
                        }
                      }}
                      onMouseLeave={(e: React.MouseEvent<HTMLDivElement>) => {
                        const paper = e.currentTarget.querySelector('.paper-card') as HTMLElement
                        if (paper) {
                          paper.style.boxShadow = 'var(--elevation-1)'
                          paper.style.transform = 'translateY(0)'
                        }
                      }}
                    >
                      <Paper
                        elevation={1}
                        className="paper-card"
                        style={{
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          cursor: 'pointer',
                          transition: 'all var(--transition-base)',
                        }}
                      >
                      <Stack spacing={3} style={{ flex: 1 }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                          <Typography variant="h6">
                            {db.id.toUpperCase()}
                          </Typography>
                          <Chip
                            label={`${db.schema.total_tables} tables`}
                            color={getSizeColor(db.schema.total_tables)}
                            size="sm"
                          />
                        </Stack>
                        
                        <Typography variant="h6" fontWeight="semibold">
                          {db.name}
                        </Typography>
                        
                        <Typography variant="body2" color="secondary" style={{ flex: 1 }}>
                          {db.short_description}
                        </Typography>
                        
                        <Stack direction="row" spacing={2} style={{ paddingTop: 'var(--spacing-4)', borderTop: '1px solid var(--color-border-primary)' }}>
                          <Typography variant="caption" color="tertiary">
                            {db.queries.total_queries} queries
                          </Typography>
                          <Typography variant="caption" color="tertiary">
                            {(parseFloat(db.files.total_data_size_mb) / 1024).toFixed(1)} GB
                          </Typography>
                        </Stack>
                      </Stack>
                      </Paper>
                    </Box>
                  </Link>
                </GridItem>
              ))}
            </Grid>
          ) : (
            <Paper elevation={1} style={{ padding: 'var(--spacing-12)', textAlign: 'center' }}>
              <Stack spacing={3} alignItems="center">
                <Typography variant="body1" color="secondary">
                  No databases found matching your search criteria.
                </Typography>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSearchTerm('')
                    setFilterBy('all')
                  }}
                >
                  Clear Filters
                </Button>
              </Stack>
            </Paper>
          )}
        </Container>
      </main>
    </>
  )
}
