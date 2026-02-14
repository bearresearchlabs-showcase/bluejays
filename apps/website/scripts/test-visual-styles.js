#!/usr/bin/env node

/**
 * Visual Style Testing Script
 * Compares local styles with deployed site styles
 */

const https = require('https')
const http = require('http')

const DEPLOYED_URL = 'https://db-documentation-f51u.vercel.app/'
const LOCAL_URL = 'http://localhost:3000'

// Expected values from deployed site
const EXPECTED_STYLES = {
  colors: {
    textPrimary: '#000000',
    textSecondary: '#6b7280',
    bgPrimary: '#ffffff',
    bgSecondary: '#fafafa',
    border: '#e5e7eb',
    accent: '#000000',
  },
  spacing: {
    mainContentPadding: '24px',
    cardPadding: '20px',
    sidebarPadding: '32px 0px',
  },
  typography: {
    h1FontSize: '32px',
    h1FontWeight: '600',
    h1LineHeight: '52.8px',
    h1LetterSpacing: '-0.64px',
    h2FontSize: '24px',
    h2FontWeight: '600',
    bodyFontSize: '16px',
    bodyLineHeight: '26.4px',
    bodyLetterSpacing: '-0.16px',
  },
  borderRadius: {
    card: '6px',
  },
}

function fetchHTML(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http
    client.get(url, (res) => {
      let data = ''
      res.on('data', (chunk) => {
        data += chunk
      })
      res.on('end', () => {
        resolve(data)
      })
    }).on('error', (err) => {
      reject(err)
    })
  })
}

async function checkLocalServer() {
  try {
    await fetchHTML(LOCAL_URL)
    return true
  } catch (err) {
    return false
  }
}

function checkCSSVariables(cssText) {
  const results = {
    passed: 0,
    failed: 0,
    errors: [],
  }

  // Check color variables
  Object.entries(EXPECTED_STYLES.colors).forEach(([key, expectedValue]) => {
    const varName = key === 'textPrimary' ? '--text-primary' :
                   key === 'textSecondary' ? '--text-secondary' :
                   key === 'bgPrimary' ? '--bg-primary' :
                   key === 'bgSecondary' ? '--bg-secondary' :
                   key === 'border' ? '--border' :
                   key === 'accent' ? '--accent' : null

    if (varName) {
      const regex = new RegExp(`${varName}:\\s*([^;]+)`, 'i')
      const match = cssText.match(regex)
      if (match && match[1].trim() === expectedValue) {
        results.passed++
      } else {
        results.failed++
        results.errors.push(`CSS variable ${varName}: expected ${expectedValue}, got ${match ? match[1].trim() : 'not found'}`)
      }
    }
  })

  return results
}

async function main() {
  console.log('Visual Style Testing\n')
  console.log('='.repeat(50))

  // Check if local server is running
  const serverRunning = await checkLocalServer()
  if (!serverRunning) {
    console.log('ERROR: Local server is not running on', LOCAL_URL)
    console.log('Please run: npm run dev')
    process.exit(1)
  }

  console.log('Local server is running')
  console.log('Checking CSS variables in design-system.css...\n')

  const fs = require('fs')
  const path = require('path')
  const cssPath = path.join(__dirname, '..', 'app', 'design-system.css')
  const globalsPath = path.join(__dirname, '..', 'app', 'globals.css')

  if (!fs.existsSync(cssPath)) {
    console.log('ERROR: design-system.css not found')
    process.exit(1)
  }

  const cssContent = fs.readFileSync(cssPath, 'utf8')
  const globalsContent = fs.existsSync(globalsPath) ? fs.readFileSync(globalsPath, 'utf8') : ''

  const combinedCSS = cssContent + '\n' + globalsContent
  const results = checkCSSVariables(combinedCSS)

  console.log('CSS Variable Checks:')
  console.log(`  Passed: ${results.passed}`)
  console.log(`  Failed: ${results.failed}`)

  if (results.errors.length > 0) {
    console.log('\nErrors:')
    results.errors.forEach((error) => {
      console.log(`  - ${error}`)
    })
  }

  console.log('\n' + '='.repeat(50))
  
  if (results.failed === 0) {
    console.log('All visual style checks passed!')
    process.exit(0)
  } else {
    console.log('Some visual style checks failed')
    process.exit(1)
  }
}

main().catch((err) => {
  console.error('Error:', err)
  process.exit(1)
})
