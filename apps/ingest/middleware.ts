import { NextRequest, NextResponse } from 'next/server'

// RoleGuard (rendered from the root layout) reads x-pathname to know which
// route it is guarding — most importantly to exempt /login and /logout.
// Without this header every render defaults to '/', so an unauthenticated
// visit to /login redirects to /login in an infinite 307 loop.
export function middleware(request: NextRequest) {
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-pathname', request.nextUrl.pathname)
  return NextResponse.next({ request: { headers: requestHeaders } })
}
