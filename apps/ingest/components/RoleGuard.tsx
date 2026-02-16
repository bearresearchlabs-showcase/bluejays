import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { getSession, getActiveRole } from '@/lib/auth'
import { loadPrivilegesConfig, getViewsForRole, isSystemOwner } from '@/lib/privileges'

/**
 * Enforces role-based access: annotator, customer, staff.
 * Redirects to first allowed view when current path is not allowed for the logged-in role.
 */
export async function RoleGuard({ children }: { children: React.ReactNode }) {
  const headersList = await headers()
  const pathname = headersList.get('x-pathname') || '/'

  if (pathname === '/login' || pathname === '/logout') {
    return <>{children}</>
  }

  const session = await getSession()
  if (!session) {
    redirect('/login')
  }

  const activeRole = await getActiveRole()
  const config = loadPrivilegesConfig()
  const allowedViews = getViewsForRole(session.user, activeRole, config)

  const base = pathname.split('?')[0].replace(/\/$/, '') || '/'
  const isAllowed =
    allowedViews.some((v) => v === base || base.startsWith(v + '/')) ||
    (base === '/admin/privileges' && session.user === 'staff' && isSystemOwner(activeRole))

  if (!isAllowed) {
    redirect(allowedViews[0] || '/')
  }

  return <>{children}</>
}
