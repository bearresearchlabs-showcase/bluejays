import { NextResponse } from 'next/server'
import { getSession, getViewMode } from '@/lib/auth'
import {
  loadPrivilegesConfig,
  savePrivilegesConfig,
  getViewsForRole,
  canExport,
  ALL_VIEWS,
  type PrivilegesConfig,
} from '@/lib/privileges'

export async function GET() {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const config = loadPrivilegesConfig()
  const mode = await getViewMode()
  const views = getViewsForRole(session.user, mode, config)
  const exportAllowed = canExport(session.user, mode, config)
  const canConfigure = session.user === 'staff' && mode === 'admin'
  return NextResponse.json({
    config,
    views,
    canExport: exportAllowed,
    canConfigure,
    allViews: ALL_VIEWS,
  })
}

export async function POST(request: Request) {
  const session = await getSession()
  if (!session || session.user !== 'staff') {
    return NextResponse.json({ error: 'Only staff can configure privileges' }, { status: 403 })
  }
  const mode = await getViewMode()
  if (mode !== 'admin') {
    return NextResponse.json({ error: 'Switch to Admin mode to configure privileges' }, {
      status: 403,
    })
  }
  let body: Partial<PrivilegesConfig>
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 })
  }
  const current = loadPrivilegesConfig()
  const config: PrivilegesConfig = {
    annotator: {
      views: Array.isArray(body.annotator?.views) ? body.annotator.views : current.annotator.views,
      canExport: typeof body.annotator?.canExport === 'boolean' ? body.annotator.canExport : current.annotator.canExport,
    },
    customer: {
      views: Array.isArray(body.customer?.views) ? body.customer.views : current.customer.views,
      canExport: typeof body.customer?.canExport === 'boolean' ? body.customer.canExport : current.customer.canExport,
    },
  }
  try {
    savePrivilegesConfig(config)
  } catch {
    return NextResponse.json(
      { error: 'Failed to save config (filesystem may be read-only in production)' },
      { status: 500 }
    )
  }
  return NextResponse.json({ ok: true, config })
}
