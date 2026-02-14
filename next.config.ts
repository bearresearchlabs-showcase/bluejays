import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname),
  outputFileTracingIncludes: {
    '/api/**': ['source/**', 'template/**', 'lib/**'],
    '/*': ['source/**', 'template/**', 'lib/**'],
  },
  outputFileTracingExcludes: {
    '/api/**': ['venv_selenium/**', '.venv/**', '**/venv/**'],
    '/*': ['venv_selenium/**', '.venv/**', '**/venv/**'],
  },
}

export default nextConfig
