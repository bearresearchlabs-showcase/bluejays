'use client'

import { useEffect, useState } from 'react'
import ClientScripts from './ClientScripts'
import { Container } from '@/components/design-system/layout/Container'
import { Box } from '@/components/design-system/layout/Box'
import { Stack } from '@/components/design-system/layout/Stack'
import { Paper } from '@/components/design-system/layout/Paper'
import { Typography } from '@/components/design-system/data-display/Typography'
import { Loading } from '@/components/design-system/feedback/Loading'
import { Alert } from '@/components/design-system/feedback/Alert'
import Button from '@/components/design-system/Button'

interface MetadataContentProps {
  dbId: string
}

export default function MetadataContent({ dbId }: MetadataContentProps) {
  const [metadata, setMetadata] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const response = await fetch(`/api/metadata/${dbId}`)
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: 'Failed to load metadata' }))
          setError(errorData.error || `Failed to load metadata: ${response.status}`)
          setLoading(false)
          return
        }
        
        const jsonData = await response.json()
        setMetadata(jsonData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load metadata')
      } finally {
        setLoading(false)
      }
    }

    loadMetadata()
  }, [dbId])

  useEffect(() => {
    // Re-highlight code after content is rendered
    const checkAndHighlight = () => {
      if (typeof window !== 'undefined' && (window as any).Prism) {
        (window as any).Prism.highlightAll()
      } else {
        setTimeout(checkAndHighlight, 100)
      }
    }
    
    if (metadata && isExpanded) {
      setTimeout(checkAndHighlight, 200)
    }
  }, [metadata, isExpanded])

  const handleToggle = () => {
    setIsExpanded(!isExpanded)
  }

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (metadata) {
      const jsonString = JSON.stringify(metadata, null, 2)
      try {
        await navigator.clipboard.writeText(jsonString)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy:', err)
      }
    }
  }

  if (loading) {
    return (
      <>
        <ClientScripts />
        <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Stack spacing={4} alignItems="center">
              <Loading />
              <Typography variant="h5">Loading Metadata...</Typography>
            </Stack>
          </Container>
        </Box>
      </>
    )
  }

  if (error) {
    return (
      <>
        <ClientScripts />
        <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Box component="section" id={`${dbId}-metadata`}>
              <Stack spacing={4}>
                <Typography variant="h1">{dbId.toUpperCase()} - Metadata</Typography>
                <Alert severity="error">Error: {error}</Alert>
              </Stack>
            </Box>
          </Container>
        </Box>
      </>
    )
  }

  if (!metadata) {
    return (
      <>
        <ClientScripts />
        <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Box component="section" id={`${dbId}-metadata`}>
              <Stack spacing={4}>
                <Typography variant="h1">{dbId.toUpperCase()} - Metadata</Typography>
                <Typography variant="body1">No metadata available.</Typography>
              </Stack>
            </Box>
          </Container>
        </Box>
      </>
    )
  }

  const fileName = `${dbId.replace('db', 'db-')}_deliverable.json`

  return (
    <>
      <ClientScripts />
      <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
        <Container maxWidth="xl">
          <Box component="section" id={`${dbId}-metadata`}>
            <Stack spacing={4}>
              <Typography variant="h1">{dbId.toUpperCase()} - Metadata</Typography>

              <Paper elevation={1} variant="outlined">
                <Box>
                  <Box
                    onClick={handleToggle}
                    style={{
                      cursor: 'pointer',
                      padding: 'var(--spacing-4)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Typography variant="h6">{fileName}</Typography>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => void handleCopy(e)}
                      >
                        {copied ? 'Copied!' : 'Copy'}
                      </Button>
                      <Typography variant="body2">{isExpanded ? '▲' : '▼'}</Typography>
                    </Stack>
                  </Box>
                  {isExpanded && (
                    <Box style={{ padding: 'var(--spacing-4)', borderTop: '1px solid var(--color-border-primary)' }}>
                      <pre className="language-json"><code className="language-json">
                        {JSON.stringify(metadata, null, 2)}
                      </code></pre>
                    </Box>
                  )}
                </Box>
              </Paper>
            </Stack>
          </Box>
        </Container>
      </Box>
    </>
  )
}
