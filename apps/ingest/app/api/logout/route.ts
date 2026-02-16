import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const res = NextResponse.redirect(new URL('/login', request.url))
  res.cookies.set('annotator_session', '', { path: '/', maxAge: 0 })
  res.cookies.set('active_role', '', { path: '/', maxAge: 0 })
  return res
}

export async function POST(request: NextRequest) {
  const res = NextResponse.redirect(new URL('/login', request.url))
  res.cookies.set('annotator_session', '', { path: '/', maxAge: 0 })
  res.cookies.set('active_role', '', { path: '/', maxAge: 0 })
  return res
}
