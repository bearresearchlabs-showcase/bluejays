#!/usr/bin/env node
/**
 * Wrapper to start Next.js dev server with explicit args.
 * Prevents stray shell arguments (e.g. pasted comments) from reaching Next.js.
 */
const path = require('path');
const { spawn } = require('child_process');
const proc = spawn('npx', ['next', 'dev', '-p', '3007'], {
  stdio: 'inherit',
  cwd: path.resolve(__dirname, '..'),
  shell: false,
});
proc.on('exit', (code) => process.exit(code ?? 0));
