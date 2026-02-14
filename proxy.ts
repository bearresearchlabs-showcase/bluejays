import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Proxy (Next.js 16): enforce auth for all routes except /login, /logout, and API.
 * Sets x-pathname for RoleGuard. SSO-style privilege boundary.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-pathname', pathname)

  if (pathname === '/login' || pathname === '/logout') {
    return NextResponse.next({ request: { headers: requestHeaders } })
  }
  if (pathname.startsWith('/api/')) return NextResponse.next()

  const token = request.cookies.get('annotator_session')?.value
  if (!token) {
    const url = new URL('/login', request.url)
    if (pathname !== '/') url.searchParams.set('from', pathname)
    return NextResponse.redirect(url)
  }

  return NextResponse.next({ request: { headers: requestHeaders } })
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
