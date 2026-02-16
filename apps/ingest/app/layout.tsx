import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Analytics } from '@vercel/analytics/react'
import { DebugPing } from '@/components/DebugPing'
import { RoleGuard } from '@/components/RoleGuard'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

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
    <html lang="en" className={inter.variable}>
      <head>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
      </head>
      <body className={`${inter.className} bg-[#0f1419] text-[#e6edf3]`}>
        <DebugPing />
        <RoleGuard>
          {children}
        </RoleGuard>
        <Analytics />
      </body>
    </html>
  )
}
