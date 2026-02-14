# Database Documentation

## Overview

This project uses a **PostgreSQL** database hosted on **Supabase** to store real-time ADS-B (Automatic Dependent Surveillance-Broadcast) aircraft tracking data. A Raspberry Pi running dump1090 software receives ADS-B radio signals from aircraft transponders and a Python streamer writes the decoded data into the database. A Node.js web application then queries the database to visualize aircraft on a map and perform collision detection analytics.

All tables live in the `public` schema. The single receiver is identified as `labgpspi`.

---

## Data Flow

```
ADS-B Radio Signals (1090 MHz)
        │
        ▼
┌──────────────────┐
│  dump1090 (SDR)  │  Decodes transponder signals into SBS-1 text format
│  Raspberry Pi    │  Outputs on TCP port 30003
└────────┬─────────┘
         │
         ▼
┌────────────────────────────┐
│  adsb_streamer_optimized.py│  Parses SBS-1 messages, buffers in memory,
│  (Python)                  │  batch-inserts via PostgreSQL COPY command
└────────┬───────────────────┘
         │  PostgreSQL connection (Supabase, port 5432/6543)
         ▼
┌────────────────────────────┐
│  Supabase PostgreSQL       │  10 tables (see below)
│  (Cloud Database)          │
└────────┬───────────────────┘
         │  Queried by Node.js Express server
         ▼
┌────────────────────────────┐
│  Web Application           │  REST API → Leaflet 2D map / Cesium 3D globe
│  (Node.js + Express)       │
└────────────────────────────┘
```

---

## Table Relationships

The `hex` column (ICAO 24-bit aircraft identifier) is the primary join key across tables:

```
aircraft_real.hex ─────────┬──── aircraft_position_history.hex
       (current state)     │          (position trail log)
                           │
                           ├──── aircraft_sessions_real.hex
                           │          (flight session tracking)
                           │
                           ├──── collision_alerts.hex1 / hex2
                           │          (proximity alerts between pairs)
                           │
                           └──── risk_assessments.hex1 / hex2
                                      (risk scores between pairs)
```

---

## Active Tables (with data)

### 1. `aircraft_real` — Current Aircraft State

Stores the **most recent** position and metadata for each aircraft currently or recently tracked. Each row is upserted by `hex`; only the latest reading per aircraft is kept.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `hex` | varchar(6) | **PK** | — | ICAO 24-bit aircraft identifier (e.g. `A1B2C3`) |
| `flight` | varchar(10) | yes | — | Callsign / flight number (e.g. `UAL1225`) |
| `lat` | double precision | yes | — | Latitude in decimal degrees |
| `lon` | double precision | yes | — | Longitude in decimal degrees |
| `altitude` | integer | yes | — | Altitude in feet (barometric) |
| `speed` | integer | yes | — | Ground speed in knots |
| `track` | integer | yes | — | Heading in degrees (0–359) |
| `vertical_rate` | integer | yes | — | Climb/descent rate in ft/min |
| `squawk` | varchar(4) | yes | — | Transponder squawk code |
| `receiver_id` | varchar(255) | yes | — | ID of the ADS-B receiver that detected this aircraft |
| `seen_at` | timestamptz | yes | `now()` | Timestamp of most recent detection |
| `created_at` | timestamptz | yes | `now()` | Timestamp when this aircraft was first inserted |

**Indexes:** `(lat, lon)`, `(receiver_id)`, `(seen_at)`
**Row count:** ~107 (only currently/recently tracked aircraft)
**Data range:** Continuously updated; snapshot reflects most recent receiver session

---

### 2. `aircraft_position_history` — Position Trail Log

Append-only table recording every position update. Used for drawing flight trails on the map and as input to the Kalman filter for collision prediction.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | bigserial | **PK** | auto | Row identifier |
| `hex` | varchar(6) | no | — | Aircraft ICAO identifier |
| `lat` | double precision | no | — | Latitude |
| `lon` | double precision | no | — | Longitude |
| `altitude` | integer | no | — | Altitude in feet |
| `speed` | integer | yes | — | Ground speed in knots |
| `track` | integer | yes | — | Heading in degrees |
| `vertical_rate` | integer | yes | — | Climb/descent rate in ft/min |
| `timestamp` | timestamptz | no | — | Time of this position reading |
| `created_at` | timestamptz | yes | `now()` | When this row was inserted |

**Indexes:** `(hex, timestamp DESC)`, `(lat, lon)`, `(timestamp)`
**Row count:** ~14,054
**Data range:** 2026-01-16 22:42 UTC – 2026-01-17 00:43 UTC (~2 hours; older data is periodically cleaned up)

---

### 3. `aircraft_sessions_real` — Flight Sessions

Tracks when each aircraft was first and last detected by the receiver. A "session" begins when an aircraft first appears and the `last_seen` value is continuously updated. When the aircraft is no longer detected, `ended_at` is set.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `hex` | varchar(6) | **PK** | — | Aircraft ICAO identifier |
| `flight` | varchar(10) | yes | — | Callsign at time of detection |
| `receiver_id` | varchar(255) | yes | — | Primary receiver for this session |
| `first_seen` | timestamptz | no | — | When the aircraft was first detected |
| `last_seen` | timestamptz | no | — | Most recent detection timestamp |
| `ended_at` | timestamptz | yes | — | When the session ended (NULL if still active) |
| `created_at` | timestamptz | yes | `now()` | Row creation time |

