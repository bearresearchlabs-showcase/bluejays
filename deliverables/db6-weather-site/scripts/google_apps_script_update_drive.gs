/**
 * Google Apps Script to Update Notebooks in Google Drive Folder
 * 
 * This script:
 * 1. Connects to the Drive folder
 * 2. Lists all notebook files (.ipynb)
 * 3. Updates notebooks with failsafe logic
 * 4. Syncs files from local repository (if using Drive API)
 * 
 * Setup Instructions:
 * 1. Open Google Apps Script: https://script.google.com
 * 2. Create new project
 * 3. Paste this script
 * 4. Enable Drive API: Resources > Advanced Google Services > Drive API v2
 * 5. Run updateNotebooks() function
 */

// Configuration
const DRIVE_FOLDER_ID = '1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C';
const DRIVE_FOLDER_URL = 'https://drive.google.com/drive/folders/' + DRIVE_FOLDER_ID;

/**
 * Main function to update all notebooks in the Drive folder
 */
function updateNotebooks() {
  try {
    Logger.log('Starting notebook update process...');
    
    // Get folder
    const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
    Logger.log('Folder found: ' + folder.getName());
    
    // Get all notebook files
    const notebooks = getNotebookFiles(folder);
    Logger.log('Found ' + notebooks.length + ' notebook files');
    
    // Update each notebook
    const results = [];
    notebooks.forEach(function(notebook) {
      try {
        const result = updateNotebookWithFailsafe(notebook);
        results.push({
          name: notebook.getName(),
          success: result.success,
          message: result.message
        });
        Logger.log(notebook.getName() + ': ' + (result.success ? 'Success' : 'Failed - ' + result.message));
      } catch (error) {
        results.push({
          name: notebook.getName(),
          success: false,
          message: error.toString()
        });
        Logger.log('Error updating ' + notebook.getName() + ': ' + error);
      }
    });
    
    // Generate report
    const report = generateReport(results);
    Logger.log('\n' + report);
    
    // Optionally create a report file in Drive
    createReportFile(folder, report, results);
    
    return results;
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    throw error;
  }
}

/**
 * Get all notebook files recursively from folder
 */
function getNotebookFiles(folder) {
  const notebooks = [];
  const files = folder.getFilesByType('application/json'); // .ipynb files are JSON
  
  // Get .ipynb files directly in folder
  while (files.hasNext()) {
    const file = files.next();
    if (file.getName().endsWith('.ipynb')) {
      notebooks.push(file);
    }
  }
  
  // Recursively search subfolders
  const subfolders = folder.getFolders();
  while (subfolders.hasNext()) {
    const subfolder = subfolders.next();
    const subfolderNotebooks = getNotebookFiles(subfolder);
    notebooks.push.apply(notebooks, subfolderNotebooks);
  }
  
  return notebooks;
}

/**
 * Update a notebook file with failsafe logic
 */
function updateNotebookWithFailsafe(file) {
  try {
    // Read notebook content
    const content = file.getBlob().getDataAsString();
    const notebook = JSON.parse(content);
    
    // Check if failsafe already exists
    if (hasFailsafe(notebook)) {
      return {
        success: true,
        message: 'Failsafe already exists'
      };
    }
    
    // Add failsafe cell
    addFailsafeCell(notebook);
    
    // Create backup
    createBackup(file);
    
    // Update file
    const updatedContent = JSON.stringify(notebook, null, 1);
    file.setContent(updatedContent);
    
    return {
      success: true,
      message: 'Failsafe added successfully'
    };
  } catch (error) {
    return {
      success: false,
      message: error.toString()
    };
  }
}

/**
 * Check if notebook already has failsafe logic
 */
function hasFailsafe(notebook) {
  const cells = notebook.cells || [];
  for (let i = 0; i < cells.length; i++) {
    const cell = cells[i];
    if (cell.cell_type === 'code') {
      const source = cell.source.join('');
      if (source.indexOf('FAILSAFE: Force Path Correction') !== -1) {
        return true;
      }
    }
  }
  return false;
}

/**
 * Add failsafe cell to notebook
 */
