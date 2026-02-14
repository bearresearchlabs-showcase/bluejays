'use client'

import Link from 'next/link'
import { useEffect } from 'react'
import ClientScripts from './ClientScripts'
import databaseIndex from '@/lib/database-index.json'
import { Container } from '@/components/design-system/layout/Container'
import { Box } from '@/components/design-system/layout/Box'
import { Grid, GridItem } from '@/components/design-system/layout/Grid'
import { Paper } from '@/components/design-system/layout/Paper'
import { Stack } from '@/components/design-system/layout/Stack'
import { Typography } from '@/components/design-system/data-display/Typography'

const index = databaseIndex as {
  totalDatabases: number
  databases: { id: string; name: string; shortDescription: string; tableCount: number; queryCount: number }[]
}

export default function DatabasesContent() {
  useEffect(() => {
    const checkAndHighlight = () => {
      if (typeof window !== 'undefined' && (window as any).Prism) {
        (window as any).Prism.highlightAll()
      } else {
        setTimeout(checkAndHighlight, 100)
      }
    }
    setTimeout(checkAndHighlight, 200)
  }, [])

  return (
    <>
      <ClientScripts />
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Box component="section" id="databases">
            <Stack spacing={4}>
              <Box component="header">
                <Typography variant="h1">Available Databases</Typography>
                <Typography variant="body1" style={{ marginTop: 'var(--spacing-2)' }}>
                  Production databases db-6 through db-15. Sourced from systems used by businesses with{' '}
                  <strong>$1M+ ARR</strong>.
                </Typography>
              </Box>

              <Paper elevation={1} style={{ padding: 'var(--spacing-6)' }}>
                <Stack spacing={2}>
                  <Typography variant="body1"><strong>Total Databases:</strong> {index.totalDatabases}</Typography>
                  <Typography variant="body1"><strong>Database Range:</strong> db-6 through db-15</Typography>
                  <Typography variant="body1">
                    <strong>Source:</strong> Production systems; real-world implementations powering critical operations and paying customers.
                  </Typography>
                </Stack>
              </Paper>

              <Typography variant="h2">Database Catalog</Typography>
              <Grid container spacing={3}>
                {index.databases.map((db) => (
                  <GridItem key={db.id} xs={12} sm={6} md={4}>
                    <Link
                      href={`/db/${db.id}`}
                      style={{ textDecoration: 'none', display: 'block', height: '100%' }}
                    >
                      <Paper
                        elevation={1}
                        style={{
                          height: '100%',
                          padding: 'var(--spacing-4)',
                          cursor: 'pointer',
                          transition: 'all var(--transition-base)',
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
                        <Stack spacing={2}>
                          <Typography variant="h6">{db.id.toUpperCase()}</Typography>
                          <Typography variant="body1" fontWeight="medium">{db.name}</Typography>
                          {db.shortDescription && (
                            <Typography variant="body2" color="secondary">{db.shortDescription}</Typography>
                          )}
                          <Typography variant="caption" color="tertiary">
                            {db.tableCount} tables · {db.queryCount} queries
                          </Typography>
                        </Stack>
                      </Paper>
                    </Link>
                  </GridItem>
                ))}
              </Grid>
            </Stack>
          </Box>
        </Container>
      </Box>
    </>
  )
}
