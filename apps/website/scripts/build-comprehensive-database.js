#!/usr/bin/env node
/**
 * Build comprehensive database structure from all client/db/ folders
 * Extracts: databases, schemas, queries, files, metadata, and relationships
 * Creates a single structured JSON file for the website
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '../..');
const clientDbRoot = path.join(rootDir, 'client', 'db');
const outputFile = path.join(__dirname, '../lib/comprehensive-database.json');

function findDeliverableFolder(dbDirName) {
  const dbDir = path.join(clientDbRoot, dbDirName);
  if (!fs.existsSync(dbDir)) return null;
  const entries = fs.readdirSync(dbDir, { withFileTypes: true });
  for (const e of entries) {
    if (e.isDirectory() && !e.name.startsWith('.') && !e.name.includes('deliverable')) {
      const candidate = path.join(dbDir, e.name);
      if (fs.existsSync(path.join(candidate, `${dbDirName}_deliverable.json`)) ||
          fs.existsSync(path.join(candidate, `${dbDirName}.md`))) {
        return candidate;
      }
    }
  }
  return null;
}

function extractSchemaInfo(schema) {
  if (!schema || !schema.tables) return { total_tables: 0, tables: [] };
  
  return {
    total_tables: schema.total_tables || schema.tables.length,
    tables: schema.tables.map(table => ({
      name: table.name,
      description: table.description || '',
      column_count: table.columns ? table.columns.length : 0,
      columns: table.columns ? table.columns.map(col => ({
        name: col.name,
        data_type: col.data_type,
        constraints: col.constraints,
        description: col.description || ''
      })) : []
    }))
  };
}

function extractQueryInfo(queries) {
  if (!queries || !Array.isArray(queries)) return { total_queries: 0, queries: [] };
  
  return {
    total_queries: queries.length,
    queries: queries.map(q => ({
      number: q.number,
      title: q.title,
      description: q.description || '',
      use_case: q.use_case || '',
      business_value: q.business_value || '',
      complexity: q.complexity || '',
      sql_preview: q.sql ? q.sql.substring(0, 200) + '...' : ''
    }))
  };
}

function listDataFiles(folderPath) {
  const dataDir = path.join(folderPath, 'data');
  if (!fs.existsSync(dataDir)) return [];
  
  const files = fs.readdirSync(dataDir, { recursive: false });
  return files
    .filter(f => f.endsWith('.sql'))
    .map(f => {
      const filePath = path.join(dataDir, f);
      const stats = fs.statSync(filePath);
      return {
        name: f,
        size_bytes: stats.size,
        size_mb: (stats.size / (1024 * 1024)).toFixed(2),
        path: `data/${f}`
      };
    })
    .sort((a, b) => b.size_bytes - a.size_bytes);
}

function extractDatabase(dbNum) {
  const dbDirName = `db-${dbNum}`;
  const id = `db${dbNum}`;
  const folder = findDeliverableFolder(dbDirName);
  
  if (!folder) {
    console.warn(`⚠️  No deliverable folder found for ${dbDirName}`);
    return null;
  }

  const deliverableJsonPath = path.join(folder, `${dbDirName}_deliverable.json`);
  const mdPath = path.join(folder, `${dbDirName}.md`);
  const vercelJsonPath = path.join(folder, 'vercel.json');
  
  let deliverableData = null;
  if (fs.existsSync(deliverableJsonPath)) {
    try {
      deliverableData = JSON.parse(fs.readFileSync(deliverableJsonPath, 'utf-8'));
    } catch (e) {
      console.warn(`⚠️  Failed to parse ${deliverableJsonPath}:`, e.message);
    }
  }

  const database = deliverableData?.database || {};
  const schema = extractSchemaInfo(deliverableData?.schema);
  const queries = extractQueryInfo(deliverableData?.queries);
  const dataFiles = listDataFiles(folder);

  // Extract first paragraph for short description
  const fullDescription = database.description || '';
  const shortDescription = fullDescription.split('\n\n')[0].substring(0, 300);

  return {
    id,
    db_number: dbNum,
    name: database.name || `${dbDirName.toUpperCase()} Database`,
    short_description: shortDescription,
    full_description: fullDescription,
    created_date: database.created_date || null,
    version: database.version || null,
    folder_name: path.basename(folder),
    schema: {
      total_tables: schema.total_tables,
      tables: schema.tables.map(t => ({
        name: t.name,
        description: t.description,
        column_count: t.column_count
      }))
    },
    queries: {
      total_queries: queries.total_queries,
      preview: queries.queries.slice(0, 5) // First 5 queries as preview
    },
    files: {
      deliverable_json: fs.existsSync(deliverableJsonPath),
      markdown: fs.existsSync(mdPath),
      vercel_config: fs.existsSync(vercelJsonPath),
      data_files: dataFiles,
      total_data_size_mb: dataFiles.reduce((sum, f) => sum + parseFloat(f.size_mb), 0).toFixed(2)
    },
    paths: {
      deliverable_json: deliverableJsonPath.replace(rootDir + '/', ''),
      markdown: mdPath.replace(rootDir + '/', ''),
      folder: folder.replace(rootDir + '/', '')
    }
  };
}

function buildComprehensiveDatabase() {
  console.log('📊 Building comprehensive database structure...\n');
  
  const databases = [];
  const stats = {
    total_databases: 0,
    total_tables: 0,
    total_queries: 0,
    total_data_size_mb: 0
  };

  for (let n = 6; n <= 15; n++) {
    const db = extractDatabase(n);
    if (db) {
      databases.push(db);
      stats.total_databases++;
      stats.total_tables += db.schema.total_tables;
      stats.total_queries += db.queries.total_queries;
      stats.total_data_size_mb += parseFloat(db.files.total_data_size_mb);
    }
  }

  const comprehensive = {
    generated_at: new Date().toISOString(),
    source: 'client/db/',
    statistics: {
      ...stats,
      total_data_size_mb: stats.total_data_size_mb.toFixed(2),
      average_tables_per_db: (stats.total_tables / stats.total_databases).toFixed(1),
      average_queries_per_db: (stats.total_queries / stats.total_databases).toFixed(1)
    },
    databases: databases.sort((a, b) => a.db_number - b.db_number),
    categories: {
      by_table_count: {
        small: databases.filter(d => d.schema.total_tables < 12).length,
        medium: databases.filter(d => d.schema.total_tables >= 12 && d.schema.total_tables < 15).length,
        large: databases.filter(d => d.schema.total_tables >= 15).length
      },
      by_query_count: {
        standard: databases.filter(d => d.queries.total_queries === 30).length,
        other: databases.filter(d => d.queries.total_queries !== 30).length
      }
    }
  };

  const outDir = path.dirname(outputFile);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  
  fs.writeFileSync(outputFile, JSON.stringify(comprehensive, null, 2), 'utf-8');
  
  console.log(`✅ Comprehensive database structure built:`);
  console.log(`   📄 Output: ${outputFile}`);
  console.log(`   📊 Databases: ${stats.total_databases}`);
  console.log(`   🗂️  Total Tables: ${stats.total_tables}`);
  console.log(`   📝 Total Queries: ${stats.total_queries}`);
  console.log(`   💾 Total Data Size: ${stats.total_data_size_mb.toFixed(2)} MB`);
  
  return comprehensive;
}

buildComprehensiveDatabase();
