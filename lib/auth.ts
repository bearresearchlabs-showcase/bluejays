import { SignJWT, jwtVerify } from 'jose'
import { cookies } from 'next/headers'
import { loadPrivilegesConfig, isPathAllowedForRole } from '@/lib/privileges'

const SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'annotator-dev-secret-change-in-production'
)
const COOKIE = 'annotator_session'
const VIEW_MODE_COOKIE = 'view_mode'

export const USER_CREDENTIALS: Record<string, string> = {
  staff: '123123',
  annotator: '123123',
  customer: '123123',
}

export type UserRole = 'staff' | 'annotator' | 'customer'

export async function signToken(user: string, expiresInDays = 30): Promise<string> {
  const exp = Math.floor(Date.now() / 1000) + expiresInDays * 86400
  return new SignJWT({ user })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime(exp)
    .sign(SECRET)
}

export async function verifyToken(token: string): Promise<{ user: string } | null> {
  try {
    const { payload } = await jwtVerify(token, SECRET)
    return { user: payload.user as string }
  } catch {
    return null
  }
}

export async function getSession(): Promise<{ user: string } | null> {
  const cookieStore = await cookies()
  const token = cookieStore.get(COOKIE)?.value
  if (!token) return null
  return verifyToken(token)
}

export async function setSessionCookie(token: string, maxAge: number) {
  const cookieStore = await cookies()
  cookieStore.set(COOKIE, token, {
    path: '/',
    maxAge,
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  })
}

export async function clearSession() {
  const cookieStore = await cookies()
  cookieStore.delete(COOKIE)
  cookieStore.delete(VIEW_MODE_COOKIE)
}

export async function getViewMode(): Promise<string> {
  const cookieStore = await cookies()
  return cookieStore.get(VIEW_MODE_COOKIE)?.value || 'annotator'
}

export async function setViewModeCookie(mode: string) {
  const cookieStore = await cookies()
  cookieStore.set(VIEW_MODE_COOKIE, mode, {
    path: '/',
    maxAge: 30 * 86400,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  })
}

export function isPathAllowed(path: string, user: string, viewMode: string): boolean {
  const config = loadPrivilegesConfig()
  return isPathAllowedForRole(path, user, viewMode, config)
}
