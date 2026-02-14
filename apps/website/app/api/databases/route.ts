import { NextResponse } from 'next/server'
import comprehensiveDatabase from '@/lib/comprehensive-database.json'

export async function GET() {
  try {
    return NextResponse.json(comprehensiveDatabase)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load databases', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}
