'use client'

import { useEffect } from 'react'
import databaseContent from '@/lib/database-content.json'
import ClientScripts from './ClientScripts'
import { Container } from '@/components/design-system/layout/Container'
import { Box } from '@/components/design-system/layout/Box'

interface DatabaseContentProps {
  dbId: string
}

export default function DatabaseContent({ dbId }: DatabaseContentProps) {
  useEffect(() => {
    // Handle hash navigation on mount
    const handleHashNavigation = () => {
      const hash = window.location.hash
      if (hash) {
        const targetId = hash.replace('#', '')
        const element = document.getElementById(targetId)
        if (element) {
          setTimeout(() => {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }, 300)
        }
      }
    }

      // Initialize Mermaid after content is rendered
    const initMermaidAfterRender = () => {
      if (typeof (window as any).mermaid === 'undefined') {
        setTimeout(initMermaidAfterRender, 100)
        return
      }

      const mermaid = (window as any).mermaid
      
      // Find all Mermaid code blocks (both pre.language-mermaid and pre code.language-mermaid)
      const mermaidPreBlocks = document.querySelectorAll('pre.language-mermaid, pre.language-mmd')
      const mermaidCodeBlocks = document.querySelectorAll('pre code.language-mermaid, pre code.language-mmd')
      
      const totalBlocks = mermaidPreBlocks.length + mermaidCodeBlocks.length
      
      if (totalBlocks === 0) {
        console.log('No Mermaid blocks found in DOM')
        return
      }

      console.log(`Found ${totalBlocks} Mermaid block(s) to convert`)

      // Convert pre.language-mermaid blocks directly
      mermaidPreBlocks.forEach((preBlock, index) => {
        const codeElement = preBlock.querySelector('code')
        const code = codeElement 
          ? (codeElement.textContent || (codeElement as HTMLElement).innerText)
          : (preBlock.textContent || (preBlock as HTMLElement).innerText)
        
        if (!code || code.trim().length === 0) return

        const container = document.createElement('div')
        container.className = 'mermaid'
        container.setAttribute('data-mermaid-id', `mermaid-pre-${index}`)
        container.textContent = code.trim()

        preBlock.replaceWith(container)
      })

      // Convert pre code.language-mermaid blocks
      mermaidCodeBlocks.forEach((codeBlock, index) => {
        const code = codeBlock.textContent || (codeBlock as HTMLElement).innerText
        if (!code || code.trim().length === 0) return

        const container = document.createElement('div')
        container.className = 'mermaid'
        container.setAttribute('data-mermaid-id', `mermaid-code-${index}`)
        container.textContent = code.trim()

        // Replace the parent pre element
        const preElement = codeBlock.parentElement
        if (preElement && preElement.tagName === 'PRE') {
          preElement.replaceWith(container)
        } else {
          codeBlock.replaceWith(container)
        }
      })

      // Render all Mermaid diagrams after conversion
      setTimeout(() => {
        const mermaidDivs = document.querySelectorAll('.mermaid')
        if (mermaidDivs.length > 0) {
          console.log(`Rendering ${mermaidDivs.length} Mermaid diagram(s)`)
          try {
            if (typeof mermaid.contentLoaded === 'function') {
              // Mermaid v10+ API
              mermaid.contentLoaded()
            } else if (typeof mermaid.run === 'function') {
              // Older Mermaid API
              mermaid.run({
                querySelector: '.mermaid',
              })
            } else {
              console.error('Mermaid API not found')
            }
          } catch (error) {
            console.error('Error rendering Mermaid diagrams:', error)
          }
        } else {
          console.log('No .mermaid divs found after conversion')
        }
      }, 200)
    }

    // Re-highlight code after content is rendered
    const checkAndHighlight = () => {
      if (typeof window !== 'undefined' && (window as any).Prism) {
        // Ensure all SQL elements are properly marked
        document.querySelectorAll('pre[class*="sql"], code[class*="sql"]').forEach((element) => {
          if (!element.classList.contains('language-sql')) {
            element.classList.add('language-sql')
          }
        })
        // Highlight all code
        ;(window as any).Prism.highlightAll()
        handleHashNavigation()
        
        // Initialize Mermaid after Prism is done
        setTimeout(initMermaidAfterRender, 300)
      } else {
        // Prism not ready yet, retry
        setTimeout(checkAndHighlight, 100)
      }
    }
    
    // Wait for DOM to be ready, then check
    setTimeout(checkAndHighlight, 200)
  }, [dbId])

  const content = databaseContent[dbId as keyof typeof databaseContent]

  if (!content) {
    return (
      <>
        <ClientScripts />
        <Box component="main" className="main-content" style={{ padding: 'var(--spacing-8)' }}>
          <Container maxWidth="xl">
            <Box component="section">
              <Box component="header">
                <h1>Database Not Found</h1>
                <p>The database {dbId} could not be found.</p>
              </Box>
            </Box>
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
          <Box
            component="section"
            id={`${dbId}-section`}
            dangerouslySetInnerHTML={{ __html: content as string }}
          />
        </Container>
      </Box>
    </>
  )
}
