import { NextResponse } from 'next/server'

// Unauthenticated liveness probe. Used by scripts/test-app-running.sh and
// playwright.config.ts webServer readiness — every page route 307-redirects
// through the auth flow, so readiness checks need a plain 200.
export async function GET() {
  return NextResponse.json({ status: 'ok' })
}
