import { NextResponse } from 'next/server'
import { getSession, getActiveRole } from '@/lib/auth'

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const role = await getActiveRole()
  return NextResponse.json({
    user: session.user,
    role: session.user,
    activeRole: role,
    mode: role,
    canSwitchRole: session.user === 'staff',
    canSwitchMode: session.user === 'staff',
  })
}
