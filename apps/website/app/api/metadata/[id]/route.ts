import { NextResponse } from 'next/server'
import { head } from '@vercel/blob'
import { readFile, readdir } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

const BLOB_STORE_BASE = 'guides'

// Vercel Blob Storage configuration
// Token is read from BLOB_READ_WRITE_TOKEN environment variable
// Set in Vercel dashboard or .env.local file
const getBlobToken = () => {
  return process.env.BLOB_READ_WRITE_TOKEN || ''
}

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    // Convert db6 to db-6 format
    const dbNumber = id.replace('db', 'db-')
    
    // Construct blob pathname: guides/{db-number}_deliverable.json
    const blobPathname = `${BLOB_STORE_BASE}/${dbNumber}_deliverable.json`
    
    // Try Vercel Blob Storage first
    try {
      const token = getBlobToken()
      if (!token) {
        console.warn('BLOB_READ_WRITE_TOKEN not set - blob storage will not work')
        throw new Error('BLOB_READ_WRITE_TOKEN not configured')
      }
      
      // Get blob metadata (includes downloadUrl)
      // @vercel/blob automatically reads BLOB_READ_WRITE_TOKEN from env
      // Passing token explicitly ensures it's available
      const blobInfo = await head(blobPathname, {
        token: token,
      })
      
      // Fetch the actual file content using downloadUrl
      const response = await fetch(blobInfo.downloadUrl)
      if (!response.ok) {
        throw new Error(`Failed to fetch blob: ${response.status} ${response.statusText}`)
      }
      
      const fileContent = await response.text()
      const metadata = JSON.parse(fileContent)
      return NextResponse.json(metadata)
    } catch (blobError) {
      console.log('Blob not found in Vercel Blob Storage, trying local filesystem...')
      
      // Fallback to local filesystem (client/db only)
      const dbBasePath = join(process.cwd(), '..', 'client', 'db', dbNumber)
      let fileContent: string | null = null
      
      try {
        if (existsSync(dbBasePath)) {
          const entries = await readdir(dbBasePath, { withFileTypes: true })
          
          // Try multiple filename patterns
          const filenamePatterns = [
            `${dbNumber}_deliverable.json`,
            `database_deliverable.json`
          ]
          
          // Look for the file directly in deliverable folder
          for (const filename of filenamePatterns) {
            const directPath = join(dbBasePath, filename)
            if (existsSync(directPath)) {
              fileContent = await readFile(directPath, 'utf-8')
              break
            }
          }
          
          // If not found, look in subdirectories
          if (!fileContent) {
            for (const entry of entries) {
              if (entry.isDirectory()) {
                for (const filename of filenamePatterns) {
                  const subPath = join(dbBasePath, entry.name, filename)
                  if (existsSync(subPath)) {
                    fileContent = await readFile(subPath, 'utf-8')
                    break
                  }
                }
                if (fileContent) break
              }
            }
          }
        }
      } catch (fsError) {
        console.error('Error reading from local filesystem:', fsError)
      }
      
      if (fileContent) {
        const metadata = JSON.parse(fileContent)
        return NextResponse.json(metadata)
      }
      
      // If neither blob nor local file found, return error
      return NextResponse.json(
        { error: `Deliverable file not found for ${id}`, details: blobError instanceof Error ? blobError.message : String(blobError) },
        { status: 404 }
      )
    }
  } catch (error) {
    console.error('Error loading metadata:', error)
    return NextResponse.json(
      { error: 'Failed to load metadata', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
