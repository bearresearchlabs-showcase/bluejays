import { NextRequest, NextResponse } from 'next/server'
import { getSession, setViewModeCookie } from '@/lib/auth'

export async function POST(request: NextRequest) {
  const session = await getSession()
  if (!session || session.user !== 'staff') {
    return NextResponse.json({ error: 'Only staff can set mode' }, { status: 403 })
  }
  const body = await request.json()
  const mode = (body.mode || 'annotator').toLowerCase()
  const valid = mode === 'annotator' || mode === 'admin'
  const m = valid ? mode : 'annotator'

  const res = NextResponse.json({ ok: true, mode: m })
  res.cookies.set('view_mode', m, {
    path: '/',
    maxAge: 30 * 86400,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  })
  return res
}
