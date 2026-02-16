import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { getTask } from '@/lib/scale-data'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const taskId = request.nextUrl.searchParams.get('task_id')
  const dataset = request.nextUrl.searchParams.get('dataset')
  if (!taskId || !dataset) {
    return NextResponse.json({ error: 'task_id and dataset required' }, { status: 400 })
  }
  const numericId = taskId.includes('-') ? taskId.split('-').pop() : taskId
  const task = getTask(dataset, numericId || taskId)
  if (!task) {
    return NextResponse.json({ error: 'Task not found' }, { status: 404 })
  }
  return NextResponse.json(task)
}
