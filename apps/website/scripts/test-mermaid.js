#!/usr/bin/env node
const marked = require('marked');

// Test if marked preserves Mermaid blocks
const testMd = `# Test

\`\`\`mermaid
erDiagram
    TABLE1 ||--o{ TABLE2 : "has"
\`\`\`

Some text after.
`;

marked.setOptions({
  gfm: true,
  breaks: false,
  headerIds: true,
  mangle: false,
  tables: true
});

const html = marked.parse(testMd);
console.log('Marked output:');
console.log(html);
console.log('\nHas language-mermaid class:', html.includes('language-mermaid'));
console.log('Has pre tag:', html.includes('<pre'));
console.log('Has code tag:', html.includes('<code'));
