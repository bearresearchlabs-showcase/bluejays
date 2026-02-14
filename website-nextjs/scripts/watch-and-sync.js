#!/usr/bin/env node
/**
 * Watch deliverable HTML files for changes and automatically sync content to Next.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const rootDir = path.join(__dirname, '../..');
const extractScript = path.join(__dirname, 'extract-deliverable-content.js');

function getAllDeliverableFiles() {
  const files = [];
  
  for (let dbNum = 6; dbNum <= 15; dbNum++) {
    const dbId = `db-${dbNum}`;
    const deliverableDir = path.join(rootDir, dbId, 'deliverable');
    
    if (fs.existsSync(deliverableDir)) {
      const dirFiles = fs.readdirSync(deliverableDir, { recursive: true });
      const docFiles = dirFiles.filter(f => 
        typeof f === 'string' && 
        f.includes('documentation.html') && 
        !f.includes('node_modules')
      );
      
      docFiles.forEach(file => {
        files.push(path.join(deliverableDir, file));
      });
    }
  }
  
  return files;
}

function syncContent() {
  console.log('\n🔄 Syncing content from deliverables...');
  try {
    execSync(`node "${extractScript}"`, { stdio: 'inherit' });
    console.log('✅ Content synced successfully\n');
  } catch (error) {
    console.error('❌ Error syncing content:', error.message);
  }
}

// Initial sync
console.log('👀 Watching deliverable files for changes...');
syncContent();

// Watch for file changes
const files = getAllDeliverableFiles();
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
