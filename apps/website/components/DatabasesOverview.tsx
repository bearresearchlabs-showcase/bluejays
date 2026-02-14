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
import TextField from '@/components/design-system/forms/TextField'
import Select from '@/components/design-system/forms/Select'
import { Chip } from '@/components/design-system/data-display/Chip'
import StatsCard from '@/components/design-system/StatsCard'
import { Loading } from '@/components/design-system/feedback/Loading'
import { Alert } from '@/components/design-system/feedback/Alert'
import Button from '@/components/design-system/Button'

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
    average_tables_per_db: string
    average_queries_per_db: string
  }
  databases: Database[]
}

export default function DatabasesOverview() {
  const [data, setData] = useState<ComprehensiveData | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState<'all' | 'small' | 'medium' | 'large'>('all')

  useEffect(() => {
    fetch('/api/databases')
      .then(res => res.json())
      .then((data: ComprehensiveData) => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load databases:', err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Stack spacing={4} alignItems="center">
            <Loading />
            <Typography variant="body1">Loading databases...</Typography>
          </Stack>
        </Container>
      </Box>
    )
  }

  if (!data) {
    return (
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Stack spacing={4} alignItems="center">
            <Alert severity="error">Failed to load databases</Alert>
          </Stack>
        </Container>
      </Box>
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

  const getSizeColor = (tableCount: number): 'primary' | 'secondary' | 'warning' | 'error' => {
    if (tableCount >= 15) return 'primary'
    if (tableCount >= 12) return 'warning'
    return 'secondary'
  }

  return (
    <>
      <ClientScripts />
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Box component="section" id="overview">
            <Stack spacing={4}>
              <Box component="header">
                <Typography variant="h1">Database Catalog</Typography>
                <Typography variant="body1" style={{ marginTop: 'var(--spacing-2)' }}>
                  Comprehensive view of all production databases from client/db/
                </Typography>
              </Box>

              {/* Statistics Dashboard */}
              <Grid container spacing={3}>
                <GridItem xs={12} sm={6} md={3}>
                  <StatsCard
                    label="Databases"
                    value={data.statistics.total_databases.toString()}
                  />
                </GridItem>
                <GridItem xs={12} sm={6} md={3}>
                  <StatsCard
                    label="Total Tables"
                    value={data.statistics.total_tables.toString()}
                  />
                </GridItem>
                <GridItem xs={12} sm={6} md={3}>
                  <StatsCard
                    label="SQL Queries"
                    value={data.statistics.total_queries.toString()}
                  />
                </GridItem>
                <GridItem xs={12} sm={6} md={3}>
                  <StatsCard
                    label="Data Size"
                    value={`${parseFloat(data.statistics.total_data_size_mb).toLocaleString()} MB`}
                  />
                </GridItem>
              </Grid>

              {/* Search and Filter */}
              <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
                <TextField
                  placeholder="Search databases..."
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
                <Typography variant="body2" color="secondary">
                  Showing {filteredDatabases.length} of {data.databases.length}
                </Typography>
              </Stack>

              {/* Database Grid */}
              {filteredDatabases.length > 0 ? (
                <Grid container spacing={3}>
                  {filteredDatabases.map((db) => (
                    <GridItem key={db.id} xs={12} sm={6} md={4}>
                      <Link
                        href={`/db/${db.id}`}
                        style={{ textDecoration: 'none', display: 'block', height: '100%' }}
                      >
                        <Paper
                          elevation={1}
                          style={{
                            height: '100%',
                            padding: 'var(--spacing-6)',
                            cursor: 'pointer',
                            transition: 'all var(--transition-base)',
                            display: 'flex',
                            flexDirection: 'column',
                          }}
                          onMouseEnter={(e: React.MouseEvent<HTMLDivElement>) => {
                            e.currentTarget.style.boxShadow = 'var(--elevation-4)'
                            e.currentTarget.style.transform = 'translateY(-2px)'
                          }}
                          onMouseLeave={(e: React.MouseEvent<HTMLDivElement>) => {
                            e.currentTarget.style.boxShadow = 'var(--elevation-1)'
                            e.currentTarget.style.transform = 'translateY(0)'
                          }}
                        >
                          <Stack spacing={3} style={{ flex: 1 }}>
                            <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                              <Typography variant="h6">{db.id.toUpperCase()}</Typography>
                              <Chip
                                label={`${db.schema.total_tables} tables`}
                                color={getSizeColor(db.schema.total_tables)}
                                size="sm"
                              />
                            </Stack>
                            <Typography variant="h6" fontWeight="semibold">{db.name}</Typography>
                            <Typography variant="body2" color="secondary" style={{ flex: 1 }}>
                              {db.short_description}
                            </Typography>
                            <Stack direction="row" spacing={2} style={{ paddingTop: 'var(--spacing-4)', borderTop: '1px solid var(--color-border-primary)' }}>
                              <Typography variant="caption" color="tertiary">
                                {db.queries.total_queries} queries
                              </Typography>
                              <Typography variant="caption" color="tertiary">
                                {parseFloat(db.files.total_data_size_mb).toLocaleString()} MB
                              </Typography>
                            </Stack>
                          </Stack>
                        </Paper>
                      </Link>
                    </GridItem>
                  ))}
                </Grid>
              ) : (
                <Paper elevation={0} variant="outlined" style={{ padding: 'var(--spacing-12)', textAlign: 'center' }}>
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
            </Stack>
          </Box>
        </Container>
      </Box>
    </>
  )
}
