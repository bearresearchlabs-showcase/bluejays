#!/usr/bin/env python3
"""
Standardize db-1 through db-5 into consistent hierarchical deliverable structure
"""

import shutil
from pathlib import Path
from datetime import datetime

class DeliverableStandardizer:
    def __init__(self, root_dir='.'):
        self.root = Path(root_dir)
        self.standard_structure = {
            'queries': {
                'required': True,
                'files': ['queries.md']
            },
            'results': {
                'required': True,
                'files': ['*.json']
            },
            'docs': {
                'required': False,
                'files': ['README.md', 'SCHEMA.md', 'DATA_DICTIONARY.md']
            },
            'data': {
                'required': False,
                'files': ['*.sql', '*.dump']
            },
            'scripts': {
                'required': False,
                'files': ['*.py', '*.sh']
            }
        }

    def analyze_database_structure(self, db_num):
        """Analyze current structure of a database"""
        db_dir = self.root / f'db-{db_num}'
        if not db_dir.exists():
            return None

        structure = {
            'name': f'db-{db_num}',
            'directories': {},
            'root_files': [],
            'issues': []
        }

        # List all items
        for item in db_dir.iterdir():
            if item.is_dir():
                structure['directories'][item.name] = {
                    'path': item,
                    'files': list(item.rglob('*')) if item.name != 'extracted' else []
                }
            elif item.is_file():
                structure['root_files'].append(item.name)

        return structure

    def create_standard_structure(self, db_num):
        """Create standard directory structure for a database"""
        db_dir = self.root / f'db-{db_num}'

        # Create standard directories
        standard_dirs = ['queries', 'results', 'docs', 'data', 'scripts']
        for dir_name in standard_dirs:
            (db_dir / dir_name).mkdir(exist_ok=True)

    def organize_database(self, db_num):
        """Organize a database into standard structure"""
        db_dir = self.root / f'db-{db_num}'
        if not db_dir.exists():
            return False

        print(f"\nOrganizing db-{db_num}...")

        # Create standard structure
        self.create_standard_structure(db_num)

        moved_items = []

        # Move queries.md to queries/
        queries_files = list(db_dir.rglob('queries.md'))
        for qf in queries_files:
            if 'queries' not in str(qf.parent.relative_to(db_dir)):
                dest = db_dir / 'queries' / 'queries.md'
                if qf != dest:
                    if dest.exists():
                        dest.unlink()
                    shutil.move(str(qf), str(dest))
                    moved_items.append(f"queries.md -> queries/")

        # Move JSON results to results/
        json_files = [f for f in db_dir.rglob('*.json')
                     if 'results' not in str(f.parent.relative_to(db_dir))
                     and f.parent != db_dir / 'results']
        for jf in json_files:
            dest = db_dir / 'results' / jf.name
            if jf != dest:
                if dest.exists():
                    # Handle duplicates
                    dest = db_dir / 'results' / f"{jf.parent.name}_{jf.name}"
                shutil.move(str(jf), str(dest))
                moved_items.append(f"{jf.name} -> results/")

        # Move documentation files to docs/
        doc_patterns = ['README.md', 'SCHEMA.md', 'DATA_DICTIONARY.md', '*_DOCUMENTATION.md', '*_SUMMARY.md', '*_REPORT.md']
        for pattern in doc_patterns:
            doc_files = list(db_dir.rglob(pattern))
            for df in doc_files:
                if 'docs' not in str(df.parent.relative_to(db_dir)) and df.parent != db_dir / 'docs':
                    dest = db_dir / 'docs' / df.name
                    if df != dest:
                        if dest.exists():
                            dest = db_dir / 'docs' / f"{df.parent.name}_{df.name}"
                        shutil.move(str(df), str(dest))
                        moved_items.append(f"{df.name} -> docs/")

        # Move SQL/data files to data/
        sql_files = [f for f in db_dir.rglob('*.sql')
                    if 'data' not in str(f.parent.relative_to(db_dir))
                    and f.parent != db_dir / 'data'
                    and 'queries' not in str(f.parent.relative_to(db_dir))]
        for sf in sql_files:
            dest = db_dir / 'data' / sf.name
            if sf != dest:
                if dest.exists():
                    dest = db_dir / 'data' / f"{sf.parent.name}_{sf.name}"
                shutil.move(str(sf), str(dest))
                moved_items.append(f"{sf.name} -> data/")

        # Move scripts to scripts/
        script_files = list(db_dir.rglob('*.py')) + list(db_dir.rglob('*.sh'))
        script_files = [f for f in script_files
                       if 'scripts' not in str(f.parent.relative_to(db_dir))
                       and f.parent != db_dir / 'scripts']
        for script in script_files:
            dest = db_dir / 'scripts' / script.name
            if script != dest:
                if dest.exists():
                    dest = db_dir / 'scripts' / f"{script.parent.name}_{script.name}"
                shutil.move(str(script), str(dest))
                moved_items.append(f"{script.name} -> scripts/")

        # Move notebooks to docs/ or keep in root
        notebooks = list(db_dir.rglob('*.ipynb'))
        for nb in notebooks:
            if nb.parent != db_dir:
                dest = db_dir / 'docs' / nb.name
                if nb != dest:
                    shutil.move(str(nb), str(dest))
                    moved_items.append(f"{nb.name} -> docs/")

        # Create README.md in docs/ if it doesn't exist
        if not (db_dir / 'docs' / 'README.md').exists():
            # Try to find existing README
            existing_readme = None
            for readme in db_dir.rglob('README.md'):
                if readme.parent != db_dir / 'docs':
                    existing_readme = readme
                    break

            if existing_readme:
                shutil.move(str(existing_readme), str(db_dir / 'docs' / 'README.md'))
                moved_items.append("README.md -> docs/")

        if moved_items:
            print(f"  ✅ Moved {len(moved_items)} items")
            for item in moved_items[:10]:
                print(f"     - {item}")
            if len(moved_items) > 10:
                print(f"     ... and {len(moved_items) - 10} more")
        else:
            print(f"  ✅ Already organized")

        return True

    def create_deliverable_readme(self, db_num, db_info):
        """Create a standard README.md for the deliverable"""
        db_dir = self.root / f'db-{db_num}'
        readme_path = db_dir / 'README.md'

        # Get database name from existing structure
        db_name = f"Database {db_num}"
        if (db_dir / 'docs' / 'README.md').exists():
            # Try to extract name from existing README
            try:
                content = (db_dir / 'docs' / 'README.md').read_text()
                # Look for title patterns
                import re
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    db_name = title_match.group(1)
            except:
                pass

        readme_content = f"""# {db_name}

**Deliverable:** db-{db_num}
**Status:** ✅ Complete

## Structure

```
db-{db_num}/
├── queries/
│   └── queries.md          # 30+ extremely complex SQL queries
├── results/
│   └── *.json              # Test results and validation reports
├── docs/
│   ├── README.md           # Database documentation
│   └── *.md                 # Additional documentation
├── data/
│   └── *.sql               # Database schema and data files
└── scripts/
    └── *.py, *.sh          # Utility scripts
```

## Contents

- **Queries:** 30+ extremely complex SQL queries in `queries/queries.md`
- **Results:** JSON test results in `results/`
- **Documentation:** Database documentation in `docs/`
- **Data:** Schema and data files in `data/`

## Usage

See `queries/queries.md` for SQL queries.
See `results/` for test results.
See `docs/README.md` for database documentation.

---
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""

        readme_path.write_text(readme_content)
        return readme_path

    def standardize_all(self):
        """Standardize all databases"""
        print("=" * 70)
        print("STANDARDIZING DELIVERABLES (db-1 through db-5)")
        print("=" * 70)

        for db_num in range(1, 6):
            if self.organize_database(db_num):
                # Create deliverable README
                db_info = self.analyze_database_structure(db_num)
                if db_info:
                    self.create_deliverable_readme(db_num, db_info)
                    print(f"  ✅ Created README.md")

        print("\n" + "=" * 70)
        print("STANDARDIZATION SUMMARY")
        print("=" * 70)

        # Verify structure
        for db_num in range(1, 6):
            db_dir = self.root / f'db-{db_num}'
            if db_dir.exists():
                print(f"\ndb-{db_num}:")
                required_dirs = ['queries', 'results']
                for req_dir in required_dirs:
                    req_path = db_dir / req_dir
                    if req_path.exists():
                        file_count = len(list(req_path.glob('*')))
                        print(f"  ✅ {req_dir}/ ({file_count} items)")
                    else:
                        print(f"  ❌ {req_dir}/ (MISSING)")

                optional_dirs = ['docs', 'data', 'scripts']
                for opt_dir in optional_dirs:
                    opt_path = db_dir / opt_dir
                    if opt_path.exists():
                        file_count = len(list(opt_path.glob('*')))
                        print(f"  📁 {opt_dir}/ ({file_count} items)")

        print("\n" + "=" * 70)
        print("Standardization complete!")
        print("=" * 70)

if __name__ == '__main__':
    standardizer = DeliverableStandardizer()
    standardizer.standardize_all()
