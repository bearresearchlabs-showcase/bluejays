import { NextResponse } from 'next/server'
import comprehensiveDatabase from '@/lib/comprehensive-database.json'

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
    
    return NextResponse.json(db)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load database', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
