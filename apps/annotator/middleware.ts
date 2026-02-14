import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'


export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  if (pathname === '/login') return NextResponse.next()
  if (pathname.startsWith('/api/')) return NextResponse.next() // API routes handle auth
  const token = request.cookies.get('annotator_session')?.value
  if (!token) {
    const url = new URL('/login', request.url)
    if (pathname !== '/') url.searchParams.set('from', pathname)
    return NextResponse.redirect(url)
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
