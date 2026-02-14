import { NextResponse } from 'next/server'
import comprehensiveDatabase from '@/lib/comprehensive-database.json'
import { readFile } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const db = (comprehensiveDatabase as any).databases.find((d: any) => d.id === id)
    
    if (!db) {
      return NextResponse.json(
        { error: `Database ${id} not found` },
        { status: 404 }
      )
    }

    // Try to load full schema from deliverable JSON
    const rootDir = join(process.cwd(), '..')
    const deliverablePath = join(rootDir, db.paths.deliverable_json)
    
    if (existsSync(deliverablePath)) {
      try {
        const deliverableData = JSON.parse(await readFile(deliverablePath, 'utf-8'))
        return NextResponse.json({
          database_id: id,
          schema: deliverableData.schema || db.schema
        })
      } catch (e) {
        console.warn(`Failed to load full schema for ${id}:`, e)
      }
    }

    return NextResponse.json({
      database_id: id,
      schema: db.schema
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load schema', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
