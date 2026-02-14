#!/usr/bin/env node
/**
 * Fix db6 content structure - ensure proper header and section IDs
 */

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '../lib/database-content.json');
const content = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

if (content.db6) {
  let db6Content = content.db6;

  // Fix header structure - should have proper h1 and description
  const headerMatch = db6Content.match(/<header id="db6-overview">(.*?)<\/header>/s);
  if (headerMatch) {
    const headerContent = headerMatch[1];
    // Check if it has the description paragraph
    if (!headerContent.includes('Comprehensive documentation')) {
      // Add the description paragraph
      const newHeader = `<header id="db6-overview">
            <h1>Weather Consulting Database</h1>
            <p>Comprehensive documentation for database db-6, including complete schema documentation, all SQL queries with business context, and usage instructions. This database and its queries are sourced from production systems used by businesses with <strong>$1M+ Annual Recurring Revenue (ARR)</strong>.</p>
        </header>`;
      db6Content = db6Content.replace(/<header id="db6-overview">.*?<\/header>/s, newHeader);
    }
  }

  // Ensure Backstory has proper ID
  db6Content = db6Content.replace(/<h2>Backstory<\/h2>/g, '<h2 id="db6-backstory">Backstory</h2>');

  // Ensure Data Dictionary section has proper ID and is wrapped in section
  if (db6Content.includes('Data Dictionary') && !db6Content.includes('id="db6-data-dictionary"')) {
    // Find the Data Dictionary h2
    db6Content = db6Content.replace(/<h2[^>]*>([^<]*Data Dictionary[^<]*)<\/h2>/i, '<section id="db6-data-dictionary"><h2 id="db6-data-dictionary">$1</h2>');

    // Find where to close the section (before next major section or end)
    const schemaSection = db6Content.indexOf('<section id="db6-schema"');
    if (schemaSection !== -1) {
      // Close data dictionary section before schema section
      const beforeSchema = db6Content.substring(0, schemaSection);
      const afterSchema = db6Content.substring(schemaSection);
      db6Content = beforeSchema + '</section>' + afterSchema;
    } else {
      // Close at end if no schema section found
      const queriesSection = db6Content.indexOf('<section id="db6-queries"');
      if (queriesSection !== -1) {
        const beforeQueries = db6Content.substring(0, queriesSection);
        const afterQueries = db6Content.substring(queriesSection);
        db6Content = beforeQueries + '</section>' + afterQueries;
      }
    }
  }

  content.db6 = db6Content;
  fs.writeFileSync(filePath, JSON.stringify(content, null, 2));
  console.log('✓ Fixed header and section structure');
}
