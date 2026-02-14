import type { Metadata } from 'next'
import { Analytics } from '@vercel/analytics/react'
import Script from 'next/script'
import { ThemeProvider } from '@/components/design-system'
import './globals.css'
import './design-system.css'
import './design-system-utilities.css'

export const metadata: Metadata = {
  title: 'Database Documentation - Production SQL Databases',
  description: 'Comprehensive documentation for production databases db-6 through db-15. All databases and queries are sourced from production systems used by businesses with $1M+ ARR.',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Prism.js Syntax Highlighting - Match db-6_documentation.html */}
        <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css" rel="stylesheet" />
        {/* Custom Prism.js Token Colors - Must load after Prism.js theme */}
        <style dangerouslySetInnerHTML={{ __html: `
          /* SQL Token Colors - Override Prism.js Okaidia theme - Maximum Specificity */
          pre[class*="language-sql"] .token.keyword,
          pre[class*="language-sql"] code .token.keyword,
          code[class*="language-sql"] .token.keyword,
          pre code[class*="language-sql"] .token.keyword { color: #569cd6 !important; }
          pre[class*="language-sql"] .token.function,
          pre[class*="language-sql"] code .token.function,
          code[class*="language-sql"] .token.function,
          pre code[class*="language-sql"] .token.function { color: #dcdcaa !important; }
          pre[class*="language-sql"] .token.string,
          pre[class*="language-sql"] code .token.string,
          code[class*="language-sql"] .token.string,
          pre code[class*="language-sql"] .token.string { color: #ce9178 !important; }
          pre[class*="language-sql"] .token.number,
          pre[class*="language-sql"] code .token.number,
          code[class*="language-sql"] .token.number,
          pre code[class*="language-sql"] .token.number { color: #b5cea8 !important; }
          pre[class*="language-sql"] .token.comment,
          pre[class*="language-sql"] code .token.comment,
          code[class*="language-sql"] .token.comment,
          pre code[class*="language-sql"] .token.comment { color: #6a9955 !important; font-style: italic !important; }
          pre[class*="language-sql"] .token.operator,
          pre[class*="language-sql"] code .token.operator,
          code[class*="language-sql"] .token.operator,
          pre code[class*="language-sql"] .token.operator { color: #d4d4d4 !important; }
          pre[class*="language-sql"] .token.punctuation,
          pre[class*="language-sql"] code .token.punctuation,
          code[class*="language-sql"] .token.punctuation,
          pre code[class*="language-sql"] .token.punctuation { color: #d4d4d4 !important; }
          pre[class*="language-sql"] .token.builtin,
          pre[class*="language-sql"] code .token.builtin,
          code[class*="language-sql"] .token.builtin,
          pre code[class*="language-sql"] .token.builtin { color: #4ec9b0 !important; }
          
          /* JSON Token Colors - Override Prism.js Okaidia theme - Maximum Specificity */
          pre[class*="language-json"] .token.property,
          pre[class*="language-json"] code .token.property,
          code[class*="language-json"] .token.property,
          pre code[class*="language-json"] .token.property { color: #79b8ff !important; }
          pre[class*="language-json"] .token.string,
          pre[class*="language-json"] code .token.string,
          code[class*="language-json"] .token.string,
          pre code[class*="language-json"] .token.string { color: #9ecbff !important; }
          pre[class*="language-json"] .token.number,
          pre[class*="language-json"] code .token.number,
          code[class*="language-json"] .token.number,
          pre code[class*="language-json"] .token.number { color: #79b8ff !important; }
          pre[class*="language-json"] .token.boolean,
          pre[class*="language-json"] code .token.boolean,
          code[class*="language-json"] .token.boolean,
          pre code[class*="language-json"] .token.boolean { color: #ffab70 !important; }
          pre[class*="language-json"] .token.null,
          pre[class*="language-json"] code .token.null,
          code[class*="language-json"] .token.null,
          pre code[class*="language-json"] .token.null { color: #f97583 !important; }
          pre[class*="language-json"] .token.punctuation,
          pre[class*="language-json"] code .token.punctuation,
          code[class*="language-json"] .token.punctuation,
          pre code[class*="language-json"] .token.punctuation { color: #c9d1d9 !important; }
          pre[class*="language-json"] .token.operator,
          pre[class*="language-json"] code .token.operator,
          code[class*="language-json"] .token.operator,
          pre code[class*="language-json"] .token.operator { color: #c9d1d9 !important; }
          pre[class*="language-json"] .token.keyword,
          pre[class*="language-json"] code .token.keyword,
          code[class*="language-json"] .token.keyword,
          pre code[class*="language-json"] .token.keyword { color: #79b8ff !important; }
        ` }} />
      </head>
      <body>
        <ThemeProvider>
          {children}
        </ThemeProvider>
        <Script
          src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"
          strategy="afterInteractive"
        />
        <Script
          src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"
          strategy="afterInteractive"
        />
        <Script
          src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"
          strategy="afterInteractive"
        />
        {/* Mermaid.js for ER diagrams and visualizations */}
        <Script
          src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"
          strategy="afterInteractive"
        />
        <Analytics />
      </body>
    </html>
  )
}
