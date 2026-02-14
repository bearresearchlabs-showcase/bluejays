'use client'

import { useState, useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import Link from 'next/link'
import { Drawer } from '@/components/design-system/navigation/Drawer'
import { Accordion } from '@/components/design-system/navigation/Accordion'
import { List, ListItem, ListItemButton, ListItemText } from '@/components/design-system/data-display/List'
import { Typography } from '@/components/design-system/data-display/Typography'
import { Box } from '@/components/design-system/layout/Box'
import { Stack } from '@/components/design-system/layout/Stack'
import { useMediaQuery } from '@/components/design-system/ThemeProvider'
import databaseIndex from '@/lib/database-index.json'

const databases = (databaseIndex as { databases: { id: string; name: string }[] }).databases

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const isMobile = useMediaQuery('(max-width: 899px)')
  const [drawerOpen, setDrawerOpen] = useState(!isMobile)
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    db6: true,
  })
  const [activeSection, setActiveSection] = useState<string>('overview')
  
  useEffect(() => {
    if (pathname?.includes('/docs')) {
      setActiveSection('docs')
    } else if (pathname?.includes('/metadata')) {
      setActiveSection('metadata')
    } else if (pathname?.includes('/db/')) {
      const hash = typeof window !== 'undefined' ? window.location.hash.replace('#', '') : ''
      if (hash) {
        setActiveSection(hash)
      } else {
        setActiveSection('overview')
      }
    }
  }, [pathname])

  useEffect(() => {
    if (typeof window !== 'undefined' && (window as any).Prism) {
      (window as any).Prism.highlightAll()
    }
  }, [])

  const toggleSection = (sectionId: string) => {
    setExpanded(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }))
  }

  const handleLinkClick = async (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const [path, hash] = href.split('#')
    const targetId = hash || ''
    
    // If we're not on the target page, navigate there first
    if (path && pathname !== path) {
      await router.push(path)
      // Wait for navigation to complete before scrolling
      setTimeout(() => {
        if (targetId) {
          setActiveSection(targetId)
          const findElement = (attempt = 0): void => {
            const element = document.getElementById(targetId)
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'start' })
              // Update URL hash without triggering navigation
              window.history.replaceState(null, '', `${path}#${targetId}`)
            } else if (attempt < 3) {
              setTimeout(() => findElement(attempt + 1), 100 * (attempt + 1))
            }
          }
          findElement()
        }
      }, 100)
    } else {
      // Already on the page, just scroll to the section
      if (targetId) {
        setActiveSection(targetId)
        const findElement = (attempt = 0): void => {
          const element = document.getElementById(targetId)
          if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' })
            // Update URL hash without triggering navigation
            window.history.replaceState(null, '', `${pathname}#${targetId}`)
          } else if (attempt < 3) {
            setTimeout(() => findElement(attempt + 1), 100 * (attempt + 1))
          }
        }
        findElement()
      }
    }
    
    if (isMobile) {
      setDrawerOpen(false)
    }
  }

  const drawerContent = (
    <Box style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box style={{ padding: 'var(--spacing-6)', borderBottom: '1px solid var(--color-border-primary)' }}>
        <Typography variant="h5" style={{ marginBottom: 'var(--spacing-1)' }}>
          Database Docs
        </Typography>
        <Typography variant="body2" color="secondary">
          Production Databases
        </Typography>
      </Box>

      {/* Navigation Content */}
      <Box style={{ flex: 1, overflowY: 'auto', padding: 'var(--spacing-2)' }}>
        <Stack spacing={1}>
          {/* All Databases Link */}
          <Link
            href="/databases"
            style={{ textDecoration: 'none' }}
            onClick={() => isMobile && setDrawerOpen(false)}
          >
            <ListItemButton selected={pathname === '/databases'}>
              <ListItemText primary="All Databases" />
            </ListItemButton>
          </Link>

          {/* Database Sections */}
          {databases.map((db) => {
            const queriesExpanded = expanded[`${db.id}-queries`] ?? false
            
            return (
              <Accordion
                key={db.id}
                expanded={expanded[db.id] ?? false}
                onChange={(expanded) => toggleSection(db.id)}
              >
                <Box>
                  <Link
                    href={`/db/${db.id}`}
                    style={{ textDecoration: 'none', color: 'inherit' }}
                    onClick={() => isMobile && setDrawerOpen(false)}
                  >
                    <ListItemButton>
                      <ListItemText 
                        primary={db.id.toUpperCase()}
                      />
                    </ListItemButton>
                  </Link>
                  
                  {expanded[db.id] && (
                    <List dense disablePadding>
                      <Link
                        href={`/db/${db.id}#${db.id}-overview`}
                        style={{ textDecoration: 'none', color: 'inherit' }}
                        onClick={(e) => handleLinkClick(e as any, `/db/${db.id}#${db.id}-overview`)}
                      >
                        <ListItemButton 
                          selected={pathname === `/db/${db.id}` && activeSection === `${db.id}-overview`}
                          style={{ paddingLeft: 'var(--spacing-8)' }}
                        >
                          <ListItemText primary="Overview" />
                        </ListItemButton>
                      </Link>
                      
                      <Link
                        href={`/db/${db.id}#${db.id}-schema`}
                        style={{ textDecoration: 'none', color: 'inherit' }}
                        onClick={(e) => handleLinkClick(e as any, `/db/${db.id}#${db.id}-schema`)}
                      >
                        <ListItemButton 
                          selected={pathname === `/db/${db.id}` && activeSection === `${db.id}-schema`}
                          style={{ paddingLeft: 'var(--spacing-8)' }}
                        >
                          <ListItemText primary="Schema" />
                        </ListItemButton>
                      </Link>
                      
                      {/* Queries Subsection */}
                      <Accordion
                        expanded={queriesExpanded}
                        onChange={(expanded) => toggleSection(`${db.id}-queries`)}
                      >
                        <Box>
                          <ListItemButton
                            onClick={() => toggleSection(`${db.id}-queries`)}
                            style={{ paddingLeft: 'var(--spacing-8)' }}
                          >
                            <ListItemText primary="Queries" />
                          </ListItemButton>
                          
                          {queriesExpanded && (
                            <List dense disablePadding>
                              <Link
                                href={`/db/${db.id}#${db.id}-queries`}
                                style={{ textDecoration: 'none', color: 'inherit' }}
                                onClick={(e) => handleLinkClick(e as any, `/db/${db.id}#${db.id}-queries`)}
                              >
                                <ListItemButton 
                                  selected={pathname === `/db/${db.id}` && activeSection === `${db.id}-queries`}
                                  style={{ paddingLeft: 'var(--spacing-12)' }}
                                >
                                  <ListItemText primary="All Queries" />
                                </ListItemButton>
                              </Link>
                              {Array.from({ length: 30 }, (_, i) => i + 1).map((num) => {
                                const queryId = `${db.id}-query-${num}`
                                return (
                                  <Link
                                    key={queryId}
                                    href={`/db/${db.id}#${queryId}`}
                                    style={{ textDecoration: 'none', color: 'inherit' }}
                                    onClick={(e) => handleLinkClick(e as any, `/db/${db.id}#${queryId}`)}
                                  >
                                    <ListItemButton 
                                      selected={pathname === `/db/${db.id}` && activeSection === queryId}
                                      style={{ paddingLeft: 'var(--spacing-12)' }}
                                    >
                                      <ListItemText primary={`Query ${num}`} />
                                    </ListItemButton>
                                  </Link>
                                )
                              })}
                            </List>
                          )}
                        </Box>
                      </Accordion>
                      
                      <Link
                        href={`/db/${db.id}/docs`}
                        style={{ textDecoration: 'none', color: 'inherit' }}
                        onClick={() => isMobile && setDrawerOpen(false)}
                      >
                        <ListItemButton 
                          selected={pathname === `/db/${db.id}/docs`}
                          style={{ paddingLeft: 'var(--spacing-8)' }}
                        >
                          <ListItemText primary="Docs" />
                        </ListItemButton>
                      </Link>
                      
                      <Link
                        href={`/db/${db.id}/metadata`}
                        style={{ textDecoration: 'none', color: 'inherit' }}
                        onClick={() => isMobile && setDrawerOpen(false)}
                      >
                        <ListItemButton 
                          selected={pathname === `/db/${db.id}/metadata`}
                          style={{ paddingLeft: 'var(--spacing-8)' }}
                        >
                          <ListItemText primary="Metadata" />
                        </ListItemButton>
                      </Link>
                    </List>
                  )}
                </Box>
              </Accordion>
            )
          })}
        </Stack>
      </Box>
    </Box>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      {isMobile && (
        <Box
          style={{
            position: 'fixed',
            top: 'var(--spacing-4)',
            left: 'var(--spacing-4)',
            zIndex: 1000,
          }}
        >
          <button
            onClick={() => setDrawerOpen(true)}
            style={{
              padding: 'var(--spacing-2)',
              background: 'var(--color-bg-elevated)',
              border: '1px solid var(--color-border-primary)',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer',
            }}
          >
            ☰
          </button>
        </Box>
      )}

      {/* Drawer */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        variant={isMobile ? 'temporary' : 'permanent'}
        anchor="left"
        width={280}
      >
        {drawerContent}
      </Drawer>
    </>
  )
}
