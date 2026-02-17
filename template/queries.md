# Healthcare Hospital Database — Query Documentation

## Database Overview

```yaml
db_id: healthcare_hospital
domain: Healthcare / Hospital Operations
source: [License source, e.g. Kaggle, direct vendor, synthetic]
license_type: [Commercial / Open / Academic]
license_cost: [Annual cost if applicable]
tables: 12
total_rows: ~1.2M
date_range: 2020-01-01 to 2026-12-31
sql_dialect: SQLite
```

## Purpose

```text
This database models a mid-size hospital's operational data including patient admissions,
diagnoses, physician assignments, billing, lab results, and departmental staffing. It is
designed to support text-to-SQL training across clinical, financial, and operational
query types commonly encountered in healthcare analytics.
```

## Use Case

```text
Target use cases for this database:
- Clinical operations: length of stay, readmission analysis, diagnosis patterns
- Revenue cycle: billing aggregation, physician productivity, payer mix
- Resource planning: bed utilization, staffing ratios, department throughput
- Quality metrics: mortality rates, complication tracking, patient satisfaction
```

## Business Value

```text
Healthcare databases represent one of the highest-value domains for text-to-SQL because:
- Queries require domain knowledge (ICD codes, CPT codes, clinical definitions)
- Data relationships are complex (patient → visit → diagnosis → billing chains)
- Stakeholders are non-technical (physicians, administrators, quality officers)
- Errors have real consequences (misreported readmission rates affect reimbursement)
This makes the evidence field critical — the model must learn WHY the SQL is correct.
```

## Training Data Field Definitions

Each query entry is structured to serve the text-to-SQL RLHF training pipeline.
Fields are grouped by their role in the training loop and their benchmark alignment.

### BIRD-SQL Standard Fields (benchmark-compatible)

| Field | Type | Training Role | Benchmark Source |
|-------|------|--------------|-----------------|
| `db_id` | string | Database routing — tells the agent which schema to load | BIRD-SQL `db_id`, LiveSQLBench `selected_database` |
| `question_id` | integer (1–30) | Unique identifier per query within this database | BIRD-SQL `question_id`, LiveSQLBench `instance_id` |
| `question` | string | **Agent input** — the natural-language prompt the model receives at inference time | BIRD-SQL `question`, LiveSQLBench `query` / `normal_query` |
| `SQL` | string | **Golden solution** — the correct SQL the agent must learn to generate | BIRD-SQL `SQL` (uppercase), LiveSQLBench `sol_sql` |
| `evidence` | string | **Chain-of-thought (COT)** — domain reasoning that bridges the question to the SQL; teaches the agent to decompose intent into schema-grounded logic | BIRD-SQL `evidence`, LiveSQLBench `external_knowledge` |
| `difficulty` | string | **Curriculum signal** — controls training distribution; values: `simple` / `moderate` / `challenging` | BIRD-SQL `difficulty` (same 3 levels) |

### Training Extension Fields (RLHF enhancements beyond benchmark)

| Field | Type | Training Role |
|-------|------|--------------|
| `query_category` | string | **Curriculum coverage** — SQL pattern label ensuring the 30-query set covers all required skills: `aggregation`, `aggregation/ranking`, `filtering/lookup`, `join`, `window/self-join`, `subquery/cte`, `date-arithmetic` |
| `tables_used` | string[] | **Schema-linking ground truth** — the tables the agent should identify before generating SQL; used to evaluate the agent's table-selection accuracy |
| `schema_context` | object | **Inference-time context** — the per-query schema subset the agent sees; simulates real-world partial-schema retrieval where the agent does not see the full database DDL |
| `expected_output` | string | **Execution accuracy (EX) reward signal** — the stringified 2D array of the SQL result set; used by the reward model to verify the generated SQL produces the correct output |

### How Fields Map to the Training Loop

```text
TRAINING PIPELINE:

  1. INPUT PROMPT       → question + schema_context + evidence
     (what the agent sees at inference time)

  2. GOLDEN OUTPUT      → SQL
     (what the agent must learn to produce)

  3. REWARD SIGNAL      → expected_output
     (execution match confirms the generated SQL is functionally correct)

  4. CURRICULUM CONTROL → difficulty + query_category + tables_used
     (ensures balanced training across skill levels and SQL patterns)

  5. EVALUATION         → tables_used for schema-linking accuracy
                        → expected_output for execution accuracy (EX)
                        → SQL for exact-match accuracy (EM)
```

## Schema

### Table: patients

