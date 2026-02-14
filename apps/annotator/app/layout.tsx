import type { Metadata } from 'next'
import { Analytics } from '@vercel/analytics/react'
import { DebugPing } from '@/components/DebugPing'
import './globals.css'

export const metadata: Metadata = {
  title: 'SQL Annotator — Workbench',
  description: 'Text-to-SQL annotation workbench with task board and customer portal',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <DebugPing />
        {children}
      </body>
      <Analytics />
    </html>
  )
}
