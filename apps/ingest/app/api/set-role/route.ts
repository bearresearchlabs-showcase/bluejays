import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'

export async function POST(request: NextRequest) {
  const session = await getSession()
  if (!session || session.user !== 'staff') {
    return NextResponse.json({ error: 'Only staff can set role' }, { status: 403 })
  }
  const body = await request.json()
  const role = (body.role ?? body.mode ?? 'annotator').toLowerCase()
  const valid =
    role === 'annotator' ||
    role === 'staff' ||
    role === 'customer' ||
    role === 'system_owner' ||
    role === 'admin'
  const r = valid ? (role === 'admin' ? 'system_owner' : role) : 'annotator'

  const res = NextResponse.json({ ok: true, role: r })
  res.cookies.set('active_role', r, {
    path: '/',
    maxAge: 30 * 86400,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  })
  return res
}
