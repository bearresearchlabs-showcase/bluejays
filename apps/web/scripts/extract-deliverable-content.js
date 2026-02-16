#!/usr/bin/env node
/**
 * Extract content from client deliverable folders (client/db/db-6 ... db-15)
 * and update the Next.js database-content.json file.
 * Uses only client/db as the source of truth.
 */

const fs = require('fs');
const path = require('path');

// Try to load marked for markdown conversion
let marked = null;
try {
  marked = require('marked');
} catch (e) {
  // marked not available, will use simple converter
}

const rootDir = path.join(__dirname, '../../..');
const clientDbRoot = path.join(rootDir, 'client', 'db');
const outputFile = path.join(__dirname, '../lib/database-content.json');

function normalizeIds(content, dbPrefix) {
  // Normalize IDs to match expected structure (overview, schema, queries, query-1, etc.)
  // This handles different ID patterns across databases
  
  // Normalize overview IDs (database-overview, database-overview-section, etc. -> overview)
  content = content.replace(/id=["']([^"']*database[^"']*overview[^"']*)["']/gi, `id="${dbPrefix}-overview"`);
  content = content.replace(/id=["']([^"']*overview[^"']*database[^"']*)["']/gi, `id="${dbPrefix}-overview"`);
  
  // Normalize schema IDs (database-schema, schema-section, database-schema-documentation, data-dictionary, etc. -> schema)
  content = content.replace(/id=["']([^"']*database[^"']*schema[^"']*)["']/gi, `id="${dbPrefix}-schema"`);
  content = content.replace(/id=["']([^"']*schema[^"']*section[^"']*)["']/gi, `id="${dbPrefix}-schema"`);
  content = content.replace(/id=["']([^"']*schema[^"']*documentation[^"']*)["']/gi, `id="${dbPrefix}-schema"`);
  // Normalize data-dictionary to schema (it's part of schema documentation)
  content = content.replace(/id=["']([^"']*data[^"']*dictionary[^"']*)["']/gi, `id="${dbPrefix}-schema"`);
  // If there's a h2/h3 with "Database Schema" or "Schema" but no ID, add one
  content = content.replace(/<h([23])[^>]*>([^<]*Database[^<]*Schema[^<]*|Schema[^<]*)<\/h\1>/gi, (match, level, text) => {
    // Only add ID if it doesn't already have one
    if (!match.includes('id=')) {
      return `<h${level} id="${dbPrefix}-schema">${text}</h${level}>`;
    }
    return match;
  });
  
  // Normalize queries section IDs (sql-queries, queries-section, etc. -> queries)
  // Match sql-queries patterns that are NOT individual queries (query-1, query-2, etc.)
  content = content.replace(/id=["']([^"']*sql[^"']*quer[^"']*)["']/gi, (match, idValue) => {
    // Check if this is a queries section (not an individual query)
    // Individual queries have pattern like "query-1" or "query-2"
    if (!idValue.match(/query-\d+/)) {
      return `id="${dbPrefix}-queries"`;
    }
    return match;
  });
  
  // Also normalize any ID that contains "queries" but not "query-" followed by a number
  content = content.replace(/id=["']([^"']*quer[^"']*ies[^"']*)["']/gi, (match, idValue) => {
    // Skip if it's an individual query (query-1, query-2, etc.)
    if (!idValue.match(/query-\d+/)) {
      return `id="${dbPrefix}-queries"`;
    }
    return match;
  });
  
  // Normalize query IDs (query-1-something-long -> query-1)
  content = content.replace(/id=["']([^"']*query-(\d+)[^"']*)["']/gi, (match, idValue, queryNum) => {
    // Only normalize if it's a long query ID, keep simple ones
    if (idValue.length > 20) {
      return `id="${dbPrefix}-query-${queryNum}"`;
    }
    return match;
  });
  
  return content;
}

function prefixIds(content, dbPrefix) {
  // Prefix all id attributes with database prefix
  // Pattern: id="something" -> id="db6-something"
  // Also handles href="#something" -> href="#db6-something"
  
  // First normalize IDs to standard patterns
  content = normalizeIds(content, dbPrefix);
  
  // Prefix IDs in id attributes
  content = content.replace(/id=["']([^"']+)["']/g, (match, idValue) => {
    // Skip if already prefixed or is a special ID
    if (idValue.startsWith(dbPrefix + '-') || idValue.startsWith('json-')) {
      return match;
    }
    return `id="${dbPrefix}-${idValue}"`;
  });
  
  // Prefix IDs in href attributes that point to anchors
  content = content.replace(/href=["']#([^"']+)["']/g, (match, anchorId) => {
    // Skip if already prefixed or is a special anchor
    if (anchorId.startsWith(dbPrefix + '-') || anchorId.startsWith('json-')) {
      return match;
    }
    return `href="#${dbPrefix}-${anchorId}"`;
  });
  
  return content;
}

function extractMainContent(htmlContent) {
  // Try to find main content section
  const mainMatch = htmlContent.match(/<main[^>]*class="main-content"[^>]*>(.*?)<\/main>/s);
  if (mainMatch) {
    return mainMatch[1].trim();
  }
  
  // Try without class
  const mainMatch2 = htmlContent.match(/<main[^>]*>(.*?)<\/main>/s);
  if (mainMatch2) {
    return mainMatch2[1].trim();
  }
  
  // Try body content excluding nav/sidebar
  const bodyMatch = htmlContent.match(/<body[^>]*>(.*?)<\/body>/s);
  if (bodyMatch) {
    let bodyContent = bodyMatch[1];
    // Remove sidebar/nav
    bodyContent = bodyContent.replace(/<nav[^>]*>.*?<\/nav>/gs, '');
    // Remove scripts
    bodyContent = bodyContent.replace(/<script[^>]*>.*?<\/script>/gs, '');
    return bodyContent.trim();
  }
  
  return null;
}

function markdownToHtml(markdownText) {
  // Use marked if available, otherwise use simple converter
  if (marked) {
    // Configure marked options with table support
    marked.setOptions({
      gfm: true,
      breaks: false,
      headerIds: true,
      mangle: false,
      tables: true  // Enable GitHub Flavored Markdown tables
    });
    
    // Convert markdown to HTML
    let html = marked.parse(markdownText);
    
    // Post-process to add proper classes for Prism.js
    html = html.replace(/<pre><code class="language-(\w+)">/g, '<pre class="language-$1"><code class="language-$1">');
    html = html.replace(/<pre><code>/g, '<pre><code>');
    
    // Ensure Mermaid blocks have the class on both pre and code
    html = html.replace(/<pre><code class="language-mermaid">/g, '<pre class="language-mermaid"><code class="language-mermaid">');
    html = html.replace(/<pre><code class="language-mmd">/g, '<pre class="language-mmd"><code class="language-mmd">');
    
    // Ensure tables have proper styling classes
    html = html.replace(/<table>/g, '<table class="data-table">');
    
    return html;
  }
  
  // Simple markdown to HTML converter fallback
  let html = markdownText;
  
  // Headers (with ID support)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  // Code blocks - preserve Mermaid blocks
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang || '';
    // Preserve Mermaid code blocks for client-side rendering
    if (language === 'mermaid' || language === 'mmd') {
      return `<pre class="language-${language}"><code class="language-${language}">${code.trim()}</code></pre>`;
    }
    return `<pre class="language-${language}"><code class="language-${language}">${code.trim()}</code></pre>`;
  });
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  
  // Lists
  html = html.replace(/^\d+\.\s+(.*)$/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
    return '<ol>' + match + '</ol>';
  });
  html = html.replace(/^-\s+(.*)$/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
    if (!match.includes('<ol>')) {
      return '<ul>' + match + '</ul>';
    }
    return match;
  });
  
  // Paragraphs (lines that aren't already wrapped)
  html = html.split('\n').map(line => {
    line = line.trim();
    if (!line || line.startsWith('<') || line.match(/^[#\-\d\.]/)) {
      return line;
    }
    return `<p>${line}</p>`;
  }).join('\n');
  
  // Tables (basic markdown table support)
  html = html.replace(/\|(.+)\|\n\|([\-:\s\|]+)\|\n((?:\|.+\|\n?)+)/g, (match, header, separator, rows) => {
    const headers = header.split('|').map(h => h.trim()).filter(h => h);
    const rowLines = rows.trim().split('\n');
    
    let table = '<table><thead><tr>';
    headers.forEach(h => {
      table += `<th>${h}</th>`;
    });
    table += '</tr></thead><tbody>';
    
    rowLines.forEach(row => {
      const cells = row.split('|').map(c => c.trim()).filter(c => c);
      if (cells.length > 0) {
        table += '<tr>';
        cells.forEach(cell => {
          // Check if cell contains code
          if (cell.includes('`')) {
            cell = cell.replace(/`([^`]+)`/g, '<code>$1</code>');
          }
          table += `<td>${cell}</td>`;
        });
        table += '</tr>';
      }
    });
    
    table += '</tbody></table>';
    return table;
  });
  
  // Horizontal rule
  html = html.replace(/^---$/gim, '<hr>');
  
  return html;
}

function extractDatabaseContent(dbNum) {
  const dbDirName = `db-${dbNum}`; // Directory name (db-6)
  const dbPrefix = `db${dbNum}`;   // Prefix for IDs (db6)
  const dbDir = path.join(clientDbRoot, dbDirName);

  if (!fs.existsSync(dbDir)) {
    console.log(`⚠️  No client/db directory found for ${dbDirName}`);
    return null;
  }

  // Client structure: client/db/db-6/db6-weather-consulting-insurance/ contains db-6.md, db-6_deliverable.json
  const entries = fs.readdirSync(dbDir, { withFileTypes: true });
  let deliverableDir = null;
  for (const e of entries) {
    if (e.isDirectory() && !e.name.startsWith('.')) {
      const subPath = path.join(dbDir, e.name);
      if (fs.existsSync(path.join(subPath, `${dbDirName}.md`)) ||
          fs.existsSync(path.join(subPath, `${dbDirName}_deliverable.json`))) {
        deliverableDir = subPath;
        break;
      }
    }
  }

  if (!deliverableDir) {
    console.log(`⚠️  No deliverable subfolder found in client/db/${dbDirName}`);
    return null;
  }

  // First, try to find markdown file for complete content
  const files = fs.readdirSync(deliverableDir, { recursive: true });
  
  // Look for markdown file in subdirectories (e.g., db6-weather-consulting-insurance/db-6.md)
  let mdFile = null;
  for (const file of files) {
    if (typeof file === 'string') {
      const filePath = path.join(deliverableDir, file);
      const fileName = path.basename(file);
      if ((fileName === `${dbDirName}.md` || fileName === `db-${dbNum}.md`) && 
          !file.includes('node_modules') && 
          fs.existsSync(filePath)) {
        mdFile = file;
        break;
      }
    }
  }
  
  // Also check for markdown in root deliverable directory
  if (!mdFile) {
    const rootMdPath = path.join(deliverableDir, `${dbDirName}.md`);
    if (fs.existsSync(rootMdPath)) {
      mdFile = `${dbDirName}.md`;
    }
  }
  
  let markdownContent = null;
  if (mdFile) {
    const mdPath = path.join(deliverableDir, mdFile);
    try {
      markdownContent = fs.readFileSync(mdPath, 'utf-8');
      console.log(`📄 Found markdown file: ${mdFile}`);
    } catch (error) {
      console.log(`⚠️  Could not read markdown file: ${error.message}`);
    }
  }
  
  // Find documentation HTML file
  const docFile = files.find(f => 
    typeof f === 'string' && 
    f.includes('documentation.html') && 
    !f.includes('node_modules')
  );
  
  if (!docFile && !markdownContent) {
    console.log(`⚠️  No documentation.html or markdown file found for ${dbDirName}`);
    return null;
  }
  
  let htmlContent = '';
  
  // If we have markdown, convert it to HTML (preferred for complete content)
  if (markdownContent) {
    // Convert entire markdown to HTML
    htmlContent = markdownToHtml(markdownContent);
    
    // Extract and structure the header section
    const headerMatch = markdownContent.match(/^# ID: db-(\d+)[\s\S]*?(?=^##|$)/m);
    if (headerMatch) {
      const headerMd = markdownContent.substring(0, markdownContent.indexOf('##', headerMatch.index + 10) || markdownContent.length);
      const headerHtml = markdownToHtml(headerMd);
      
      // Extract h1 and wrap in header tag
      const h1Match = headerHtml.match(/<h1>(.*?)<\/h1>/);
      if (h1Match) {
        const restOfHeader = headerHtml.substring(headerHtml.indexOf('</h1>') + 5);
        htmlContent = `<header id="${dbPrefix}-overview"><h1>${h1Match[1]}</h1>${restOfHeader}</header>` + htmlContent.substring(htmlContent.indexOf('</h1>') + 5);
      }
    }
    
    // Ensure proper section wrapping
    // Add section tags around major sections if not present
    htmlContent = htmlContent.replace(/<h2[^>]*>([^<]*Database Schema[^<]*)<\/h2>/gi, `<section id="${dbPrefix}-schema"><h2>$1</h2>`);
    htmlContent = htmlContent.replace(/<h2[^>]*>([^<]*Data Dictionary[^<]*)<\/h2>/gi, `<section id="${dbPrefix}-schema"><h2>$1</h2>`);
    
    // Close sections before next major h2
    htmlContent = htmlContent.replace(/(<\/table>|<\/div>)\s*(?=<h2[^>]*>)/g, '$1</section>$2');
  } else if (docFile) {
    // Fallback to HTML extraction
    const fullPath = path.join(deliverableDir, docFile);
    try {
      const htmlFileContent = fs.readFileSync(fullPath, 'utf-8');
      htmlContent = extractMainContent(htmlFileContent);
      
      if (!htmlContent || htmlContent.length < 100) {
        console.log(`⚠️  Insufficient content extracted for ${dbDirName} (${htmlContent?.length || 0} chars)`);
        return null;
      }
    } catch (error) {
      console.error(`❌ Error reading ${fullPath}:`, error.message);
      return null;
    }
  }
  
  // Clean up: remove nested main-content divs
  let cleanedContent = htmlContent
    .replace(/<div[^>]*class="main-content"[^>]*>/g, '')
    .replace(/<\/div>\s*<\/div>\s*<!--.*?-->/g, '</div>')
    .replace(/<div[^>]*class="sidebar"[^>]*>.*?<\/div>/gs, '');
  
  // Fix invalid HTML: remove <p> tags that wrap block elements (h1, h2, h3, header, section, etc.)
  // This prevents browser from auto-closing tags and breaking ID attributes
  cleanedContent = cleanedContent.replace(/<p[^>]*>(\s*<h[1-6])/g, '$1');
  cleanedContent = cleanedContent.replace(/(<\/h[1-6]>\s*)<\/p>/g, '$1');
  cleanedContent = cleanedContent.replace(/<p[^>]*>(\s*<header)/g, '$1');
  cleanedContent = cleanedContent.replace(/(<\/header>\s*)<\/p>/g, '$1');
  cleanedContent = cleanedContent.replace(/<p[^>]*>(\s*<section)/g, '$1');
  cleanedContent = cleanedContent.replace(/(<\/section>\s*)<\/p>/g, '$1');
  
  // Prefix all IDs with database prefix (e.g., db6-overview, db6-query-1)
  // This ensures navigation links work correctly
  cleanedContent = prefixIds(cleanedContent, dbPrefix);
  
  console.log(`✅ Extracted ${dbPrefix} (${cleanedContent.length} chars)`);
  return cleanedContent;
}

function main() {
  console.log('📖 Extracting content from deliverable folders...\n');
  
  const databases = {};
  
  for (let dbNum = 6; dbNum <= 15; dbNum++) {
    const dbId = `db${dbNum}`;
    const content = extractDatabaseContent(dbNum);
    
    if (content) {
      databases[dbId] = content;
    }
  }
  
  // Ensure output directory exists
  const outputDir = path.dirname(outputFile);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Write to JSON file
  fs.writeFileSync(
    outputFile,
    JSON.stringify(databases, null, 2),
    'utf-8'
  );
  
  console.log(`\n✅ Extracted ${Object.keys(databases).length} databases`);
  console.log(`📄 Saved to: ${outputFile}`);
  console.log(`\nTotal content size: ${JSON.stringify(databases).length} bytes`);

  // Build website database index from client deliverables (single source for catalog/sidebar)
  try {
    require('./build-website-database.js');
  } catch (e) {
    console.warn('⚠️  Could not build website database index:', e.message);
  }
}

main();
