import { NextResponse } from 'next/server'
import { getSession, getViewMode } from '@/lib/auth'

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const mode = await getViewMode()
  return NextResponse.json({
    user: session.user,
    role: session.user,
    mode,
    canSwitchMode: session.user === 'staff',
  })
}