function addFailsafeCell(notebook) {
  const cells = notebook.cells || [];
  
  // Find insertion point (after environment detection)
  let insertIndex = 0;
  for (let i = 0; i < cells.length; i++) {
    const cell = cells[i];
    if (cell.cell_type === 'code') {
      const source = cell.source.join('');
      if (source.indexOf('ENVIRONMENT DETECTION COMPLETE') !== -1 || 
          source.indexOf('Environment Type:') !== -1) {
        insertIndex = i + 1;
        break;
      }
    }
  }
  
  // Create failsafe cell
  const failsafeCell = {
    cell_type: 'code',
    execution_count: null,
    metadata: {},
    outputs: [],
    source: getFailsafeCode().split('\n')
  };
  
  // Insert cell
  cells.splice(insertIndex, 0, failsafeCell);
  notebook.cells = cells;
}

/**
 * Get failsafe code as string
 */
function getFailsafeCode() {
  return `# ============================================================================
# FAILSAFE: Force Path Correction and Package Installation
# ============================================================================
import sys
import subprocess
import os
from pathlib import Path

def force_install_package(package_name, import_name=None):
    """Force install package using multiple methods."""
    if import_name is None:
        import_name = package_name.split('[')[0].split('==')[0].split('>=')[0]
    
    # Try import first
    try:
        __import__(import_name)
        return True
    except ImportError:
        pass
    
    # Method 1: pip install --user
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '--quiet', package_name], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 2: pip install --break-system-packages (Python 3.12+)
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--break-system-packages', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 3: pip install system-wide
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 4: conda install (if conda available)
    try:
        subprocess.check_call(['conda', 'install', '-y', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    # Method 5: apt-get install (Linux/Docker)
    if os.path.exists('/usr/bin/apt-get'):
        try:
            apt_package = f'python3-{import_name.replace("_", "-")}'
            subprocess.check_call(['apt-get', 'install', '-y', '--quiet', apt_package],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            __import__(import_name)
            return True
        except:
            pass
    
    # Method 6: Direct pip install with --force-reinstall
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--quiet', package_name],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        __import__(import_name)
        return True
    except:
        pass
    
    print(f"⚠️  Warning: Could not install {package_name}, continuing anyway...")
    return False

def correct_file_path(file_path, search_paths=None):
    """Correct file path by searching multiple locations."""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # If path exists, return it
    if file_path.exists():
        return file_path
    
    # Default search paths
    if search_paths is None:
        search_paths = [
            Path.cwd(),
            Path('/workspace/client/db'),
            Path('/workspace/db'),
            Path('/workspace'),
            Path('/content/drive/MyDrive/db'),
            Path('/content/db'),
            Path('/content'),
            Path.home() / 'Documents' / 'AQ' / 'db',
            Path('/Users/machine/Documents/AQ/db'),
        ]
    
    # Search recursively
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Try direct path
        candidate = search_path / file_path.name
        if candidate.exists():
            return candidate
        
        # Try recursive search
        try:
            for found_path in search_path.rglob(file_path.name):
                if found_path.is_file():
                    return found_path
        except:
            continue
    
    # Return original path (will fail later, but at least we tried)
    return file_path

def ensure_packages_installed():
    """Ensure all required packages are installed."""
    required_packages = [
        ('psycopg2-binary', 'psycopg2'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
        ('ipython', 'IPython'),
        ('jupyter', 'jupyter'),
    ]
    
    print("\\n" + "="*80)
    print("FAILSAFE: Ensuring all packages are installed...")
    print("="*80)
    
    for package, import_name in required_packages:
        if force_install_package(package, import_name):
            print(f"✅ {package} installed")
        else:
            print(f"⚠️  {package} installation failed, but continuing...")
    
    print("="*80 + "\\n")

def ensure_paths_correct():
    """Ensure all file paths are correct."""
    print("\\n" + "="*80)
    print("FAILSAFE: Correcting file paths...")
    print("="*80)
    
    # Correct BASE_DIR if needed
    if 'BASE_DIR' not in globals() or not BASE_DIR.exists():
        BASE_DIR = correct_file_path(Path('/Users/machine/Documents/AQ/db'))
        print(f"✅ BASE_DIR corrected: {BASE_DIR}")
    
    # Correct DB_DIR if needed
    if 'DB_DIR' in globals() and DB_DIR and not DB_DIR.exists():
        DB_DIR = correct_file_path(DB_DIR)
        print(f"✅ DB_DIR corrected: {DB_DIR}")
    
    print("="*80 + "\\n")

# Run failsafe checks
ensure_packages_installed()
ensure_paths_correct()

print("✅ Failsafe checks complete")`;
}