```sql
CREATE TABLE patients (
    patient_id    INTEGER PRIMARY KEY,
    first_name    VARCHAR(50),
    last_name     VARCHAR(50),
    date_of_birth DATE,           -- e.g. '1965-03-22'
    gender        VARCHAR(10),     -- 'Male', 'Female', 'Other'
    admit_date    DATE,            -- date of this admission
    discharge_date DATE,           -- date of this discharge (NULL if still admitted)
    department    VARCHAR(50),     -- 'Emergency', 'Cardiology', 'Orthopedics', etc.
    status        VARCHAR(20)      -- 'admitted', 'discharged', 'transferred'
);
-- Sample values:
-- (1, 'John', 'Doe', '1965-03-22', 'Male', '2024-10-15', '2024-10-22', 'Cardiology', 'discharged')
-- (2, 'Jane', 'Smith', '1980-07-11', 'Female', '2024-11-01', NULL, 'Emergency', 'admitted')
-- Row count: ~45,000
```

### Table: diagnoses

```sql
CREATE TABLE diagnoses (
    diagnosis_id   INTEGER PRIMARY KEY,
    patient_id     INTEGER REFERENCES patients(patient_id),
    icd_code       VARCHAR(10),    -- ICD-10 code, e.g. 'I21.0' = acute ST-elevation MI
    description    TEXT,            -- 'Acute ST elevation myocardial infarction of anterior wall'
    diagnosis_type VARCHAR(10)      -- 'primary', 'secondary', 'admitting'
);
-- Sample values:
-- (1, 1, 'I21.0', 'Acute ST elevation myocardial infarction of anterior wall', 'primary')
-- (2, 1, 'E11.9', 'Type 2 diabetes mellitus without complications', 'secondary')
-- Row count: ~78,000
```

### Table: billing

```sql
CREATE TABLE billing (
    billing_id   INTEGER PRIMARY KEY,
    visit_id     INTEGER REFERENCES visits(visit_id),
    amount       DECIMAL(10,2),   -- billed amount in USD
    billing_code VARCHAR(10),      -- CPT code, e.g. '99213' = office visit level 3
    payer        VARCHAR(50),      -- 'Medicare', 'BlueCross', 'Self-Pay', etc.
    status       VARCHAR(20)       -- 'billed', 'paid', 'denied', 'pending'
);
-- Sample values:
-- (1, 1, 1250.00, '99223', 'Medicare', 'paid')
-- (2, 1, 450.00, '93000', 'Medicare', 'billed')
-- Row count: ~120,000
```

### Table: visits

```sql
CREATE TABLE visits (
    visit_id      INTEGER PRIMARY KEY,
    patient_id    INTEGER REFERENCES patients(patient_id),
    physician_id  INTEGER REFERENCES physicians(physician_id),
    visit_type    VARCHAR(20),     -- 'outpatient', 'inpatient', 'emergency'
    visit_date    DATE,
    department    VARCHAR(50)
);
-- Row count: ~85,000
```

### Table: physicians

```sql
CREATE TABLE physicians (
    physician_id   INTEGER PRIMARY KEY,
    physician_name VARCHAR(100),
    specialty      VARCHAR(50),    -- 'Cardiology', 'Emergency Medicine', 'Internal Medicine'
    department     VARCHAR(50),
    hire_date      DATE
);
-- Row count: ~200
```

## Domain Knowledge

```text
Key domain concepts required to write correct queries against this database:

ICD-10 CODE STRUCTURE:
- Codes starting with 'I' = diseases of the circulatory system (cardiac)
- Codes starting with 'E' = endocrine/metabolic (diabetes, obesity)
- Codes starting with 'J' = diseases of the respiratory system
- Codes starting with 'S'/'T' = injury/trauma

CLINICAL DEFINITIONS:
- Length of Stay (LOS): discharge_date - admit_date, measured in days
- Readmission: same patient_id admitted again within 30 days of discharge
- Case Mix Index (CMI): average DRG weight across admissions; higher = sicker patients
- Mortality rate: deaths / total admissions for a given period

BILLING/FINANCIAL:
- CPT codes: 5-digit codes for procedures/services (99213 = office visit level 3)
- Revenue = SUM(billing.amount) WHERE billing.status IN ('billed', 'paid')
- Net collections = SUM(billing.amount) WHERE billing.status = 'paid'
- Denial rate = COUNT(status='denied') / COUNT(*) for a given period

TIME CONVENTIONS:
- All dates are in ISO 8601 format (YYYY-MM-DD)
- Fiscal year = calendar year for this hospital
- Q1 = Jan-Mar, Q2 = Apr-Jun, Q3 = Jul-Sep, Q4 = Oct-Dec
```

## Query Difficulty Distribution

```text
Target distribution across 30 queries:
- simple (10 queries): Single-table, basic aggregation, straightforward filters
- moderate (12 queries): 2-3 table joins, GROUP BY + HAVING, date arithmetic
- challenging (8 queries): CTEs, self-joins, window functions, correlated subqueries

Category coverage:
- Aggregation/Ranking: 8 queries
- Filtering/Lookup: 5 queries
- Join (multi-table): 7 queries
- Window/Self-Join: 4 queries
- Subquery/CTE: 4 queries
- Date Arithmetic: 2 queries
```

## Queries

### Query 1 — moderate / aggregation

