# Content Synchronization Guide

## Overview

The Next.js website imports content **only from the client** folder: `client/db/db-{N}/` (db-6 through db-15). Each database's deliverable subfolder (e.g. `db6-weather-consulting-insurance/`) contains `db-{N}.md` or `*_documentation.html`, which is extracted into `lib/database-content.json`.

## Content Sources

Content is extracted from **client/db only**:
- `client/db/db-6/*/db-6.md` (or `*_documentation.html`)
- `client/db/db-7/*/db-7.md` (or `*_documentation.html`)
- … through db-15

## Sync Methods

### 1. Manual Sync

Run the extraction script manually:

```bash
npm run sync-content
```

Or directly:

```bash
node scripts/extract-deliverable-content.js
```

### 2. Automatic Sync on Build

Content is automatically synced before each production build:

```bash
npm run build
```

The build script runs `extract-content` automatically before building.

### 3. Watch Mode (Development)

For active development, use watch mode to automatically sync when files change:

```bash
npm run watch-content
```

This watches all deliverable HTML files and updates `lib/database-content.json` whenever changes are detected.

## How It Works

1. **Content Extraction**: The script reads from `client/db/db-{N}/`, finds the deliverable subfolder (e.g. `db6-weather-consulting-insurance`), and uses `db-{N}.md` or `*documentation.html`.
2. **Content Parsing**: Prefers markdown (converted to HTML); falls back to `<main class="main-content">` from HTML files.
3. **Content Cleaning**: Removes nested `main-content` divs and sidebar elements; normalizes and prefixes IDs.
4. **JSON Storage**: Saves all content to `lib/database-content.json` with database IDs as keys.

## Content Format

The extracted content is stored in `lib/database-content.json`:

```json
{
  "db6": "<div id=\"db6-section\">...</div>",
  "db7": "<div id=\"db7-section\">...</div>",
  ...
}
```

## Troubleshooting

### Content Not Updating

1. **Check file paths**: Ensure content exists under `client/db/db-{N}/<subfolder>/` (e.g. `db-6.md` or `*documentation.html`).
2. **Run manual sync**: Try `npm run sync-content` to see any error messages.
3. **Check file permissions**: Ensure the script can read the client/db files.

### Missing Databases

If a database is missing from the extracted content:

1. Check that `client/db/db-{N}/` exists and contains a subfolder (e.g. `db6-weather-consulting-insurance`).
2. Check that the subfolder contains `db-{N}.md` or `db-{N}_deliverable.json`.
3. Check the console output for warnings about missing files.

### Content Size Issues

If content seems incomplete:

1. Check the console output for extraction warnings
2. Verify the HTML file has a `<main>` tag or substantial body content
3. Ensure the content is at least 100 characters (minimum threshold)

## Integration with Development Workflow

### During Development

1. Make changes to deliverable HTML files
2. Run `npm run watch-content` in a separate terminal
3. Changes are automatically synced to `lib/database-content.json`
4. Next.js dev server will hot-reload with new content

### Before Deployment

1. Ensure all deliverable files are up to date
2. Run `npm run build` (automatically syncs content)
3. Verify build succeeds
4. Deploy to Vercel

## File Structure

```
apps/website/
├── scripts/
│   ├── extract-deliverable-content.js  # Main extraction script
│   └── watch-and-sync.js               # Watch mode script
├── lib/
│   └── database-content.json          # Extracted content (generated)
└── components/
    └── MainContent.tsx                 # Component that uses the JSON
```

## Notes

- Content extraction preserves HTML structure and formatting
- Prism.js syntax highlighting is handled client-side
- Large content files (~3MB total) are loaded at runtime
- Consider code splitting for very large content sections if performance becomes an issue
