import { NextRequest, NextResponse } from 'next/server'
import { signToken, USER_CREDENTIALS } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const form = await request.formData()
    const user = (form.get('user') as string)?.trim()
    const password = form.get('password') as string
    const stay = form.get('stay') === '1'

    if (!user || !USER_CREDENTIALS[user] || USER_CREDENTIALS[user] !== password) {
      return NextResponse.redirect(
        new URL('/login?err=Invalid+username+or+password', request.url)
      )
    }

    const maxAge = stay ? 30 * 86400 : 86400
    const token = await signToken(user, maxAge / 86400)
    const res = NextResponse.redirect(
      new URL(user === 'customer' ? '/customer' : '/', request.url)
    )
    res.cookies.set('annotator_session', token, {
      path: '/',
      maxAge,
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
    })
    return res
  } catch {
    return NextResponse.redirect(new URL('/login?err=Invalid+request', request.url))
  }
}