/**
 * Create backup of notebook file
 */
function createBackup(file) {
  try {
    const backupName = file.getName() + '.failsafe_backup';
    const existingBackups = file.getParents().next().getFilesByName(backupName);
    
    // Delete existing backup if exists
    while (existingBackups.hasNext()) {
      existingBackups.next().setTrashed(true);
    }
    
    // Create new backup
    file.makeCopy(backupName, file.getParents().next());
    Logger.log('Backup created: ' + backupName);
  } catch (error) {
    Logger.log('Warning: Could not create backup: ' + error);
  }
}

/**
 * Generate update report
 */
function generateReport(results) {
  const successful = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  const total = results.length;
  
  let report = '='.repeat(80) + '\n';
  report += 'NOTEBOOK UPDATE REPORT\n';
  report += '='.repeat(80) + '\n';
  report += 'Timestamp: ' + new Date().toISOString() + '\n';
  report += 'Total notebooks: ' + total + '\n';
  report += 'Successful: ' + successful + '\n';
  report += 'Failed: ' + failed + '\n';
  report += '\n';
  
  if (successful > 0) {
    report += 'SUCCESSFUL UPDATES:\n';
    report += '-'.repeat(80) + '\n';
    results.filter(r => r.success).forEach(function(r) {
      report += '✅ ' + r.name + '\n';
    });
    report += '\n';
  }
  
  if (failed > 0) {
    report += 'FAILED UPDATES:\n';
    report += '-'.repeat(80) + '\n';
    results.filter(r => !r.success).forEach(function(r) {
      report += '❌ ' + r.name + ': ' + r.message + '\n';
    });
    report += '\n';
  }
  
  report += '='.repeat(80) + '\n';
  
  return report;
}

/**
 * Create report file in Drive folder
 */
function createReportFile(folder, report, results) {
  try {
    const reportName = 'notebook_update_report_' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyyMMdd-HHmmss') + '.txt';
    const reportFile = folder.createFile(reportName, report);
    Logger.log('Report file created: ' + reportName);
    return reportFile;
  } catch (error) {
    Logger.log('Warning: Could not create report file: ' + error);
    return null;
  }
}

/**
 * List all files in folder (for debugging)
 */
function listAllFiles() {
  const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
  const files = folder.getFiles();
  const fileList = [];
  
  while (files.hasNext()) {
    const file = files.next();
    fileList.push({
      name: file.getName(),
      id: file.getId(),
      type: file.getMimeType(),
      size: file.getSize(),
      url: file.getUrl()
    });
  }
  
  Logger.log('Files in folder:');
  fileList.forEach(function(file) {
    Logger.log('- ' + file.name + ' (' + file.type + ')');
  });
  
  return fileList;
}

/**
 * Sync specific notebook from local repository (requires Drive API)
 * Note: This requires additional setup and Drive API v2
 */
function syncNotebookFromLocal(notebookName, localContent) {
  try {
    const folder = DriveApp.getFolderById(DRIVE_FOLDER_ID);
    const files = folder.getFilesByName(notebookName);
    
    if (files.hasNext()) {
      const file = files.next();
      file.setContent(localContent);
      Logger.log('Synced: ' + notebookName);
      return true;
    } else {
      // Create new file
      folder.createFile(notebookName, localContent);
      Logger.log('Created: ' + notebookName);
      return true;
    }
  } catch (error) {
    Logger.log('Error syncing ' + notebookName + ': ' + error);
    return false;
  }
}
