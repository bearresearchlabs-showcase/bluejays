#!/usr/bin/env node
const marked = require('marked');

// Test markdown table conversion
const testMd = `### Data Dictionary

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| \`composite_id\` | \`VARCHAR(255)\` | PRIMARY KEY | - |
| \`product_type\` | \`VARCHAR(100)\` | NOT NULL | 'Precipitation', 'Cloud', 'Storm', 'Fire', 'Temperature' |`;

marked.setOptions({
  gfm: true,
  breaks: false,
  headerIds: true,
  mangle: false,
  tables: true
});

const html = marked.parse(testMd);
console.log('Converted HTML:');
console.log(html);
console.log('\nHas table tag:', html.includes('<table'));
