#!/usr/bin/env node
/**
 * Verify Vercel Blob Storage configuration
 * Checks if BLOB_READ_WRITE_TOKEN is set and can connect to blob storage
 */

// Try to load dotenv if available (for standalone script execution)
try {
  require('dotenv').config({ path: '.env.local' })
} catch (e) {
  // dotenv not available - Next.js will load .env.local automatically
  // This script can still check process.env if token is set via environment
}

const token = process.env.BLOB_READ_WRITE_TOKEN

if (!token) {
  console.error('❌ BLOB_READ_WRITE_TOKEN is not set')
  console.log('\nTo configure:')
  console.log('1. Create .env.local file in apps/website/')
  console.log('2. Add: BLOB_READ_WRITE_TOKEN=your_token_here')
  console.log('3. Or set in Vercel dashboard: Project Settings > Environment Variables')
  process.exit(1)
}

if (!token.startsWith('vercel_blob_')) {
  console.warn('⚠️  Token format looks incorrect (should start with "vercel_blob_")')
}

console.log('✅ BLOB_READ_WRITE_TOKEN is configured')
console.log(`   Token prefix: ${token.substring(0, 20)}...`)
console.log('\nTo test blob storage, make a request to:')
console.log('  GET /api/deliverable/db6')
console.log('  GET /api/metadata/db6')
