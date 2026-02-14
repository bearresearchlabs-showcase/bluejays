import { NextRequest, NextResponse } from 'next/server'

const base = () => process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3001'

export async function GET(request: NextRequest) {
  const res = NextResponse.redirect(new URL('/login', request.url))
  res.cookies.set('annotator_session', '', { path: '/', maxAge: 0 })
  res.cookies.set('view_mode', '', { path: '/', maxAge: 0 })
  return res
}

export async function POST() {
  const res = NextResponse.redirect(new URL('/login', base()))
  res.cookies.set('annotator_session', '', { path: '/', maxAge: 0 })
  res.cookies.set('view_mode', '', { path: '/', maxAge: 0 })
  return res
}
