# Eraser.io C4 Model Import Guide - db-16

**Workspace:** https://app.eraser.io/workspace/xs4eGrR8v2KRhJsJbm4X  
**API Token:** `191Pty6OikJY1NQsy0NI`  
**File:** `C4_ERASER_IO.code`

## Overview

This file contains C4 model architecture diagrams in Eraser.io code format for db-16 Flood Risk Assessment Database. The diagrams model the system at multiple C4 levels, focusing on M&A due diligence use cases.

## Diagrams Included

1. **Level 1: System Context** - Users (M&A Analyst, M&A Manager, Portfolio Manager) and external systems (FEMA, NOAA, USGS, NASA APIs)
2. **Level 2: Container** - Web app, API service, spatial engine, risk calculator, databases
3. **Level 3: Component - API Service** - Detailed API components and services
4. **Level 3: Component - Database Schema** - Database tables and relationships
5. **M&A Use Case 1:** Pre-Acquisition Risk Assessment flow
6. **M&A Use Case 2:** Portfolio-Level Risk Analysis flow
7. **M&A Use Case 3:** Comparative Risk Analysis flow

## Import Instructions

### Method 1: Copy-Paste into Eraser.io

1. Open Eraser.io workspace: https://app.eraser.io/workspace/xs4eGrR8v2KRhJsJbm4X
2. Create new diagram
3. Copy contents of `C4_ERASER_IO.code`
4. Paste into Eraser.io diagram editor
5. Eraser.io will render the diagrams

### Method 2: Import via API

Use the import script with Eraser.io code format:

```bash
cd db-16/docs/c4
python3 ../../scripts/import_diagram_api.py --file C4_ERASER_IO.code --workspace xs4eGrR8v2KRhJsJbm4X
```

## Diagram Structure

Each diagram is defined with:
- **diagram { }** blocks for separate diagrams
- **person**, **system**, **container**, **component**, **database**, **external** elements
- **->** relationships with labels and protocols
- Descriptions in curly braces

## M&A Use Cases Modeled

- **Pre-Acquisition Risk Assessment**: M&A Analyst inputs property location, receives comprehensive risk report
- **Portfolio-Level Risk Analysis**: M&A Manager analyzes entire acquisition target portfolio
- **Comparative Risk Analysis**: Side-by-side comparison of multiple acquisition targets

## Notes

- Eraser.io code format uses simplified syntax
- Each diagram block creates a separate diagram in Eraser.io
- Relationships use arrow notation with optional protocol labels
- Descriptions are included in element definitions

---
**Last Updated:** 2026-02-06
