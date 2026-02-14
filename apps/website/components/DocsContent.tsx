'use client'

import { useEffect, useState } from 'react'
import ClientScripts from './ClientScripts'
import { Container } from '@/components/design-system/layout/Container'
import { Box } from '@/components/design-system/layout/Box'
import { Stack } from '@/components/design-system/layout/Stack'
import { Paper } from '@/components/design-system/layout/Paper'
import { Typography } from '@/components/design-system/data-display/Typography'
import { Table, TableHead, TableBody, TableRow, TableCell } from '@/components/design-system/data-display/Table'
import { Loading } from '@/components/design-system/feedback/Loading'
import { Alert } from '@/components/design-system/feedback/Alert'

interface DocsContentProps {
  dbId: string
}

interface DeliverableData {
  database: {
    id: string
    name: string
    description: string
    created_date: string
    version: string
  }
  schema: {
    total_tables: number
    tables: Array<{
      name: string
      description: string
      columns: Array<{
        name: string
        data_type: string
        constraints: string
        description: string
      }>
    }>
  }
  queries: Array<{
    number: number
    title: string
    description: string
    sql: string
  }>
}

export default function DocsContent({ dbId }: DocsContentProps) {
  const [data, setData] = useState<DeliverableData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadDeliverable = async () => {
      try {
        // Convert db6 to db-6 format for file path
        const dbNumber = dbId.replace('db', 'db-')
        const response = await fetch(`/api/deliverable/${dbId}`)
        
        if (!response.ok) {
          throw new Error(`Failed to load deliverable for ${dbId}`)
        }
        
        const jsonData = await response.json()
        setData(jsonData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load deliverable')
      } finally {
        setLoading(false)
      }
    }

    loadDeliverable()
  }, [dbId])

  if (loading) {
    return (
      <>
        <ClientScripts />
        <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Stack spacing={4} alignItems="center">
              <Loading />
              <Typography variant="h5">Loading Documentation...</Typography>
            </Stack>
          </Container>
        </Box>
      </>
    )
  }

  if (error || !data) {
    return (
      <>
        <ClientScripts />
        <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Stack spacing={4}>
              <Typography variant="h1">Documentation Not Found</Typography>
              <Alert severity="error">
                {error || `The documentation for ${dbId} could not be loaded.`}
              </Alert>
            </Stack>
          </Container>
        </Box>
      </>
    )
  }

  return (
    <>
      <ClientScripts />
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Box component="section" id={`${dbId}-docs`}>
            <Stack spacing={4}>
              <Box component="header">
                <Typography variant="h1">{data.database.name} - Documentation</Typography>
                <Stack spacing={1} style={{ marginTop: 'var(--spacing-2)' }}>
                  <Typography variant="body1"><strong>Database ID:</strong> {data.database.id}</Typography>
                  <Typography variant="body1"><strong>Version:</strong> {data.database.version}</Typography>
                  <Typography variant="body1"><strong>Created:</strong> {data.database.created_date}</Typography>
                </Stack>
              </Box>

              <Paper elevation={1} style={{ padding: 'var(--spacing-6)', marginTop: 'var(--spacing-4)' }}>
                <Stack spacing={3}>
                  <Typography variant="h2">Database Description</Typography>
                  <Box
                    style={{
                      lineHeight: '1.6',
                      whiteSpace: 'pre-wrap',
                      wordWrap: 'break-word'
                    }}
                    dangerouslySetInnerHTML={{
                      __html: data.database.description
                        .replace(/\n\n/g, '</p><p>')
                        .replace(/\n/g, '<br />')
                        .replace(/^\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    }}
                  />
                </Stack>
              </Paper>

              <Box component="section" style={{ marginTop: 'var(--spacing-4)' }}>
                <Stack spacing={3}>
                  <Typography variant="h2">Schema Overview</Typography>
                  <Typography variant="body1"><strong>Total Tables:</strong> {data.schema.total_tables}</Typography>

                  {data.schema.tables.map((table, idx) => (
                    <Paper key={idx} elevation={1} style={{ padding: 'var(--spacing-4)', marginTop: 'var(--spacing-4)' }}>
                      <Stack spacing={2}>
                        <Typography variant="h3">{table.name}</Typography>
                        <Typography variant="body2">{table.description}</Typography>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Column Name</TableCell>
                              <TableCell>Data Type</TableCell>
                              <TableCell>Constraints</TableCell>
                              <TableCell>Description</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {table.columns.map((column, colIdx) => (
                              <TableRow key={colIdx}>
                                <TableCell><code>{column.name}</code></TableCell>
                                <TableCell><code>{column.data_type}</code></TableCell>
                                <TableCell><code>{column.constraints}</code></TableCell>
                                <TableCell>{column.description}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </Stack>
                    </Paper>
                  ))}
                </Stack>
              </Box>

              <Box component="section" style={{ marginTop: 'var(--spacing-4)' }}>
                <Stack spacing={3}>
                  <Typography variant="h2">Queries Overview</Typography>
                  <Typography variant="body1"><strong>Total Queries:</strong> {data.queries.length}</Typography>

                  {data.queries && data.queries.length > 0 ? (
                    <Stack spacing={3}>
                      {data.queries.map((query) => (
                        <Paper key={query.number} elevation={1} style={{ padding: 'var(--spacing-4)' }}>
                          <Stack spacing={2}>
                            <Typography variant="h3">Query {query.number}: {query.title || 'Untitled Query'}</Typography>
                            {query.description && <Typography variant="body2">{query.description}</Typography>}
                            {query.sql && (
                              <Box className="code-block">
                                <pre className="language-sql"><code className="language-sql">{query.sql}</code></pre>
                              </Box>
                            )}
                          </Stack>
                        </Paper>
                      ))}
                    </Stack>
                  ) : (
                    <Typography variant="body1">No queries available in deliverable data.</Typography>
                  )}
                </Stack>
              </Box>
            </Stack>
          </Box>
        </Container>
      </Box>
    </>
  )
}
