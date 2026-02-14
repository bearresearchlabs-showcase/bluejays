'use client'

import { useEffect } from 'react'

export default function ClientScripts() {
  useEffect(() => {
    // Wait for Prism.js to load
    const waitForPrism = () => {
      if (typeof (window as any).Prism === 'undefined') {
        setTimeout(() => {
          initializeAll()
        }, 500)
      } else {
        initializeAll()
      }
    }

    // Accordion functionality for navigation
    const initAccordions = () => {
      document.querySelectorAll('.nav-accordion-header').forEach((header) => {
        header.addEventListener('click', function (this: HTMLElement) {
          const section = this.getAttribute('data-section')
          if (!section) return
          
          const content = document.getElementById(section + '-content')
          if (!content) return

          const isExpanded = content.classList.contains('expanded')
          
          if (isExpanded) {
            content.classList.remove('expanded')
            this.classList.remove('active')
          } else {
            content.classList.add('expanded')
            this.classList.add('active')
          }
        })
      })
    }

    // Initialize default expanded sections (DB-6 and Overview)
    const initDefaultExpanded = () => {
      const db6Content = document.getElementById('db6-content')
      const overviewContent = document.getElementById('db6-overview-content')
      const db6Header = document.querySelector('[data-section="db6"]')
      const overviewHeader = document.querySelector('[data-section="db6-overview"]')
      
      if (db6Content && db6Header) {
        db6Content.classList.add('expanded')
        db6Header.classList.add('active')
      }
      
      if (overviewContent && overviewHeader) {
        overviewContent.classList.add('expanded')
        overviewHeader.classList.add('active')
      }
    }

    // Highlight SQL code blocks
    const highlightAllSQL = () => {
      if (typeof (window as any).Prism === 'undefined') return

      // First, ensure all SQL elements have the language-sql class
      document.querySelectorAll('.code-block code, pre.language-sql, code.language-sql, pre[class*="sql"]').forEach((element) => {
        const text = element.textContent || (element as HTMLElement).innerText
        if (
          text.match(/\b(SELECT|FROM|WHERE|JOIN|WITH|INSERT|UPDATE|CREATE|ALTER|DELETE|DROP|CASE|WHEN|THEN|GROUP BY|ORDER BY|HAVING|UNION|EXCEPT|INTERSECT|CTE|RECURSIVE)\b/i) ||
          text.match(/\b(COUNT|SUM|AVG|MAX|MIN|DATE_TRUNC|EXTRACT|ST_|CAST|CONVERT)\s*\(/i) ||
          text.match(/--.*$|\/\*[\s\S]*?\*\//m) ||
          element.classList.contains('language-sql')
        ) {
          // For pre elements, ensure they have language-sql class
          if (element.tagName === 'PRE' && !element.classList.contains('language-sql')) {
            element.classList.add('language-sql')
          }
          // For code elements, ensure they have language-sql class
          if (element.tagName === 'CODE' && !element.classList.contains('language-sql')) {
            element.classList.add('language-sql')
          }
          // Store original text
          if (!element.getAttribute('data-original-text')) {
            element.setAttribute('data-original-text', text)
          }
        }
      })

      // Handle pre.language-sql elements - ensure they have a code child
      document.querySelectorAll('pre.language-sql').forEach((preElement) => {
        let codeElement = preElement.querySelector('code')
        if (!codeElement) {
          // Create a code element if it doesn't exist
          codeElement = document.createElement('code')
          codeElement.className = 'language-sql'
          codeElement.textContent = preElement.textContent
          preElement.textContent = ''
          preElement.appendChild(codeElement)
        } else {
          // Ensure the code element has language-sql class
          if (!codeElement.classList.contains('language-sql')) {
            codeElement.classList.add('language-sql')
          }
        }
      })

      // Use highlightAll for better coverage - it will highlight all elements with language-* classes
      ;(window as any).Prism.highlightAll()
    }

    // Highlight SQL within JSON strings
    const highlightSQLInJSON = (codeElement: Element) => {
      if (!codeElement || typeof (window as any).Prism === 'undefined') return
      
      try {
        const originalText = codeElement.getAttribute('data-original-text') || 
                            (codeElement.textContent || (codeElement as HTMLElement).innerText)
        
        if (!originalText || !originalText.includes('"sql"')) {
          return
        }
        
        const sqlPattern = /"sql"\s*:\s*"((?:[^"\\]|\\.|\\n)*)"/g
        const sqlMatches: Array<{ originalValue: string; highlightedValue: string }> = []
        let match
        
        while ((match = sqlPattern.exec(originalText)) !== null) {
          const sqlContent = match[1]
          const unescapedSQL = sqlContent
            .replace(/\\n/g, '\n')
            .replace(/\\t/g, '\t')
            .replace(/\\"/g, '"')
            .replace(/\\\\/g, '\\')
          
          const tempCode = document.createElement('code')
          tempCode.className = 'language-sql'
          tempCode.textContent = unescapedSQL
          ;(window as any).Prism.highlightElement(tempCode)
          
          const highlightedSQL = tempCode.innerHTML
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
          
          sqlMatches.push({
            originalValue: sqlContent,
            highlightedValue: highlightedSQL
          })
        }
        
        if (sqlMatches.length > 0) {
          let html = codeElement.innerHTML
          sqlMatches.forEach((sqlMatch) => {
            const escapedOriginalValue = sqlMatch.originalValue
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
            
            const escapedForRegex = escapedOriginalValue.replace(/[.*+?^${}()|[\]\\]/g, (match) => '\\' + match)
            const stringTokenPattern = new RegExp(
              '("sql"[^"]*"\\s*:\\s*"[^"]*?)' + 
              escapedForRegex + 
              '([^"]*")',
              'g'
            )
            
            html = html.replace(stringTokenPattern, (fullMatch, prefix, suffix) => {
              return prefix + sqlMatch.highlightedValue + suffix
            })
          })
          codeElement.innerHTML = html
        }
      } catch (error) {
        console.error('Error in highlightSQLInJSON:', error)
      }
    }

    // Highlight JSON element
    const highlightJsonElement = (codeElement: Element) => {
      if (!codeElement) return
      if (typeof (window as any).Prism === 'undefined') return
      
      if (!codeElement.classList.contains('language-json')) {
        codeElement.classList.add('language-json')
      }
      
      if (!codeElement.hasAttribute('data-original-text')) {
        const originalText = codeElement.textContent || (codeElement as HTMLElement).innerText
        if (originalText) {
          codeElement.setAttribute('data-original-text', originalText)
        }
      }
      
      ;(window as any).Prism.highlightElement(codeElement)
      highlightSQLInJSON(codeElement)
    }

    // Highlight JSON code blocks
    const highlightAllJSON = () => {
      if (typeof (window as any).Prism === 'undefined') return

      document.querySelectorAll('.json-block .json-content code').forEach((codeElement) => {
        const text = codeElement.textContent || (codeElement as HTMLElement).innerText
        if (!codeElement.getAttribute('data-original-text')) {
          codeElement.setAttribute('data-original-text', text)
        }
        if (text.trim().match(/^[\s\n]*(?:\{|\[)/)) {
          if (!codeElement.classList.contains('language-json')) {
            codeElement.classList.add('language-json')
          }
          highlightJsonElement(codeElement)
        }
      })
    }

    // JSON toggle functionality
    const toggleJsonFunc = function (header: HTMLElement) {
      try {
        const content = header.nextElementSibling as HTMLElement
        if (!content) {
          console.warn('toggleJson: No content element found')
          return
        }
        
        const codeElement = content.querySelector('code')
        const isExpanded = content.classList.contains('expanded')
        
        if (isExpanded) {
          content.classList.remove('expanded')
          header.classList.remove('active')
          requestAnimationFrame(() => {
            content.style.maxHeight = ''
            content.style.padding = ''
          })
        } else {
          content.style.maxHeight = ''
          content.style.padding = ''
          requestAnimationFrame(() => {
            content.classList.add('expanded')
            header.classList.add('active')
          })
          
          if (codeElement) {
            const currentText = codeElement.textContent || (codeElement as HTMLElement).innerText
            if (currentText && (currentText.includes('...') || currentText.length < 2000)) {
              // Could load full JSON here if needed
            } else {
              highlightJsonElement(codeElement)
            }
            setTimeout(() => {
              highlightAllJSON()
              highlightAllSQL()
            }, 150)
          }
        }
      } catch (error) {
        console.error('Error in toggleJson:', error)
      }
    }
    
    // Make toggleJson globally accessible
    ;(window as any).toggleJson = toggleJsonFunc

    // Initialize JSON accordions
    const initAllJsonAccordions = () => {
      const jsonHeaders = document.querySelectorAll('.json-header[data-json-toggle="true"], .json-header')
      jsonHeaders.forEach((header) => {
        const htmlHeader = header as HTMLElement
        htmlHeader.removeAttribute('onclick')
        htmlHeader.style.cursor = 'pointer'
        
        if (!htmlHeader.hasAttribute('data-listener-attached')) {
          htmlHeader.addEventListener('click', function (e) {
            e.preventDefault()
            e.stopPropagation()
            if (typeof toggleJsonFunc === 'function') {
              toggleJsonFunc(this)
            }
          })
          htmlHeader.setAttribute('data-listener-attached', 'true')
        }
        
        const content = htmlHeader.nextElementSibling as HTMLElement
        if (content && !content.classList.contains('expanded')) {
          content.style.maxHeight = ''
          content.style.padding = ''
        }
      })
    }

    // Copy to clipboard function
    const copyToClipboard = async (text: string, button: HTMLElement) => {
      try {
        await navigator.clipboard.writeText(text)
        button.textContent = 'Copied!'
        button.classList.add('copied')
        setTimeout(() => {
          button.textContent = 'Copy'
          button.classList.remove('copied')
        }, 2000)
      } catch (err) {
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.opacity = '0'
        textArea.style.left = '-9999px'
        document.body.appendChild(textArea)
        textArea.select()
        try {
          document.execCommand('copy')
          button.textContent = 'Copied!'
          button.classList.add('copied')
          setTimeout(() => {
            button.textContent = 'Copy'
            button.classList.remove('copied')
          }, 2000)
        } catch (err) {
          button.textContent = 'Failed'
          setTimeout(() => {
            button.textContent = 'Copy'
          }, 2000)
        }
        document.body.removeChild(textArea)
      }
    }

    // Add copy buttons to code blocks
    const addCopyButtons = () => {
      document.querySelectorAll('.code-block').forEach((block) => {
        if (block.querySelector('.copy-button')) return
        
        const button = document.createElement('button')
        button.className = 'copy-button'
        button.textContent = 'Copy'
        button.setAttribute('aria-label', 'Copy SQL code')
        
        button.addEventListener('click', async (e) => {
          e.stopPropagation()
          const codeElement = block.querySelector('code')
          const code = codeElement
            ? (codeElement.getAttribute('data-original-text') || codeElement.textContent || (codeElement as HTMLElement).innerText)
            : ''
          await copyToClipboard(code, button)
        })
        
        block.appendChild(button)
      })
      
      document.querySelectorAll('.json-block').forEach((block) => {
        const jsonContent = block.querySelector('.json-content') as HTMLElement
        if (!jsonContent || jsonContent.querySelector('.copy-button')) return
        
        const button = document.createElement('button')
        button.className = 'copy-button'
        button.textContent = 'Copy'
        button.setAttribute('aria-label', 'Copy JSON')
        
        button.addEventListener('click', async (e) => {
          e.stopPropagation()
          const codeElement = jsonContent.querySelector('code')
          let code = ''
          if (codeElement) {
            const originalText = codeElement.getAttribute('data-original-text')
            code = originalText || codeElement.textContent || (codeElement as HTMLElement).innerText
          } else {
            code = jsonContent.textContent || (jsonContent as HTMLElement).innerText
          }
          await copyToClipboard(code, button)
        })
        
        jsonContent.appendChild(button)
      })
    }

    // Scroll spy functionality with throttling
    const initScrollSpy = () => {
      const sections = document.querySelectorAll('section[id], .table-card[id], .query-card[id], header[id], h1[id], h2[id], h3[id]')
      const navLinks = document.querySelectorAll('.nav-link[href^="#"]')

      const updateActiveNav = () => {
        let currentSection = ''
        const scrollPosition = window.scrollY + 150
        
        sections.forEach((section) => {
          const sectionTop = (section as HTMLElement).offsetTop
          const sectionHeight = (section as HTMLElement).offsetHeight
          const sectionId = section.getAttribute('id')
          
          if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            currentSection = sectionId || ''
          }
        })
        
        navLinks.forEach((link) => {
          link.classList.remove('active')
          const href = link.getAttribute('href')
          if (
            href === '#' + currentSection ||
            (currentSection && currentSection.startsWith('table-') && href?.includes('schema')) ||
            (currentSection && currentSection.startsWith('query-') && href?.includes('queries'))
          ) {
            link.classList.add('active')
          }
        })
      }
      
      let ticking = false
      window.addEventListener('scroll', () => {
        if (!ticking) {
          window.requestAnimationFrame(() => {
            updateActiveNav()
            ticking = false
          })
          ticking = true
        }
      })
      
      updateActiveNav()
    }

    // Initialize Mermaid.js for ER diagrams
    // Note: This is called from ClientScripts, but DatabaseContent also has its own init
    // DatabaseContent's init runs after content is injected, which is more reliable
    const initMermaid = () => {
      if (typeof (window as any).mermaid === 'undefined') {
        setTimeout(initMermaid, 100)
        return
      }
      
      // Only initialize if not already initialized
      if ((window as any).mermaid.initialized) {
        return
      }

      // Configure Mermaid
      ;(window as any).mermaid.initialize({
        startOnLoad: false, // We'll render manually
        theme: 'dark',
        themeVariables: {
          primaryColor: '#1e1e1e',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#333333',
          lineColor: '#4a9eff',
          secondaryColor: '#2d2d2d',
          tertiaryColor: '#1e1e1e',
          background: '#000000',
          mainBkg: '#1e1e1e',
          secondBkg: '#2d2d2d',
          textColor: '#ffffff',
          edgeLabelBackground: '#1e1e1e',
          clusterBkg: '#2d2d2d',
          clusterBorder: '#4a9eff',
          defaultLinkColor: '#4a9eff',
          titleColor: '#ffffff',
          actorBorder: '#4a9eff',
          actorBkg: '#1e1e1e',
          actorTextColor: '#ffffff',
          actorLineColor: '#4a9eff',
          signalColor: '#ffffff',
          signalTextColor: '#ffffff',
          labelBoxBkgColor: '#1e1e1e',
          labelBoxBorderColor: '#4a9eff',
          labelTextColor: '#ffffff',
          loopTextColor: '#ffffff',
          noteBorderColor: '#4a9eff',
          noteBkgColor: '#2d2d2d',
          noteTextColor: '#ffffff',
          activationBorderColor: '#4a9eff',
          activationBkgColor: '#2d2d2d',
          sequenceNumberColor: '#ffffff',
          sectionBkgColor: '#1e1e1e',
          altSectionBkgColor: '#2d2d2d',
          sectionBorderColor: '#4a9eff',
          sectionBkgColor2: '#1e1e1e',
          excludeBkgColor: '#1e1e1e',
          taskBorderColor: '#4a9eff',
          taskBkgColor: '#1e1e1e',
          taskTextLightColor: '#ffffff',
          taskTextColor: '#ffffff',
          taskTextDarkColor: '#ffffff',
          taskTextOutsideColor: '#ffffff',
          taskTextClickableColor: '#4a9eff',
          activeTaskBorderColor: '#4a9eff',
          activeTaskBkgColor: '#2d2d2d',
          gridColor: '#333333',
          doneTaskBkgColor: '#1e1e1e',
          doneTaskBorderColor: '#666666',
          critBorderColor: '#ff6b6b',
          critBkgColor: '#2d2d2d',
          taskTextCriticalColor: '#ff6b6b',
          todayLineColor: '#4a9eff',
          labelColor: '#ffffff',
          errorBkgColor: '#ff6b6b',
          errorTextColor: '#ffffff',
        },
        er: {
          fontSize: 14,
          padding: 10,
        },
        flowchart: {
          fontSize: 14,
          padding: 10,
        },
        securityLevel: 'loose',
      })

      // Find all mermaid code blocks and render them
      const mermaidBlocks = document.querySelectorAll('pre code.language-mermaid, pre code.language-mmd, code.language-mermaid, code.language-mmd')
      mermaidBlocks.forEach((block, index) => {
        const code = block.textContent || (block as HTMLElement).innerText
        if (!code || code.trim().length === 0) return

        // Create a container for the diagram
        const container = document.createElement('div')
        container.className = 'mermaid'
        container.setAttribute('data-mermaid-id', `mermaid-${index}`)
        
        // Replace the code block with the container
        const preElement = block.parentElement
        if (preElement && preElement.tagName === 'PRE') {
          preElement.replaceWith(container)
          container.textContent = code.trim()
        }
      })

      // Also handle pre.language-mermaid blocks directly
      const mermaidPreBlocks = document.querySelectorAll('pre.language-mermaid, pre.language-mmd')
      mermaidPreBlocks.forEach((preBlock, index) => {
        const code = preBlock.textContent || (preBlock as HTMLElement).innerText
        if (!code || code.trim().length === 0) return

        const container = document.createElement('div')
        container.className = 'mermaid'
        container.setAttribute('data-mermaid-id', `mermaid-pre-${index}`)
        
        preBlock.replaceWith(container)
        container.textContent = code.trim()
      })

      // Render all Mermaid diagrams after a short delay to ensure DOM is ready
      setTimeout(() => {
        try {
          const mermaid = (window as any).mermaid
          const mermaidDivs = document.querySelectorAll('.mermaid')
          
          if (mermaidDivs.length === 0) {
            console.log('No Mermaid diagrams found to render')
            return
          }
          
          console.log(`Found ${mermaidDivs.length} Mermaid diagram(s) to render`)
          
          // Mermaid v10+ uses contentLoaded() or run()
          if (typeof mermaid.contentLoaded === 'function') {
            // Mermaid v10+ API - contentLoaded() processes all .mermaid divs
            mermaid.contentLoaded()
          } else if (typeof mermaid.run === 'function') {
            // Older Mermaid API
            mermaid.run({
              querySelector: '.mermaid',
            })
          } else {
            // Fallback: try to render each diagram individually
            mermaidDivs.forEach((div, index) => {
              const code = div.textContent || (div as HTMLElement).innerText
              if (code && code.trim()) {
                try {
                  mermaid.render(`mermaid-diagram-${index}`, code.trim(), (svgCode: string) => {
                    div.innerHTML = svgCode
                  })
                } catch (err) {
                  console.error(`Error rendering Mermaid diagram ${index}:`, err)
                }
              }
            })
          }
        } catch (error) {
          console.error('Error running Mermaid:', error)
        }
      }, 500) // Wait 500ms for DOM to be fully ready
    }

    // Initialize all functionality
    const initializeAll = () => {
      initAccordions()
      initDefaultExpanded()
      highlightAllSQL()
      highlightAllJSON()
      initAllJsonAccordions()
      addCopyButtons()
      initScrollSpy()
      initMermaid()
      
      // Highlight initial JSON preview
      const jsonCode = document.getElementById('json-code')
      if (jsonCode) {
        const originalText = jsonCode.textContent || (jsonCode as HTMLElement).innerText
        if (originalText && !jsonCode.hasAttribute('data-original-text')) {
          jsonCode.setAttribute('data-original-text', originalText)
        }
        jsonCode.classList.add('language-json')
        if (typeof (window as any).Prism !== 'undefined') {
          ;(window as any).Prism.highlightElement(jsonCode)
          highlightSQLInJSON(jsonCode)
        }
      }
      
      // MutationObserver for dynamically added content
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.addedNodes.length) {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === 1) {
                const codeBlocks = (node as Element).querySelectorAll?.('.code-block code') || []
                codeBlocks.forEach((codeElement) => {
                  const text = codeElement.textContent || (codeElement as HTMLElement).innerText
                  if (text.match(/\b(SELECT|FROM|WHERE|JOIN|WITH|INSERT|UPDATE|CREATE|ALTER|DELETE|DROP)\b/i)) {
                    if (!codeElement.classList.contains('language-sql')) {
                      codeElement.classList.add('language-sql')
                    }
                    if (typeof (window as any).Prism !== 'undefined') {
                      ;(window as any).Prism.highlightElement(codeElement)
                    }
                  }
                })
                
                const jsonCodes = (node as Element).querySelectorAll?.('.json-content code') || []
                jsonCodes.forEach((codeElement) => {
                  if (!codeElement.classList.contains('language-json')) {
                    codeElement.classList.add('language-json')
                    if (typeof (window as any).Prism !== 'undefined') {
                      ;(window as any).Prism.highlightElement(codeElement)
                      highlightSQLInJSON(codeElement)
                    }
                  }
                })
              }
            })
          }
        })
      })
      
      observer.observe(document.body, {
        childList: true,
        subtree: true
      })
    }

    // Start initialization
    waitForPrism()

    return () => {
      // Cleanup if needed
    }
  }, [])

  return null
}
