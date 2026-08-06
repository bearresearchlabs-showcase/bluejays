# Google Apps Script Setup Guide

## Overview

This guide explains how to set up and use the Google Apps Script to update notebooks in your Google Drive folder.

## Google Drive Folder

- **URL:** https://drive.google.com/drive/folders/1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C?usp=drive_link
- **Folder ID:** `1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C`

## Setup Instructions

### Step 1: Open Google Apps Script

1. Go to [Google Apps Script](https://script.google.com)
2. Sign in with your Google account
3. Click **"New Project"**

### Step 2: Copy Script Code

1. Open `scripts/google_apps_script_update_drive.gs` from this repository
2. Copy all the code
3. Paste into the Apps Script editor

### Step 3: Enable Drive API

1. In Apps Script editor, click **"Resources"** → **"Advanced Google Services"**
2. Find **"Drive API v2"** and toggle it **ON**
3. Click **"OK"**

### Step 4: Authorize Script

1. Click **"Run"** → **"updateNotebooks"**
2. Click **"Review Permissions"**
3. Select your Google account
4. Click **"Advanced"** → **"Go to [Project Name] (unsafe)"**
5. Click **"Allow"** to grant permissions

### Step 5: Run Script

1. Click **"Run"** → **"updateNotebooks"**
2. Check **"Execution log"** for results
3. Review report file created in Drive folder

## Functions Available

### `updateNotebooks()`

Main function to update all notebooks in the Drive folder.

**What it does:**
- Finds all `.ipynb` files in the folder (recursively)
- Checks if failsafe logic exists
- Adds failsafe cell if missing
- Creates backup files
- Generates update report

**Usage:**
```javascript
// In Apps Script editor
updateNotebooks();
```

### `listAllFiles()`

Lists all files in the Drive folder (for debugging).

**Usage:**
```javascript
listAllFiles();
```

### `syncNotebookFromLocal(notebookName, localContent)`

Syncs a specific notebook from local repository to Drive.

**Usage:**
```javascript
// Requires Drive API v2
const localContent = "..." // JSON content of notebook
syncNotebookFromLocal("db-6.ipynb", localContent);
```

## Manual Execution

### Run from Apps Script Editor

1. Open Apps Script project
2. Select `updateNotebooks` function
3. Click **"Run"** button
4. Review execution log

### Run from Google Sheets (Optional)

1. Create new Google Sheet
2. Go to **"Extensions"** → **"Apps Script"**
3. Paste script code
4. Add menu item:
   ```javascript
   function onOpen() {
     SpreadsheetApp.getUi()
       .createMenu('Notebook Updates')
       .addItem('Update All Notebooks', 'updateNotebooks')
       .addToUi();
   }
   ```
5. Refresh sheet and use menu

### Schedule Automatic Updates

1. In Apps Script editor, click **"Triggers"** (clock icon)
2. Click **"Add Trigger"**
3. Configure:
   - **Function:** `updateNotebooks`
   - **Event source:** Time-driven
   - **Type:** Daily, Weekly, or Monthly
   - **Time:** Choose preferred time
4. Click **"Save"**

## Troubleshooting

### Permission Errors

**Problem:** Script can't access Drive folder

**Solution:**
1. Ensure folder is shared with your Google account
2. Re-authorize script: **"Run"** → **"Review Permissions"**
3. Check folder ID is correct: `1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C`

### File Not Found

**Problem:** Script can't find notebook files

**Solution:**
1. Verify files are `.ipynb` format
2. Check files are in the correct folder
3. Use `listAllFiles()` to debug

### JSON Parse Errors

**Problem:** Error parsing notebook JSON

**Solution:**
1. Verify notebook files are valid JSON
2. Check file encoding (should be UTF-8)
3. Manually validate JSON structure

### Execution Timeout

**Problem:** Script times out

**Solution:**
1. Process fewer files at once
2. Increase execution timeout: **"Run"** → **"Change execution timeout"**
3. Split into smaller batches

## Advanced Usage

### Custom Folder ID

To use a different folder:

```javascript
const DRIVE_FOLDER_ID = 'YOUR_FOLDER_ID_HERE';
```

### Filter Specific Files

To update only specific notebooks:

```javascript
function updateSpecificNotebooks() {
  const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
  const notebooks = getNotebookFiles(folder);
  
  // Filter by name pattern
  const filtered = notebooks.filter(function(file) {
    return file.getName().indexOf('db-6') !== -1;
  });
  
  // Update filtered notebooks
  filtered.forEach(function(notebook) {
    updateNotebookWithFailsafe(notebook);
  });
}
```

### Custom Failsafe Code

To use custom failsafe code:

```javascript
function getFailsafeCode() {
  // Return your custom failsafe code
  return `# Your custom code here`;
}
```

## Integration with Local Scripts

### Download from Drive, Update Locally

```bash
# 1. Download notebooks from Drive
python3 scripts/download_and_update_from_drive.py

# 2. Update with failsafe locally
python3 scripts/update_notebooks_failsafe.py --root-dir downloads/drive_notebooks

# 3. Upload back to Drive (manual or via Apps Script)
```

### Sync Local Updates to Drive

Use `syncNotebookFromLocal()` function or Drive API to upload updated notebooks.

## Security Considerations

1. **Permissions:** Script requires Drive access - review permissions carefully
2. **Backups:** Script creates backup files automatically
3. **Validation:** Always verify updates before running on production files
4. **Testing:** Test on a copy of folder first

## Best Practices

1. **Backup First:** Always backup files before bulk updates
2. **Test Script:** Run on test folder first
3. **Review Logs:** Check execution logs for errors
4. **Incremental Updates:** Update files in batches if many files
5. **Monitor Triggers:** Review scheduled triggers regularly

## Related Files

- `scripts/google_apps_script_update_drive.gs` - Apps Script code
- `scripts/download_and_update_from_drive.py` - Python download script
- `scripts/update_notebooks_failsafe.py` - Local update script
- `NOTEBOOK_UPDATE_README.md` - Notebook update guide

## Support

For issues:
1. Check execution logs in Apps Script
2. Verify folder permissions
3. Test with `listAllFiles()` function
4. Review troubleshooting section above

---

**Last Updated:** 2026-02-08
**Version:** 1.0
