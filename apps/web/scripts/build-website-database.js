#!/usr/bin/env node
/**
 * Build the website database index from client/db deliverable JSON files.
 * Single source of truth for catalog and sidebar: id, name, shortDescription, tableCount, queryCount.
 * Reduces redundancy by deriving all list/catalog data from client deliverables.
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '../../..');
const clientDbRoot = path.join(rootDir, 'client', 'db');
const outputFile = path.join(__dirname, '../lib/database-index.json');

const MAX_SHORT_DESCRIPTION = 200;

function firstSentenceOrTruncate(text, maxLen = MAX_SHORT_DESCRIPTION) {
  if (!text || typeof text !== 'string') return '';
  const trimmed = text.replace(/\s+/g, ' ').trim();
  const firstSentence = trimmed.split(/[.!?]\s+/)[0];
  if (firstSentence.length <= maxLen) return firstSentence + (trimmed.length > firstSentence.length ? '.' : '');
  return trimmed.slice(0, maxLen).replace(/\s+\S*$/, '') + '…';
}

function findDeliverableJson(dbDirName) {
  const dbDir = path.join(clientDbRoot, dbDirName);
  if (!fs.existsSync(dbDir)) return null;
  const entries = fs.readdirSync(dbDir, { withFileTypes: true });
  for (const e of entries) {
    if (e.isDirectory() && !e.name.startsWith('.')) {
      const candidate = path.join(dbDir, e.name, `${dbDirName}_deliverable.json`);
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  return null;
}

function buildIndex() {
  const databases = [];
  for (let n = 6; n <= 15; n++) {
    const dbDirName = `db-${n}`;
    const id = `db${n}`;
    const jsonPath = findDeliverableJson(dbDirName);
    if (!jsonPath) {
      console.warn(`⚠️  No deliverable JSON for ${dbDirName}`);
      databases.push({
        id,
        name: `${dbDirName.toUpperCase()} Database`,
        shortDescription: '',
        tableCount: 0,
        queryCount: 0,
        created_date: null,
        version: null,
      });
      continue;
    }
    let data;
    try {
      data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    } catch (err) {
      console.warn(`⚠️  Failed to read ${jsonPath}:`, err.message);
      databases.push({
        id,
        name: `${dbDirName.toUpperCase()} Database`,
        shortDescription: '',
        tableCount: 0,
        queryCount: 0,
        created_date: null,
        version: null,
      });
      continue;
    }
    const db = data.database || {};
    const schema = data.schema || {};
    const queries = data.queries || [];
    const description = db.description || '';
    databases.push({
      id,
      name: db.name || `${dbDirName.toUpperCase()} Database`,
      shortDescription: firstSentenceOrTruncate(description),
      tableCount: schema.total_tables != null ? schema.total_tables : 0,
      queryCount: queries.length,
      created_date: db.created_date || null,
      version: db.version || null,
    });
  }
  const index = {
    generated_at: new Date().toISOString(),
    totalDatabases: databases.length,
    databases,
  };
  const outDir = path.dirname(outputFile);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(outputFile, JSON.stringify(index, null, 2), 'utf-8');
  console.log(`✅ Website database index: ${outputFile} (${databases.length} databases)`);
  return index;
}

buildIndex();
