#!/usr/bin/env node
/**
 * Watch deliverable HTML files for changes and automatically sync content to Next.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const rootDir = path.join(__dirname, '../../..'); // repo root
const clientDbRoot = path.join(rootDir, 'client', 'db');

function getAllDeliverableFiles() {
  const files = [];
  if (!require('fs').existsSync(clientDbRoot)) return files;
  const dirs = require('fs').readdirSync(clientDbRoot, { withFileTypes: true });
  for (const d of dirs) {
    if (!d.isDirectory() || !d.name.startsWith('db-')) continue;
    const dbDir = path.join(clientDbRoot, d.name);
    const subdirs = require('fs').readdirSync(dbDir, { withFileTypes: true });
    for (const sd of subdirs) {
      if (!sd.isDirectory() || sd.name.startsWith('.')) continue;
      const candidate = path.join(dbDir, sd.name);
      const deliverableJson = path.join(candidate, `${d.name}_deliverable.json`);
      const docHtml = path.join(candidate, `${d.name}_documentation.html`);
      const docMd = path.join(candidate, `${d.name}.md`);
      if (require('fs').existsSync(docHtml)) files.push(docHtml);
      if (require('fs').existsSync(docMd)) files.push(docMd);
      if (require('fs').existsSync(deliverableJson)) files.push(deliverableJson);
    }
  }
  return [...new Set(files)];
}

function getAllDeliverableFilesLegacy() {
  const files = [];
  for (let dbNum = 6; dbNum <= 15; dbNum++) {
    const dbId = `db-${dbNum}`;
    const deliverableDir = path.join(rootDir, 'client', 'db', dbId);
    if (fs.existsSync(deliverableDir)) {
      const subdirs = fs.readdirSync(deliverableDir, { withFileTypes: true });
      for (const sd of subdirs) {
        if (sd.isDirectory()) {
          const docHtml = path.join(deliverableDir, sd.name, `${dbId}_documentation.html`);
          if (fs.existsSync(docHtml)) files.push(docHtml);
        }
      }
    }
  }
  return files;
}

function syncContent() {
  console.log('\n🔄 Syncing content (extract + build-website-db + build-comprehensive-db)...');
  try {
    execSync('npm run sync-content', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
    console.log('✅ Content synced');
    const workApi = process.env.WORK_API_URL || 'http://localhost:8010';
    execSync('npm run sync-to-qdrant', { stdio: 'inherit', cwd: path.join(__dirname, '..'), env: { ...process.env, WORK_API_URL: workApi } });
    console.log('✅ Qdrant sync done\n');
  } catch (error) {
    console.error('❌ Error syncing:', error.message);
  }
}

// Initial sync
console.log('👀 Watching deliverable files for changes...');
syncContent();

// Watch for file changes (client/db structure)
let files = getAllDeliverableFiles();
if (files.length === 0) files = getAllDeliverableFilesLegacy();
const watchers = new Map();

files.forEach(file => {
  if (fs.existsSync(file)) {
    try {
      const watcher = fs.watchFile(file, { interval: 1000 }, (curr, prev) => {
        if (curr.mtime !== prev.mtime) {
          console.log(`\n📝 Detected change in: ${path.relative(rootDir, file)}`);
          syncContent();
        }
      });
      watchers.set(file, watcher);
      console.log(`👁️  Watching: ${path.relative(rootDir, file)}`);
    } catch (error) {
      console.error(`⚠️  Could not watch ${file}:`, error.message);
    }
  }
});

console.log(`\n✅ Watching ${watchers.size} files. Press Ctrl+C to stop.\n`);

// Cleanup on exit
process.on('SIGINT', () => {
  console.log('\n\n🛑 Stopping watcher...');
  watchers.forEach(watcher => fs.unwatchFile(watcher));
  process.exit(0);
});
