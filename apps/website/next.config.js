const path = require('path')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  // Enable static export if needed
  // output: 'export',
  // Fix turbopack root warning by explicitly setting root directory
  // This prevents Next.js from inferring the wrong workspace root when multiple lockfiles exist
  turbopack: {
    root: __dirname,
  },
  // Explicitly set the project root for webpack
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
    }
    return config
  },
}

module.exports = nextConfig
