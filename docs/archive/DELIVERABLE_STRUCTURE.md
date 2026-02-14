# Standard Deliverable Structure

**Date:** February 3, 2026

---

## Standard Structure for db-1 through db-5

Each database deliverable follows this consistent hierarchical structure:

```
db-{N}/
├── README.md              # Deliverable overview
├── queries/
│   └── queries.md         # 30+ extremely complex SQL queries
├── results/
│   └── *.json             # Test results and validation reports (JSON only)
├── docs/
│   ├── README.md          # Database documentation
│   ├── SCHEMA.md          # Schema documentation
│   ├── DATA_DICTIONARY.md # Data dictionary
│   └── *.ipynb            # Jupyter notebooks
├── data/
│   ├── schema.sql         # Database schema
│   ├── data.sql           # Sample data
│   └── *.dump             # Database dumps
└── scripts/
    ├── *.py               # Python scripts
    ├── *.sh               # Shell scripts
    └── requirements.txt   # Python dependencies
```

---

## Directory Purposes

### `queries/`
- **Required:** Yes
- **Contents:** `queries.md` with 30+ extremely complex SQL queries
- **Purpose:** Main deliverable - SQL queries

### `results/`
- **Required:** Yes
- **Contents:** JSON files only (test results, validation reports)
- **Purpose:** Test results and validation data

### `docs/`
- **Required:** No (but recommended)
- **Contents:** Documentation files (README.md, SCHEMA.md, *.ipynb)
- **Purpose:** Database documentation and notebooks

### `data/`
- **Required:** No
- **Contents:** SQL files (schema.sql, data.sql, *.dump)
- **Purpose:** Database schema and data files

### `scripts/`
- **Required:** No
- **Contents:** Python scripts (*.py), shell scripts (*.sh), requirements.txt
- **Purpose:** Utility scripts for the database

---

## Consistency Rules

1. **All databases must have:**
   - `queries/queries.md` - SQL queries
   - `results/` - JSON results only

2. **Root directory should contain:**
   - `README.md` - Deliverable overview only
   - No other files (scripts, docs, data moved to subdirectories)

3. **File organization:**
   - All JSON files → `results/`
   - All markdown docs → `docs/`
   - All SQL files → `data/`
   - All scripts → `scripts/`
   - All notebooks → `docs/`

---

## Status

✅ All databases (db-1 through db-5) standardized to this structure.