```json
{
  "db_id": "healthcare_hospital",
  "question_id": 1,
  "question": "What is the average length of stay for patients admitted with cardiac conditions in Q4 2024?",
  "SQL": "SELECT AVG(JULIANDAY(discharge_date) - JULIANDAY(admit_date)) AS avg_los\nFROM patients p\nJOIN diagnoses d ON p.patient_id = d.patient_id\nWHERE d.icd_code LIKE 'I%'\n  AND p.admit_date BETWEEN '2024-10-01' AND '2024-12-31';",
  "evidence": "Length of stay is calculated as discharge_date minus admit_date in days. Cardiac conditions are identified by ICD-10 codes starting with 'I' (diseases of the circulatory system). Q4 2024 refers to October 1 through December 31, 2024.",
  "difficulty": "moderate",
  "query_category": "aggregation",
  "tables_used": ["patients", "diagnoses"],
  "schema_context": {
    "patients": {
      "patient_id": "INTEGER PRIMARY KEY — unique patient identifier",
      "admit_date": "DATE — date of hospital admission",
      "discharge_date": "DATE — date of hospital discharge"
    },
    "diagnoses": {
      "patient_id": "INTEGER FK → patients.patient_id",
      "icd_code": "VARCHAR(10) — ICD-10 code, e.g. 'I21.0' = acute ST-elevation MI"
    }
  },
  "expected_output": "[[7.3]]"
}
```

### Query 2 — challenging / window/self-join

```json
{
  "db_id": "healthcare_hospital",
  "question_id": 2,
  "question": "Which department had the highest number of readmissions within 30 days during 2024?",
  "SQL": "WITH readmissions AS (\n  SELECT\n    p1.department,\n    p1.patient_id,\n    p1.discharge_date AS first_discharge,\n    MIN(p2.admit_date) AS readmit_date\n  FROM patients p1\n  JOIN patients p2\n    ON p1.patient_id = p2.patient_id\n    AND p2.admit_date > p1.discharge_date\n    AND p2.admit_date <= DATE(p1.discharge_date, '+30 days')\n  WHERE p1.discharge_date BETWEEN '2024-01-01' AND '2024-12-31'\n  GROUP BY p1.department, p1.patient_id, p1.discharge_date\n)\nSELECT department, COUNT(*) AS readmission_count\nFROM readmissions\nGROUP BY department\nORDER BY readmission_count DESC\nLIMIT 1;",
  "evidence": "A readmission is defined as a new admission for the same patient_id within 30 days of a prior discharge_date. The 30-day window is calculated using DATE(discharge_date, '+30 days') in SQLite. Only index admissions with discharge dates in 2024 are counted.",
  "difficulty": "challenging",
  "query_category": "window/self-join",
  "tables_used": ["patients"],
  "schema_context": {
    "patients": {
      "patient_id": "INTEGER — same patient can have multiple rows (one per visit)",
      "department": "VARCHAR(50) — 'Emergency', 'Cardiology', 'Orthopedics'",
      "admit_date": "DATE",
      "discharge_date": "DATE"
    }
  },
  "expected_output": "[['Emergency', 142]]"
}
```

### Query 3 — simple / aggregation/ranking

```json
{
  "db_id": "healthcare_hospital",
  "question_id": 3,
  "question": "List the top 5 physicians by total billed amount for outpatient visits in 2024.",
  "SQL": "SELECT\n  ph.physician_name,\n  SUM(b.amount) AS total_billed\nFROM billing b\nJOIN visits v ON b.visit_id = v.visit_id\nJOIN physicians ph ON v.physician_id = ph.physician_id\nWHERE v.visit_type = 'outpatient'\n  AND v.visit_date BETWEEN '2024-01-01' AND '2024-12-31'\nGROUP BY ph.physician_name\nORDER BY total_billed DESC\nLIMIT 5;",
  "evidence": "Outpatient visits are identified by visit_type = 'outpatient'. Total billed amount is the SUM of billing.amount for all line items. Physicians are linked through visits.physician_id.",
  "difficulty": "simple",
  "query_category": "aggregation/ranking",
  "tables_used": ["billing", "visits", "physicians"],
  "schema_context": {
    "billing": {
      "visit_id": "INTEGER FK → visits.visit_id",
      "amount": "DECIMAL(10,2) — billed amount in USD"
    },
    "visits": {
      "visit_id": "INTEGER PRIMARY KEY",
      "physician_id": "INTEGER FK → physicians.physician_id",
      "visit_type": "VARCHAR(20) — 'outpatient', 'inpatient', 'emergency'",
      "visit_date": "DATE"
    },
    "physicians": {
      "physician_id": "INTEGER PRIMARY KEY",
      "physician_name": "VARCHAR(100)"
    }
  },
  "expected_output": "[['Dr. Smith', 482000.50], ['Dr. Johnson', 395200.00], ['Dr. Patel', 371800.75], ['Dr. Chen', 358400.00], ['Dr. Williams', 342100.25]]"
}
```

*[... queries 4-30 follow the same structure ...]*
