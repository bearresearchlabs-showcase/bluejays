import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { searchTasks } from '@/lib/scale-data'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const dataset = request.nextUrl.searchParams.get('dataset') ?? undefined
  const delivery = request.nextUrl.searchParams.get('delivery') ?? undefined
  const nextToken = request.nextUrl.searchParams.get('next_token') ?? undefined
  const { tasks, next_token } = searchTasks(dataset, delivery, nextToken)
  return NextResponse.json({ tasks, next_token })
}