**Indexes:** `(ended_at) WHERE ended_at IS NULL` (partial, active sessions only), `(first_seen, last_seen)`
**Row count:** ~16,725
**Data range:** 2025-12-12 – 2026-01-17 (over a month of session records)

---

### 4. `collision_alerts` — Proximity Violations

Records when two aircraft are detected within unsafe proximity thresholds. Each alert has a `detected_at` and is resolved (given a `resolved_at` timestamp) when the pair separates.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | bigserial | **PK** | auto | Alert identifier |
| `hex1` | varchar(6) | no | — | First aircraft ICAO hex |
| `hex2` | varchar(6) | no | — | Second aircraft ICAO hex |
| `flight1` | varchar(10) | yes | — | First aircraft callsign |
| `flight2` | varchar(10) | yes | — | Second aircraft callsign |
| `horizontal_distance_nm` | double precision | yes | — | Horizontal separation in nautical miles |
| `vertical_distance_ft` | integer | yes | — | Vertical separation in feet |
| `severity` | varchar(20) | yes | — | `critical`, `caution`, or `warning` |
| `detected_at` | timestamptz | yes | `now()` | When the alert was first detected |
| `resolved_at` | timestamptz | yes | — | When the alert was resolved (NULL if active) |

**Constraint:** `UNIQUE(hex1, hex2, resolved_at)`
**Indexes:** `(hex1, hex2, resolved_at) WHERE resolved_at IS NULL`, `(detected_at)`
**Row count:** ~7,570
**Severity distribution:** critical: 5,995 | caution: 919 | warning: 656
**Data range:** 2025-12-18 06:25 UTC – 2025-12-18 21:31 UTC

---

### 5. `risk_assessments` — Collision Risk Scores

Stores computed risk scores for aircraft pairs based on distance, closure rate, and time to closest point of approach (CPA). Generated by the Kalman filter collision detection system.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | bigserial | **PK** | auto | Row identifier |
| `hex1` | varchar(6) | no | — | First aircraft ICAO hex |
| `hex2` | varchar(6) | no | — | Second aircraft ICAO hex |
| `flight1` | varchar(10) | yes | — | First aircraft callsign |
| `flight2` | varchar(10) | yes | — | Second aircraft callsign |
| `risk_score` | double precision | no | — | Computed risk score (0–100, higher = more dangerous) |
| `horizontal_distance_nm` | double precision | yes | — | Horizontal distance in nautical miles |
| `vertical_distance_ft` | integer | yes | — | Vertical distance in feet |
| `closure_rate_knots` | double precision | yes | — | Rate at which aircraft are closing (positive = converging) |
| `time_to_cpa_seconds` | integer | yes | — | Estimated seconds until closest point of approach |
| `risk_level` | varchar(20) | yes | — | `low`, `medium`, `high`, or `critical` |
| `detected_at` | timestamptz | yes | `now()` | When this assessment was made |
| `resolved_at` | timestamptz | yes | — | When the risk was resolved (NULL if active) |

**Constraint:** `UNIQUE(hex1, hex2, resolved_at)`
**Indexes:** `(hex1, hex2, resolved_at) WHERE resolved_at IS NULL`, `(detected_at)`, `(risk_score DESC) WHERE resolved_at IS NULL`
**Row count:** ~1,235
**Risk level distribution:** high: 552 | medium: 283 | critical: 245 | low: 155
**Data range:** 2025-12-12 10:37 UTC – 2025-12-12 19:00 UTC

---

## Views

### `active_aircraft_real`

Returns aircraft from `aircraft_real` that have been seen within the last 5 minutes, along with a computed `seconds_since_seen` column.

```sql
SELECT a.*, EXTRACT(EPOCH FROM (NOW() - a.seen_at)) AS seconds_since_seen
FROM aircraft_real a
WHERE a.seen_at > NOW() - INTERVAL '5 minutes'
ORDER BY a.seen_at DESC;
```

### `active_sessions_real`

Returns flight sessions from `aircraft_sessions_real` that have not ended (`ended_at IS NULL`), along with a computed `session_duration_seconds` column.

```sql
SELECT s.*, EXTRACT(EPOCH FROM (s.last_seen - s.first_seen)) AS session_duration_seconds
FROM aircraft_sessions_real s
WHERE s.ended_at IS NULL
ORDER BY s.last_seen DESC;
```

---

## Functions

### `cleanup_old_data_real(history_hours, session_days)`

Removes stale data to keep the database lean. Called periodically.

- Deletes rows from `aircraft_history_real` older than `history_hours` (default: 2)
- Deletes ended sessions from `aircraft_sessions_real` older than `session_days` (default: 7)
- Returns count of deleted rows from each table

---

## How to Restore the Dump

The file `database_dump.sql` contains the full schema (CREATE TABLE, indexes, constraints) and all data (as INSERT statements) for every table listed above.

To restore into a fresh PostgreSQL database:

```bash
createdb adsb_tracking
psql adsb_tracking < database_dump.sql
```

Or to restore into an existing database (will drop and recreate tables):

```bash
psql -d your_database -f database_dump.sql
```

---

## Data Summary

| Table | Rows | Date Range |
|---|---|---|
| `aircraft_real` | 107 | Snapshot (last active session) |
| `aircraft_position_history` | 14,054 | 2026-01-16 – 2026-01-17 (~2 hrs) |
| `aircraft_sessions_real` | 16,725 | 2025-12-12 – 2026-01-17 (~5 weeks) |
| `collision_alerts` | 7,570 | 2025-12-18 (~15 hrs) |
| `risk_assessments` | 1,235 | 2025-12-12 (~8 hrs) |
