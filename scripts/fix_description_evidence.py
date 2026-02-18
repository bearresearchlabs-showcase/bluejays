#!/usr/bin/env python3
"""
Fix description vs evidence in queries.json: description = context, evidence = justification.
Description: domain, purpose, what the query accomplishes conceptually.
Evidence: how the query implements it, technical approach (CTEs, window functions, etc.).
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
try:
    from db_paths import SOURCE, get_queries_dir
except ImportError:
    SOURCE = BASE / "source"

    def get_queries_dir(db_dir: Path) -> Path:
        if (db_dir / "QUERIES").exists():
            return db_dir / "QUERIES"
        app = db_dir / "app"
        if app.exists() and (app / "QUERIES").exists():
            return app / "QUERIES"
        return db_dir / "queries"

# Primary: "The query" is the clearest boundary for technical content
# Secondary: "Produce/Generate/Conduct/Perform" at sentence start (after ". ")
EVIDENCE_STARTERS_PRIMARY = [
    r"\.\s+The query\b",
    r"\.\s+Produce\b",
    r"\.\s+Generate\b",
    r"\.\s+Conduct\b",
    r"\.\s+Perform\b",
    r"\.\s+Analyze\b",
    r"\.\s+Create\b",
    r"\.\s+Display\b",
]
# Fallback: "The query" anywhere
EVIDENCE_STARTERS_FALLBACK = [r"\bThe query\b"]


def _split_description_evidence(desc: str, ev: str) -> tuple[str, str]:
    """
    Heuristic split: description = context only, evidence = technical justification.
    Returns (new_description, new_evidence).
    """
    text = ev if len(ev) >= len(desc) else desc
    if not text or not text.strip():
        return (desc or "", ev or "")

    evidence_start = -1
    for pattern in EVIDENCE_STARTERS_PRIMARY + EVIDENCE_STARTERS_FALLBACK:
        m = re.search(pattern, text, re.IGNORECASE)
        if not m:
            continue
        # For "\.\s+X" patterns, evidence starts after ". " (skip period + whitespace)
        if pattern.startswith(r"\."):
            start = m.start() + 1
            while start < len(text) and text[start] in " \t\n":
                start += 1
        else:
            start = m.start()
        if evidence_start < 0 or start < evidence_start:
            evidence_start = start

    if evidence_start >= 0:
        context = text[:evidence_start].strip()
        technical = text[evidence_start:].strip()
        # Trim context to last complete sentence
        for sep in [". ", ".\n"]:
            idx = context.rfind(sep)
            if idx > 30:
                context = context[: idx + 1].strip()
                break
        if technical and len(technical) > 40 and len(context) > 30:
            return (context, technical)

    # Fallback: first 2 sentences = context, rest = evidence
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) >= 3:
        context = " ".join(sentences[:2]).strip()
        technical = " ".join(sentences[2:]).strip()
        if technical and len(technical) > 40:
            return (context, technical)

    return (desc or "", ev or "")


def fix_db_heuristic(path: Path) -> bool:
    """Apply heuristic split to all queries with description and evidence."""
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        desc = q.get("description") or ""
        ev = q.get("evidence") or ""
        if not desc and not ev:
            continue
        new_desc, new_ev = _split_description_evidence(desc, ev)
        if new_desc != desc or new_ev != ev:
            q["description"] = new_desc
            q["evidence"] = new_ev
            changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-1: Already fixed with manual mappings (skip heuristic)
DB1_DESCRIPTIONS = {
    1: "Fleet operators monitor ADS-B telemetry to track aircraft altitude over time for anomaly detection and maintenance planning. Each aircraft has a unique ICAO 24-bit transponder hex code; altitude is in feet. Daily summaries help detect sensor drift, flight envelope excursions, or operational issues.",
    2: "Flight analysts compare altitude behavior across groundspeed ranges (knots) to see if cruise vs climb/descent phases show different patterns. This supports flight profile optimization and speed-related anomaly detection.",
    3: "Fleet managers produce monthly reports to track long-term altitude trends per aircraft and identify seasonal patterns. Monthly aggregation smooths daily noise and reveals gradual shifts in flight behavior.",
    4: "Operations teams want to know whether certain speed regimes (cruise vs climb/descent) exhibit more altitude anomalies or different trend behaviors. Daily breakdowns by speed help pinpoint sensor issues or airspace constraints.",
    5: "Fleet analysts compare altitude variability and trend direction across aircraft weekly to identify units needing attention. Standard deviation indicates stability; combining it with trend counts helps prioritize investigations.",
    6: "Flight operations analysts monitor daily altitude patterns across speed regimes to identify instrumentation issues, unusual weather, or non-standard flight profiles. Speed buckets isolate climb, cruise, and descent behavior.",
    7: "Fleet managers need monthly altitude summaries per aircraft to compare operational profiles, assess fleet consistency, and identify aircraft with unusual distributions or high cumulative activity requiring maintenance review.",
    8: "Safety analysts detect rapid altitude changes between consecutive readings per aircraft. Sudden climbs or descents may indicate turbulence, emergency maneuvers, or data quality issues. Time gaps between readings assess data continuity.",
    9: "Quality assurance teams monitor altitude within specific speed regimes to detect anomalies (e.g., unexpected altitude holds at high speed, erratic changes during approach). Statistical outliers help flag data for manual review.",
    10: "Maintenance planners prioritize aircraft inspections using recency (how recently active) and frequency (how often in data) as key indicators. Aircraft that are both frequently active and recently observed may need earlier scheduling.",
    11: "Aviation analysts need to understand how altitude behavior varies across speed regimes over time, similar to cohort analysis. This identifies performance patterns and anomalies in flight operations.",
    12: "Flight safety analysts detect sudden altitude changes that may indicate emergency maneuvers, equipment issues, or unusual flight patterns. Tracking both altitude changes (first derivative) and their acceleration (second derivative) helps identify critical events.",
    13: "Aviation operations teams benchmark altitude patterns across speed regimes (cruise, climb, descent) to see if aircraft maintain appropriate altitude profiles. Cross-category comparison identifies operational inefficiencies or safety concerns.",
    14: "Aircraft maintenance and flight operations analysts identify underlying altitude trends by filtering short-term noise. Raw readings can be erratic due to weather, ATC, and normal operations; smoothing techniques enable trend detection.",
    15: "Air traffic management and capacity planning teams identify when aircraft in different speed categories reach peak altitudes each day. Peak period understanding helps optimize airspace utilization and predict congestion.",
    16: "Maintenance planning prioritizes aircraft for scheduled inspections based on total flight activity over time. LTV-style metrics rank aircraft by cumulative altitude exposure to allocate maintenance resources.",
    17: "Fleet operations need to correlate altitude with temporal patterns (hour of day, day of week) to identify time-of-day effects. This supports shift planning and operational scheduling.",
    18: "Operations analysts segment altitude behavior by speed and time period to identify regime-specific patterns. Comparing climb vs cruise vs descent phases helps optimize flight profiles.",
    19: "Maintenance teams track altitude volatility (standard deviation) and trend consistency across aircraft. High volatility may indicate equipment issues or unusual flight profiles.",
    20: "Fleet managers compare altitude distributions across aircraft and speed categories to identify outliers. Percentile-based benchmarking supports fleet-wide consistency assessment.",
    21: "Operations teams need rolling-window altitude metrics to smooth noise and reveal trends. Moving averages and cumulative sums help assess operational patterns over time.",
    22: "Flight analysts segment altitude by speed bucket and time period to identify regime-specific anomalies. Speed-temporal segmentation supports targeted investigations.",
    23: "Maintenance planners use altitude quartiles and distribution shape to assess aircraft behavior. Quartile analysis reveals central tendency and spread without assuming normality.",
    24: "Operations teams correlate altitude with temporal features (hour, day of week) to detect time-of-day patterns. This supports shift-based operational planning.",
    25: "Fleet analysts need cross-aircraft and cross-speed altitude comparisons. Percentile rankings and distribution metrics enable fleet-wide benchmarking.",
    26: "Safety analysts track altitude change rates (first derivative) and acceleration (second derivative) to detect critical events. Rate-of-change metrics support early warning systems.",
    27: "Operations teams segment altitude by speed and aggregate by time period to identify regime-specific trends. Speed-temporal aggregation supports operational optimization.",
    28: "Maintenance planners use cumulative altitude exposure and activity metrics to prioritize inspections. LTV-style and recency-frequency metrics support resource allocation.",
    29: "Fleet managers need altitude distribution metrics (quartiles, percentiles) across aircraft and speed categories. Distribution analysis supports consistency and outlier detection.",
    30: "Operations analysts correlate altitude with temporal and speed dimensions to identify multi-dimensional patterns. Cross-dimensional analysis supports comprehensive operational insights.",
}

DB1_EVIDENCE = {
    1: "The query constructs four CTEs. First, it retains the 60 most recent telemetry points per aircraft (cte_level_1). Second, it computes a 5-row rolling average and cumulative sum via window functions (cte_level_2). Third, it uses LAG, LEAD, and partition statistics for trend and z-score calculation (cte_level_3). Fourth, it flags outliers (z-score > 2) and trend direction, then aggregates by day and hex with PERCENTILE_CONT, SUM for outlier/increasing counts, and AVG for rolling average.",
    2: "The query groups telemetry by week and speed bucket. It divides altitude into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (>2 std dev), and uses LAG/LEAD to compare consecutive readings for trend direction. Aggregates include quartiles (PERCENTILE_CONT), outlier count, and increasing-trend count.",
    3: "The query groups by month and aircraft hex. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score; and aggregates record count, stddev, min, max, outlier count, and increasing count. ROW_NUMBER limits to 80 points per aircraft.",
    4: "The query groups by date and speed. It calculates running cumulative sum of altitude changes, applies a 7-row rolling window, uses NTILE(8) for distribution, and aggregates outlier count, increasing-trend count, and max cumulative sum per group.",
    5: "The query groups by week and hex. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. Aggregates include record count, quartiles, stddev, outlier count, and increasing count. ROW_NUMBER limits to 100 points per aircraft.",
    6: "The query groups by day and speed bucket. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a 5-row rolling average, and filters to groups with ≥2 records. Output includes quartiles, rolling average, and outlier count.",
    7: "The query groups by month and hex. It captures min/max altitude, flags outliers (z-score > 2), limits to 80 points per aircraft, uses PERCENT_RANK, and calculates cumulative sum via window. Aggregates include quartiles, min, max, outlier count, and max cumulative sum.",
    8: "The query groups by day and hex. It uses LAG to get previous altitude, computes delta (current minus previous), derives trend_direction from the sign, and uses LEAD for next value. Aggregates include quartiles and sequential difference metrics.",
    9: "The query groups by day and speed bucket. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into octiles (NTILE(8)), and aggregates quartiles, outlier count, and trend direction counts.",
    10: "The query groups by week and hex. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and filters to groups with ≥3 records. Output includes quartiles and rolling average.",
    11: "The query treats each speed range as a cohort. It limits to 90 points per speed bucket, uses window functions for increasing_count and trend_direction (analogous to retention), and orders by time period and average value. Output includes cohort-style progression and quartile boundaries.",
    12: "The query uses LAG to create first derivative (altitude change). trend_direction captures sign of change. LAG and LEAD together enable second-order derivative (rate of change of rate). Z-scores flag outliers. Limited to 60 points per aircraft. Output includes change rate metrics, quartiles, and outlier count.",
    13: "The query employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into sextiles. Speed categories ranked by cumulative altitude sum. Partition-level avg/stddev enable z-scores. Output includes percentile rankings and quartile distributions.",
    14: "The query implements a 6-row rolling window for simple moving average (avg_rolling). It counts periods where altitude is increasing and flags statistical outliers. Limited to 80 points per aircraft, minimum 1 record per group. Output includes quartiles and trend pattern counts.",
    15: "The query ranks altitude within each day using window functions to identify peaks per speed category. Extracts hour and day-of-week for temporal analysis. Calculates max_cumulative and avg_rolling as efficiency proxies. Output includes peak period identification and quartile distributions.",
    16: "The query computes cumulative_sum as total exposure proxy, tracks max_cumulative for lifetime activity, ranks aircraft by cumulative sum, applies PERCENT_RANK for quartile placement. Limited to 60 points per aircraft, ≥3 records per group. Output includes LTV metrics, quartiles, and cumulative totals.",
    17: "The query extracts hour_val and dow_val for temporal context. It uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by period and hex. Output includes temporal correlation metrics.",
    18: "The query segments by speed and time period. It uses PARTITION BY speed for window functions, groups by week and speed, and produces regime-specific aggregates including quartiles and trend counts.",
    19: "The query calculates STDDEV per partition as volatility measure. It uses PERCENTILE_CONT for quartiles and trend_direction for consistency. Aggregates include stddev, quartiles, outlier count, and increasing count.",
    20: "The query uses PERCENT_RANK and PERCENTILE_CONT for cross-aircraft and cross-speed distribution comparison. DENSE_RANK and NTILE support benchmarking. Output includes percentile rankings and quartile distributions.",
    21: "The query implements rolling windows (ROWS BETWEEN N PRECEDING AND CURRENT ROW) for moving average and cumulative sum. Window functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE) support trend analysis. Output includes rolling and cumulative metrics.",
    22: "The query partitions by speed and groups by day and speed. It combines temporal (DATE_TRUNC) and speed dimensions. Output includes speed-temporal segmented aggregates.",
    23: "The query uses PERCENTILE_CONT(0.25), (0.5), (0.75) for quartiles. NTILE provides distribution bins. Output includes q1, median, q3, and distribution shape metrics.",
    24: "The query extracts EXTRACT(HOUR) and EXTRACT(DOW) for temporal features. It correlates these with altitude via partition and grouping. Output includes time-of-day correlation metrics.",
    25: "The query uses PERCENT_RANK across partitions for cross-aircraft and cross-speed comparison. PERCENTILE_CONT and NTILE support distribution analysis. Output includes percentile rankings and quartile breakdowns.",
    26: "The query computes delta_value (current minus LAG) as first derivative. trend_direction (Increasing/Decreasing/Stable) captures sign. LAG+LEAD enable second derivative. Z-scores flag outliers. Output includes rate-of-change and acceleration-like metrics.",
    27: "The query groups by week and speed. It aggregates altitude metrics per speed-temporal cell. Output includes regime-specific trend aggregates.",
    28: "The query computes cumulative_sum and max_cumulative. ROW_NUMBER (desc) scores recency. Record count proxies frequency. Output includes LTV-style and recency-frequency metrics.",
    29: "The query uses PERCENTILE_CONT and PERCENT_RANK for distribution metrics. Groups by month and hex or speed. Output includes quartiles and percentile distributions across dimensions.",
    30: "The query correlates altitude with period (day/week/month), hex, and speed. Multi-dimensional grouping and window functions (PARTITION BY hex, speed) produce cross-dimensional aggregates.",
}


# db-3: Order management / e-commerce (orders_order: seller_id, total_amount, status)
DB3_DESCRIPTIONS = {
    1: "Order managers monitor how seller total amounts fluctuate over time to identify unusual patterns and flag potential issues. Daily summaries help detect anomalies, pricing errors, or operational problems.",
    2: "Business analysts compare total_amount distribution patterns across order status buckets (pending, shipped, delivered, etc.) to understand how orders behave at different processing stages.",
    3: "Operations managers produce monthly reports to track long-term total_amount trends per seller and identify seasonal patterns for inventory planning and demand forecasting.",
    4: "Warehouse and fulfillment teams use daily dashboards segmented by order status to identify whether certain processing stages exhibit more anomalies or different trend behaviors.",
    5: "Account managers compare variability (standard deviation) and trend momentum across sellers weekly to prioritize follow-up and relationship management activities.",
    6: "Operations teams monitor order processing across status categories and need to identify anomalies in daily order values within specific status buckets for quality control.",
    7: "Business intelligence teams perform monthly seller performance reviews and need to compare order value distributions across the seller network for commission calculations and tier classifications.",
    8: "Financial analysts track how individual seller order volumes change day-over-day to detect sudden spikes or drops that may indicate market opportunities, operational problems, or fraud.",
    9: "Quality assurance teams monitor order processing patterns across status categories to identify unusual total_amount behaviors that might signal system errors, pricing mistakes, or fraud.",
    10: "Seller management teams use recency-frequency-monetary (RFM) style analysis to prioritize which sellers require attention for relationship management, support allocation, or compliance review.",
    11: "Business analysts need to understand how different order status categories (delivered, cancelled, in-transit) behave over time in terms of total order amounts, similar to cohort analysis.",
    12: "Operations teams detect sudden accelerations or decelerations in a seller's daily order total amounts that can signal operational issues, fraud, or market opportunities requiring immediate attention.",
    13: "Operations teams benchmark total order amounts across order statuses (completed, pending, cancelled) to identify performance outliers and relative performance.",
    14: "Monthly order total amounts for individual sellers often contain noise from seasonal variations or data irregularities that obscure underlying trends; smoothing reveals patterns.",
    15: "Capacity planning and resource allocation teams identify when order total amounts reach peak levels within each status category for staffing and infrastructure scaling decisions.",
    16: "Business teams prioritize sellers based on total transaction activity over time to optimize maintenance scheduling and resource allocation.",
    17: "Business analysts need to understand how order volume patterns evolve across order statuses (delivered, cancelled, processing) from one year to the next.",
    18: "Operations teams require visual representation of total_amount patterns across time and sellers for fleet-wide operational insights via heatmap visualization.",
    19: "Business analysts need to understand how order amounts distribute within each order status category over time; running percentiles reveal consistency and variability.",
    20: "Business analysts need to understand how current order amounts relate to previous periods across the seller base; cross-correlation reveals consistent behavior, seasonal cycles, or trend shifts.",
    21: "Finance teams perform forensic analysis on how order total amounts transition between trend states (Increasing, Decreasing, Stable) over time to identify unusual patterns.",
    22: "Operations dashboards require a unified data source that consolidates all key performance metrics for monitoring seller activity across the entire fleet.",
    23: "Analytics teams need to understand how order total amounts evolve sequentially over time within each order status category for forecasting models.",
    24: "Management assesses market concentration and identifies whether order activity is concentrated among a few top sellers or distributed evenly for resource allocation and risk management.",
    25: "Quality assurance teams need a prioritization system to identify which order status categories exhibit unusual total amount patterns warranting immediate investigation.",
    26: "Finance teams compare seller performance across fiscal periods (month-over-month, quarter-over-quarter) for budgeting and planning cycles.",
    27: "Operations teams monitor order throughput and capacity utilization across status categories (pending, processing, shipped, delivered) to optimize workflow and identify bottlenecks.",
    28: "Sales leadership tracks how each seller's total order value accumulates over time to identify growth trajectories, seasonal patterns, and top performers for incentive programs.",
    29: "Business analysts require flexible data structures that support dynamic pivoting and slicing across time periods and order statuses for ad-hoc reporting and executive dashboards.",
    30: "Data quality teams need robust outlier detection methods; IQR-based approaches complement z-scores for skewed distributions where quartile spreads provide more reliable anomaly flagging.",
}

DB3_EVIDENCE = {
    1: "The query constructs four CTEs. First, it retains the 60 most recent order records per seller (cte_level_1). Second, it computes a 5-row rolling average and cumulative sum via window functions (cte_level_2). Third, it uses LAG, LEAD, and partition statistics for trend and z-score calculation (cte_level_3). Fourth, it flags outliers (z-score > 2) and trend direction, then aggregates by day and seller_id with PERCENTILE_CONT, SUM for outlier/increasing counts, and AVG for rolling average.",
    2: "The query groups orders by week and status. It divides total_amount into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (>2 std dev), and uses LAG/LEAD to compare consecutive readings for trend direction. Aggregates include quartiles (PERCENTILE_CONT), outlier count, and increasing-trend count.",
    3: "The query groups by month and seller_id. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score; and aggregates record count, stddev, min, max, outlier count, and increasing count. ROW_NUMBER limits to 80 records per seller.",
    4: "The query groups by day and status. It calculates running cumulative sum of total_amount, applies a 7-row rolling window, uses NTILE(8) for distribution, and aggregates outlier count, increasing-trend count, and max cumulative sum per group.",
    5: "The query groups by week and seller_id. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. Aggregates include record count, quartiles, stddev, outlier count, and increasing count. ROW_NUMBER limits to 100 records per seller.",
    6: "The query groups by day and status. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a 5-row rolling average, and filters to groups with ≥2 records. Output includes quartiles, rolling average, and outlier count.",
    7: "The query groups by month and seller_id. It captures min/max total_amount, flags outliers (z-score > 2), limits to 80 records per seller, uses PERCENT_RANK, and calculates cumulative sum via window. Aggregates include quartiles, min, max, outlier count, and max cumulative sum.",
    8: "The query groups by day and seller_id. It uses LAG to get previous total_amount, computes delta (current minus previous), derives trend_direction from the sign, and uses LEAD for next value. Aggregates include quartiles and sequential difference metrics.",
    9: "The query groups by day and status. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into octiles (NTILE(8)), and aggregates quartiles, outlier count, and trend direction counts.",
    10: "The query groups by week and seller_id. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and filters to groups with ≥3 records. Output includes quartiles and rolling average.",
    11: "The query treats each order status as a cohort. It limits to 90 records per status, uses window functions for increasing_count and trend_direction (analogous to retention), and orders by time period and average value. Output includes cohort-style progression and quartile boundaries.",
    12: "The query uses LAG to create first derivative (total_amount change). trend_direction captures sign of change. LAG and LEAD together enable second-order derivative (acceleration). Z-scores flag outliers. Output includes change rate metrics, quartiles, and outlier count.",
    13: "The query employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into sextiles. Status categories ranked by cumulative total_amount sum. Partition-level avg/stddev enable z-scores. Output includes percentile rankings and quartile distributions.",
    14: "The query implements a 6-row rolling window for simple moving average (avg_rolling). It counts periods where total_amount is increasing and flags statistical outliers. Limited to 80 records per seller, minimum 1 record per group. Output includes quartiles and trend pattern counts.",
    15: "The query ranks total_amount within each day using window functions to identify peaks per status category. Extracts hour and day-of-week for temporal analysis. Calculates max_cumulative and avg_rolling as efficiency proxies. Output includes peak period identification and quartile distributions.",
    16: "The query computes cumulative_sum as total activity proxy, tracks max_cumulative for lifetime value, ranks sellers by cumulative sum, applies PERCENT_RANK for quartile placement. Limited to 60 records per seller, ≥3 records per group. Output includes LTV metrics, quartiles, and cumulative totals.",
    17: "The query extracts hour_val and dow_val for temporal context. It uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by period and status. Output includes temporal correlation and YoY-style growth metrics.",
    18: "The query uses time period and seller_id as heatmap dimensions. It computes avg_value and record_count as intensity metrics, extracts hour and day-of-week, and flags outliers via z-scores. Output includes quartiles and outlier count.",
    19: "The query applies PERCENT_RANK for running percentile position and PERCENTILE_CONT for quartile breakpoints. Limited to 70 records per status. Counts increasing trends and outliers. Output includes running percentiles, quartiles, and trend pattern counts.",
    20: "The query uses LAG and LEAD to access preceding and following period values for each seller. It calculates delta_value and trend_direction. Partition_avg and partition_stddev enable z-score normalization. Output includes sequential correlation metrics and quartiles.",
    21: "The query treats trend_direction (Increasing, Decreasing, Stable) as status categories. It uses LAG and LEAD for sequential status change tracing, calculates z-scores, computes quartiles per group, and filters to ≥2 records. Output includes status transition sequences and quartile boundaries.",
    22: "The query performs single-pass aggregation: record_count, avg_value, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, max_cumulative. Filters to ≥3 records per seller-week. Output includes full dashboard suite of statistics.",
    23: "The query employs LAG and LEAD for previous/next period values, calculates delta_value and trend_direction, uses ROWS BETWEEN window frames, applies ROW_NUMBER for ordering, limits to 90 records per status. Output includes sequential pattern indicators and quartiles.",
    24: "The query uses DENSE_RANK for seller ranking, PERCENT_RANK for relative position, cumulative_sum for concentration measurement, NTILE(5) for quintiles, z-scores for outliers. Output includes concentration indices, quartiles, and outlier count.",
    25: "The query calculates z_score as anomaly metric, aggregates outlier_count, computes partition_avg and partition_stddev, counts trend_direction records, limits to 70 records per status. Output includes anomaly scores, quartiles, and trend counts.",
    26: "The query groups by seller and month using DATE_TRUNC('month'). It calculates quartiles (PERCENTILE_CONT), average, and standard deviation. Limits to 80 records per seller. Output includes quartile breakdowns for fiscal period comparison.",
    27: "The query groups by status and day. It calculates record_count (volume), avg_rolling (7-row moving average), max_cumulative (peak capacity). Limits to 90 records per status, ≥2 records per group. Output includes throughput indicators, quartiles, and rolling averages.",
    28: "The query computes cumulative_sum and max_cumulative. It derives trend_direction and increasing_count. Ranks sellers by cumulative sum. Filters to ≥3 records per group. Output includes cumulative trend indicators, quartiles, and seller rankings.",
    29: "The query uses time period (month) and order status as grouping dimensions. It aggregates record count, average, quartiles, stddev, min, max, outlier_count, trend indicators. Requires ≥1 record per group. Output includes multi-dimensional aggregate metrics and quartiles.",
    30: "The query groups by status and week. It calculates quartiles via PERCENTILE_CONT for Q1 and Q3 (IQR support), flags outliers (z-score > 2), includes stddev_value for IQR-based boundaries, computes trend counts. Output includes IQR-style outlier detection, quartiles, and trend metrics.",
}

# db-4: SharedAI models (id, name, user_id, created_at)
DB4_DESCRIPTIONS = {
    1: "Platform operators monitor SharedAI model creation patterns over time to identify anomalies and usage trends. Each model has an id, name, and user_id; created_at tracks when models are added. Daily summaries help detect unusual creation patterns, potential abuse, or platform growth.",
    2: "Analytics teams compare model ID distribution across user buckets to understand how different user segments create models. User_id segmentation reveals adoption patterns and power-user behavior.",
    3: "Product managers produce monthly reports to track long-term model creation trends per model name and identify seasonal or growth patterns. Monthly aggregation smooths daily noise and reveals gradual shifts.",
    4: "Operations teams want to know whether certain user segments exhibit more model creation anomalies or different trend behaviors. Daily breakdowns by user help pinpoint usage spikes or data quality issues.",
    5: "Platform analysts compare model ID variability and trend direction across model names weekly to identify which models or categories need attention. Standard deviation indicates consistency; trend counts help prioritize investigations.",
    6: "Operations teams monitor daily model creation patterns across user buckets to identify anomalies that may indicate instrumentation issues, abuse, or non-standard usage. User buckets isolate behavior by segment.",
    7: "Product managers need monthly summaries of model creation per model name to compare adoption profiles, assess platform consistency, and identify models with unusual distributions or high cumulative activity.",
    8: "Platform analysts detect rapid changes in model ID sequences between consecutive creations per user. Sudden jumps may indicate bulk imports, data quality issues, or unusual usage patterns.",
    9: "Quality assurance teams monitor model creation within specific user buckets to detect anomalies such as unexpected creation bursts or erratic patterns. Statistical outliers help flag data for manual review.",
    10: "Platform planners prioritize user support using recency (how recently active) and frequency (how often they create models) as key indicators. Users that are both frequently active and recently observed may need earlier engagement.",
    11: "Analytics teams need to understand how model creation behavior varies across user cohorts over time, similar to retention analysis. This identifies engagement patterns and power-user segments.",
    12: "Platform engineers detect sudden changes in model creation rates that may indicate system issues, abuse, or unusual usage. Tracking both change (first derivative) and acceleration (second derivative) helps identify critical events.",
    13: "Operations teams benchmark model creation patterns across user segments to see if usage is consistent. Cross-category comparison identifies adoption gaps or power-user concentration.",
    14: "Product analysts identify underlying model creation trends by filtering short-term noise. Raw data can be erratic due to campaigns, launches, or normal variance; smoothing techniques enable trend detection.",
    15: "Capacity planning teams identify when model creation reaches peak levels within each user segment each day. Peak period understanding helps optimize infrastructure and predict load.",
    16: "Platform planning prioritizes model names or users based on total creation activity over time. LTV-style metrics rank by cumulative model creation to allocate support and resources.",
    17: "Product analysts need to correlate model creation with temporal patterns (hour of day, day of week) to identify time-of-day effects. This supports capacity planning and operational scheduling.",
    18: "Operations teams segment model creation by user and time period to identify segment-specific patterns. Comparing user buckets helps optimize platform engagement.",
    19: "Platform teams track model creation volatility (standard deviation) and trend consistency across users. High volatility may indicate power users or unusual usage profiles.",
    20: "Product managers compare model creation distributions across model names and user categories to identify outliers. Percentile-based benchmarking supports platform-wide consistency assessment.",
    21: "Analytics teams trace how model creation transitions between behavioral states (Increasing, Decreasing, Stable) over time within each user to identify suspicious patterns and investigate anomalies.",
    22: "Operations dashboards require a consolidated data feed that provides all essential monitoring metrics in a single query to track platform-wide model creation without multiple database calls.",
    23: "Analysts need to understand how model creation values evolve chronologically within each user's activity stream to identify behavioral patterns, trends, and sequential dependencies over monthly periods.",
    24: "Product managers assess market concentration by understanding what proportion of total model activity is dominated by top-performing models versus distributed across the portfolio.",
    25: "Data science teams require prioritized anomaly scores to efficiently allocate investigation resources by identifying which user accounts exhibit the most unusual model creation patterns.",
    26: "Finance teams require month-over-month and quarter-over-quarter comparative analysis of model creation to support fiscal period reporting and strategic planning activities.",
    27: "Operations teams assess daily model creation activity levels across different users to optimize system capacity and resource allocation for throughput planning.",
    28: "Product managers need to understand how total model creation activity accumulates over time for each model name to identify growth patterns and prioritize development efforts.",
    29: "Business analysts require flexible, multi-dimensional views of model creation by time period and user to support ad-hoc analysis, custom reporting, and pivot table generation.",
    30: "Data quality engineers need to identify anomalous user activity patterns using quartile-based outlier detection methods (IQR approach) to complement existing z-score analysis.",
}

DB4_EVIDENCE = {
    1: "The query constructs four CTEs. First, it retains the 60 most recent records per model name (cte_level_1). Second, it computes a 5-row rolling average and cumulative sum via window functions on id (cte_level_2). Third, it uses LAG, LEAD, and partition statistics for trend and z-score calculation (cte_level_3). Fourth, it flags outliers (z-score > 2) and trend direction, then aggregates by day and name with PERCENTILE_CONT, SUM for outlier/increasing counts, and AVG for rolling average.",
    2: "The query groups by week and user_id. It divides id into sextiles (NTILE(6)), calculates z-scores per partition, flags outliers (>2 std dev), and uses LAG/LEAD to compare consecutive values for trend direction. Aggregates include quartiles (PERCENTILE_CONT), outlier count, and increasing-trend count.",
    3: "The query groups by month and name. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 6-row rolling average; flags outliers via z-score; and aggregates record count, stddev, min, max, outlier count, and increasing count. ROW_NUMBER limits to 80 points per model name.",
    4: "The query groups by day and user_id. It calculates running cumulative sum of id, applies a 7-row rolling window, uses NTILE(8) for distribution, and aggregates outlier count, increasing-trend count, and max cumulative sum per group.",
    5: "The query groups by week and name. It calculates STDDEV, PERCENTILE_CONT for quartiles, and uses LAG/LEAD with delta_value to derive trend_direction. Aggregates include record count, quartiles, stddev, outlier count, and increasing count. ROW_NUMBER limits to 100 points per model.",
    6: "The query groups by day and user_id. It computes z-scores (mean, stddev per partition; zero when stddev=0), flags outliers, calculates a rolling average, and filters to groups with ≥1 record. Output includes quartiles, rolling average, and outlier count.",
    7: "The query groups by month and name. It captures min/max id, flags outliers (z-score > 2), limits to 120 points per model, uses PERCENT_RANK, and calculates cumulative sum via window. Aggregates include quartiles, min, max, outlier count, and max cumulative sum.",
    8: "The query groups by day and user_id. It uses LAG to get previous id, computes delta (current minus previous), derives trend_direction from the sign, and uses LEAD for next value. Aggregates include quartiles and sequential difference metrics.",
    9: "The query groups by week and name. It computes mean and stddev per group, flags anomalies (|z| > 2), handles stddev=0 safely, segments into septiles (NTILE(7)), and aggregates quartiles, outlier count, and trend direction counts.",
    10: "The query groups by month and user_id. It assigns ROW_NUMBER (desc timestamp) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and filters to groups with ≥2 records. Output includes quartiles and rolling average.",
    11: "The query treats each model name as a cohort dimension. It limits to 160 points per name, uses window functions for increasing_count and trend_direction (analogous to retention), and orders by time period and average value. Output includes cohort-style progression and quartile boundaries.",
    12: "The query groups by week and user_id. It uses LAG to create first derivative (id change). trend_direction captures sign of change. LAG and LEAD together enable second-order derivative. Z-scores flag outliers. Output includes change rate metrics, quartiles, and outlier count.",
    13: "The query groups by month and name. It employs PERCENT_RANK for cross-category benchmarking and PERCENTILE_CONT for percentile values. Data segmented into quintiles (NTILE(5)). Partition-level avg/stddev enable z-scores. Output includes percentile rankings and quartile distributions.",
    14: "The query groups by day and user_id. It implements a 3-row rolling window for simple moving average (avg_rolling). It counts periods where id is increasing and flags statistical outliers. Limited to 190 points per user. Output includes quartiles and trend pattern counts.",
    15: "The query groups by week and name. It ranks id within each day using window functions to identify peaks per user category. Extracts hour and day-of-week for temporal analysis. Calculates max_cumulative and avg_rolling. Output includes peak period identification and quartile distributions.",
    16: "The query groups by month and user_id. It computes cumulative_sum as total activity proxy, tracks max_cumulative for lifetime value, ranks users by cumulative sum, applies PERCENT_RANK. Limited to 210 points per user, ≥2 records per group. Output includes LTV metrics, quartiles, and cumulative totals.",
    17: "The query groups by day and name. It extracts hour_val and dow_val for temporal context. Uses window functions (rolling avg, cumulative sum, LAG, LEAD) and aggregates by period and name. Output includes temporal correlation metrics.",
    18: "The query groups by week and user_id. It uses period and user_id as dimensions. Computes avg_value and record_count, extracts hour and day-of-week, flags outliers via z-scores. Output includes quartiles and outlier count.",
    19: "The query groups by month and name. It applies PERCENT_RANK for running percentile position and PERCENTILE_CONT for quartile breakpoints. Limited to 240 points per model. Counts increasing trends and outliers. Output includes running percentiles, quartiles, and trend pattern counts.",
    20: "The query groups by day and user_id. It uses LAG and LEAD to access preceding and following period values. Calculates delta_value and trend_direction. Partition_avg and partition_stddev enable z-score normalization. Output includes sequential correlation metrics and quartiles.",
    21: "The query groups by week and name. It treats trend_direction (Increasing, Decreasing, Stable) as status categories. Uses LAG and LEAD for sequential status change tracing, calculates z-scores, computes quartiles per group. Output includes status transition sequences and quartile boundaries.",
    22: "The query groups by month and user_id. It performs single-pass aggregation: record_count, avg_value, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, max_cumulative. Filters to ≥2 records per user-month. Output includes full dashboard suite of statistics.",
    23: "The query groups by day and name. It employs LAG and LEAD for previous/next period values, calculates delta_value and trend_direction, uses ROWS BETWEEN window frames, applies ROW_NUMBER for ordering, limits to 280 points per model. Output includes sequential pattern indicators and quartiles.",
    24: "The query groups by week and user_id. It uses DENSE_RANK for ranking, PERCENT_RANK for relative position, cumulative_sum for concentration measurement, NTILE(4) for quartiles, z-scores for outliers. Output includes concentration indices, quartiles, and outlier count.",
    25: "The query groups by month and name. It calculates z_score as anomaly metric, aggregates outlier_count, computes partition_avg and partition_stddev, counts trend_direction records, limits to 300 points per model. Output includes anomaly scores, quartiles, and trend counts.",
    26: "The query groups by day and user_id. It uses DATE_TRUNC('month') for period grouping. Calculates quartiles (PERCENTILE_CONT), average, and standard deviation. Limits to 310 points per user. Output includes quartile breakdowns for fiscal period comparison.",
    27: "The query groups by week and name. It calculates record_count (volume), avg_rolling (9-row moving average), max_cumulative (peak capacity). Limits to 320 points per model, ≥1 record per group. Output includes throughput indicators, quartiles, and rolling averages.",
    28: "The query groups by month and user_id. It computes cumulative_sum and max_cumulative. Derives trend_direction and increasing_count. Ranks users by cumulative sum. Filters to ≥2 records per group. Output includes cumulative trend indicators, quartiles, and user rankings.",
    29: "The query groups by day and name. It uses time period (day) and name as grouping dimensions. Aggregates record count, average, quartiles, stddev, min, max, outlier_count, trend indicators. Requires ≥3 records per group. Output includes multi-dimensional aggregate metrics and quartiles.",
    30: "The query groups by week and user_id. It calculates quartiles via PERCENTILE_CONT for Q1 and Q3 (IQR support), flags outliers (z-score > 2), includes stddev_value for IQR-based boundaries, computes trend counts. Limited to 350 points per user. Output includes IQR-style outlier detection, quartiles, and trend metrics.",
}

# db-5: Lucasa POS (phppos_sales: employee_id, customer_id, payment_type, location_id, sale_time, sale_id)
DB5_DESCRIPTIONS = {
    1: "Store managers need visibility into daily employee performance to identify top performers, coach underperformers, and understand whether sales representatives consistently beat their own benchmarks.",
    2: "Marketing and customer success teams segment customers by spending behavior to identify high-value or erratic spenders and detect rising or falling engagement for retention and upsell campaigns.",
    3: "Operations managers need daily performance quartiles to benchmark employees, identify consistent high performers for recognition, and flag statistical outliers who may need coaching or compliance review.",
    4: "Finance and fraud prevention teams monitor payment method performance over time to reconcile accounts, detect unusual transaction patterns, and understand customer payment preferences for strategic planning.",
    5: "Regional managers and real estate teams compare store performance across locations to allocate marketing budgets, decide on lease renewals, and identify underperforming locations requiring operational changes.",
    6: "Sales operations teams monitor employee performance daily to identify unusual patterns that may indicate data entry errors, fraudulent activity, or exceptional performance requiring investigation.",
    7: "Customer success teams want to understand how customer purchasing behavior changes month-over-month to predict churn risk and identify upsell opportunities.",
    8: "Finance and fraud prevention teams monitor payment method usage patterns daily because anomalous behavior may signal technical problems, fraudulent activity, or shifts in customer preferences.",
    9: "Marketing teams segment customers based on recent purchasing activity and frequency to design targeted retention campaigns, loyalty rewards, and personalized upsell offers.",
    10: "Human resources and sales management teams track how employee sales performance evolves over time, similar to cohort retention analysis, to inform training programs and retention strategies.",
    11: "Retail operations teams need to understand sales acceleration patterns at each location to identify high-growth stores for expansion and resource allocation.",
    12: "Sales management teams benchmark employee performance across all locations to identify top performers, establish fair compensation targets, and provide coaching to underperformers.",
    13: "Finance and strategy teams need to understand long-term trends in payment method preferences, filtering out seasonal spikes and promotional effects that create short-term noise.",
    14: "Operations teams optimize staff scheduling and promotional timing by understanding when different customer segments make purchases throughout the day.",
    15: "Corporate strategy and real estate teams prioritize locations for capital investment and concentrated marketing spend using LTV-style principles.",
    16: "Sales management teams evaluate employee performance across different seasons and plan staffing and training budgets for the upcoming fiscal year.",
    17: "Finance and operations teams visualize payment method adoption and transaction velocity patterns throughout the week and month to optimize payment processing infrastructure.",
    18: "Marketing and customer success teams segment customers based on weekly spending behavior to personalize engagement, identify high-value customers for VIP programs, and detect at-risk customers.",
    19: "Regional sales management teams identify which locations have the most effective cross-selling techniques so they can replicate best practices across underperforming stores.",
    20: "Internal audit and loss prevention teams investigate patterns in voided, refunded, or soft-deleted transactions that might indicate employee fraud, system errors, or training issues.",
    21: "Executive teams require a unified dashboard view that consolidates all critical payment-related metrics across different payment types for weekly review meetings.",
    22: "Marketing teams need to understand how individual customer purchasing behavior evolves month-over-month to build effective personalization strategies and targeted campaigns.",
    23: "Operations management needs to understand how revenue is distributed across locations daily for resource allocation, staffing levels, and identifying which locations drive the majority of sales.",
    24: "Human resources and sales management need to systematically identify employees with unusual sales patterns for recognition or compliance investigation.",
    25: "Finance departments require standardized monthly reporting aligned with fiscal periods for month-over-month and quarter-over-quarter comparisons of payment type performance.",
    26: "Business needs to assess transaction volume patterns per customer to optimize system capacity planning and design tiered loyalty programs based on activity levels.",
    27: "Retail operations management requires analysis of payment method trends across store locations to identify shifts in payment mix for terminal deployment and maintenance planning.",
    28: "Business intelligence teams require flexible, multi-dimensional sales data aggregated by time period and employee to support ad-hoc reporting, pivot tables, and cross-functional analysis.",
    29: "Sales and conversion optimization teams track how the mix of payment methods evolves throughout each day to understand customer payment preferences at different times and stages.",
    30: "Fraud detection and customer relationship management teams identify customers with unusual spending patterns using statistical outlier detection to flag potential fraud or high-value VIP customers.",
}

# db-6: Weather consulting insurance (grib2_forecasts, shapefile_boundaries, weather_stations, insurance_rate_tables, NEXRAD, satellite)
DB6_DESCRIPTIONS = {
    1: "Weather consulting firms analyze forecast accuracy and spatial distribution across geographic regions to support insurance risk assessment. Multi-region analysis helps identify where forecasts perform well or poorly.",
    2: "Insurance divisions need hierarchical relationships between administrative boundaries (country, state, county, district) to aggregate weather risk across reporting levels and determine premium calculations at various geographic scales.",
    3: "Actuaries require understanding of how weather parameters (temperature, humidity, wind, precipitation) correlate over time to model compound events that trigger claims, such as heat waves with low humidity increasing wildfire risk.",
    4: "Data engineering teams optimize the spatial ETL pipeline that matches forecast grid points to administrative boundaries. Current queries time out and impact real-time weather alert delivery to policyholders.",
    5: "Operations teams maintain an adequate weather observation network to validate forecasts and trigger parametric payouts. Coverage audits revealed potential gaps in rural and high-risk areas where station density may be insufficient.",
    6: "Weather consulting insurance companies evaluate forecasting model performance over time. grib2_forecasts contains predictions, shapefile_boundaries defines regions, weather_stations holds actual observations.",
    7: "Weather consulting insurance serves clients across geographic scales—properties, municipalities, counties, states. Clients need aggregated forecasts at their boundary level for policy pricing and risk assessment.",
    8: "Insurance companies must validate forecast reliability used in policy pricing by comparing grib2_forecasts predictions against weather_stations measurements. Systematic errors affect claim accuracy and regulatory compliance.",
    9: "Insurance policies often cover areas spanning multiple boundaries (flood zones crossing counties, agricultural regions spanning municipalities). Multi-jurisdictional overlap identification is required.",
    10: "Insurance companies use weather parameters from grib2_forecasts (temperature, precipitation, wind, humidity) to assess risk and price policies. Statistical distribution analysis supports underwriting.",
    11: "Weather consulting firms interpolate forecast data between stations and identify areas with sharp weather gradients that could indicate high-risk zones for insurance clients.",
    12: "Insurance underwriters identify recurring weather patterns across regions and time periods to predict claim frequencies. Patterns include cold fronts, heat waves, and storm systems with spatial and temporal persistence.",
    13: "Weather consulting firms integrate forecasts from multiple NWP models (GFS, ECMWF, NAM). Each model has different strengths; continuous evaluation against observations across boundaries is required.",
    14: "Insurance policies cover specific boundaries. Forecasts at boundary edges sometimes exhibit anomalies from interpolation, terrain, or genuine extreme events. Outlier identification distinguishes data quality issues from real events.",
    15: "Insurance companies need quantitative risk factors for medium-range exposure (7-14 days) to adjust premiums, trigger parametric policies, and allocate claims reserves. Ensemble forecasts cover temperature extremes, precipitation, wind.",
    16: "Weather consulting insurance teams price policies based on predicted weather risk. Rate tables translate forecast risk factors into pricing tiers for underwriting.",
    17: "The weather consulting team needs to understand how forecast prediction errors impact insurance rate calculations across geographical boundaries and time periods.",
    18: "Insurance actuaries need to correlate forecast uncertainty (ensemble spread) with historical claim volatility to calibrate risk models and set appropriate confidence intervals for rate tables.",
    19: "Insurance product managers need to compare rate tables across forecast days (7-14) to identify which lead times produce the most stable and reliable pricing for different policy types and regions.",
    20: "Risk managers need to understand which weather parameters (temperature, precipitation, wind) contribute most to rate variations across policy areas and forecast horizons for model refinement.",
    21: "Insurance underwriters need to understand how forecast prediction errors impact insurance rate calculations. Correlation between forecast accuracy and rate variations across boundaries and time periods supports model calibration.",
    22: "Insurance underwriters need multi-day ensemble statistics (spread, IQR, coefficient of variation) across forecast days 7-14 to assess rate variability and confidence intervals for pricing decisions.",
    23: "Pricing teams face a tradeoff between forecast lead time and accuracy when setting rates. Day 1 is most accurate but provides little advance notice; Day 7 allows planning but has higher error. Data-driven guidance is needed.",
    24: "Executive leadership requires a holistic view of the weather-based insurance program's analytical foundation for quarterly business reviews.",
    25: "Claims response teams need real-time situational awareness of severe weather across the US to proactively allocate adjusters and predict claim surges.",
    26: "Weather consulting firms providing insurance risk assessment need to analyze severe weather events. Storm cell tracking supports claims preparation and exposure assessment.",
    27: "National weather service providers create synoptic-scale cloud coverage products for media broadcast and public dissemination across the US.",
    28: "Hydrological forecasting agencies require accurate precipitation estimates for flood prediction and water resource management. NEXRAD provides high-resolution ground data; satellites offer broader coverage.",
    29: "Wildfire management agencies and insurance risk assessment teams monitor active fires across the continental US to coordinate suppression and evaluate property exposure.",
    30: "National weather forecasting centers produce comprehensive analysis products leveraging both ground-based radar and space-based satellite observations for seamless coverage.",
}

DB6_EVIDENCE = {
    1: "The query uses multiple nested CTEs to extract and filter forecast parameters from grib2_forecasts, spatially joins with shapefile_boundaries (ST_Contains, ST_Intersects), aggregates by region and time, computes mean/median/quartiles for temperature/precipitation/wind, and applies window functions for rolling averages and comparative metrics.",
    2: "The query employs a recursive CTE with shapefile_boundaries as anchor, recursively joins boundaries using ST_Contains/ST_Within for parent-child relationships, tracks hierarchy depth and path, accumulates area/perimeter metadata, applies window functions for cumulative statistics, and aggregates weather station counts per level.",
    3: "The query creates CTEs to pivot weather parameters into separate columns, performs temporal alignment with common time windows, computes correlation coefficients between parameter pairs across rolling windows, applies LAG/LEAD for temporal sequences and phase relationships.",
    4: "The query creates CTEs to analyze spatial join cardinality (forecast points per boundary, boundaries per cell), measures join selectivity, evaluates spatial index effectiveness, groups by boundary complexity and forecast resolution, applies window functions to rank boundaries by processing time.",
    5: "The query creates CTEs to calculate Voronoi/buffer zones around weather_stations, spatially joins with shapefile_boundaries to identify insufficient-density regions, computes coverage statistics (percentage covered, station density, average distance to nearest station).",
    6: "The query joins grib2_forecasts with weather_stations, groups by time period and forecast parameter, calculates error metrics (MAE, RMSE, bias), applies window functions for rolling accuracy and period-over-period comparison, handles NULLs via LEFT JOINs.",
    7: "The query performs spatial joins between grib2_forecasts and shapefile_boundaries using geographic intersection, groups by boundary hierarchy levels, computes aggregate statistics (mean, min, max, stddev), applies quartile calculations and window functions.",
    8: "The query joins grib2_forecasts with weather_stations by matching grid points to nearest stations and forecast times to observation timestamps, groups by station/parameter/period, calculates absolute error, percentage error, hit rates, skill scores, applies window functions for station-specific baselines.",
    9: "The query performs self-joins on shapefile_boundaries using spatial intersection functions, groups by boundary type pairs and regions, calculates overlap areas and percentages, uses window functions to rank boundaries by coverage.",
    10: "The query groups grib2_forecasts by parameter, spatial boundary (from shapefile_boundaries), and time period, computes mean/median/stddev/min/max/coefficient of variation, calculates quartiles and percentiles for distribution shape.",
    11: "The query joins forecast grid data with boundaries and station observations, groups by region and parameter, computes spatial interpolation metrics using neighboring points, calculates gradient magnitudes via window functions comparing adjacent cells, applies quartile analysis for high-gradient areas.",
    12: "The query aggregates forecast parameters by region and time, employs multi-dimensional clustering on temperature/precipitation/pressure, uses window functions for temporal persistence (rolling averages, LAG comparisons), identifies spatial coherence via correlation between adjacent regions.",
    13: "The query joins forecast data from multiple models with observations, groups by model/parameter/region/lead time, computes bias/MAE/RMSE, uses window functions for rolling accuracy and model ranking, applies quartile analysis for consistency.",
    14: "The query spatially joins forecast grid points with boundary polygons for edge regions, groups by boundary and parameter, computes mean/stddev/interquartile ranges, applies window functions for z-scores and modified z-scores for anomaly detection.",
    15: "The query filters forecasts to 7-14 day lead time, joins with insured boundaries and weather_stations, groups by region/forecast date/risk parameter, computes max values, accumulation totals, and probability of threshold exceedance.",
    16: "The query joins forecast data with boundaries and observations, groups by region and risk parameters, calculates aggregate risk scores using quartile distributions, applies window functions for rolling risk trends and comparative metrics, handles NULLs in spatial joins.",
    17: "The query constructs five CTEs: forecast_period, forecast_rate_mapping_data (joins forecast_rate_mapping, grib2_forecasts, insurance_rate_tables), parameter_impact_aggregation, parameter_contribution_analysis (window functions for contribution_percentage), parameter_ranking (ROW_NUMBER for impact/contribution rank). Output includes impact_classification.",
    18: "The query joins ensemble forecast data with historical claim rates, groups by region and forecast day, computes ensemble spread metrics (stddev, IQR), applies window functions for day-over-day spread changes and 7-day rolling averages, uses quartile analysis for reliability segmentation.",
    19: "The query compares insurance_rate_tables across forecast days 7-14, groups by policy_area/policy_type/coverage_type, computes rate volatility and confidence metrics, applies window functions for cross-day comparison, produces recommendation_status.",
    20: "The query uses five CTEs: forecast_period, forecast_rate_mapping_data, parameter_impact_aggregation, parameter_contribution_analysis (CASE for contribution_percentage, impact_percentage_of_base_rate), parameter_ranking (ROW_NUMBER for parameter_impact_rank, parameter_contribution_rank). Output includes impact_classification.",
    21: "The query joins grib2_forecasts with weather_stations and shapefile_boundaries, groups by region/forecast horizon/parameter, computes forecast error rates, correlates with rate changes, applies window functions for rolling 30-day accuracy, uses quartile analysis for forecast-to-rate sensitivity.",
    22: "The query uses five CTEs: rate_ensemble_data, ensemble_statistics (PERCENTILE_CONT for quartiles, STDDEV, VARIANCE), ensemble_consensus_calculation (consensus_rate, confidence_interval, IQR, coefficient_of_variation), ensemble_quality_assessment (ensemble_quality_score, ensemble_reliability).",
    23: "The query uses six CTEs: forecast_day_metrics, forecast_day_scoring (confidence_score, stability_score, accuracy_score, planning_horizon_score), optimization_scoring (weighted overall_optimization_score), forecast_day_ranking (ROW_NUMBER, PERCENT_RANK), recommendation_generation (recommendation_status, recommendation_justification).",
    24: "The query uses seven CTEs: risk_factors_summary, rate_tables_summary, rate_comparison_summary, claims_validation_summary, comprehensive_summary (FULL OUTER JOINs), dashboard_metrics (risk_category, rate_stability, overall_status CASE expressions).",
    25: "The query uses eight CTEs: us_spatial_bounds, active_nexrad_sites, recent_nexrad_scans, nexrad_reflectivity_data (ST_DISTANCE, quality_weight, distance_weight), us_grid_cells, grid_nexrad_matching (ST_DWITHIN), weighted_reflectivity_calculation (inverse distance weighting), final_composite_reflectivity (precipitation_intensity, coverage_quality).",
    26: "The query uses seven CTEs: time_window, storm_cells_by_scan (ROW_NUMBER for scan_number), storm_cell_movement (ST_DISTANCE, movement_speed_kmh, movement_direction_deg via ATAN2/DEGREES), storm_cell_association (association_confidence), storm_track_aggregation, storm_development_analysis (development_trend, severity_classification), predicted_storm_path (ST_TRANSLATE for 1h/2h predictions).",
    27: "The query uses eight CTEs: us_spatial_bounds, active_satellite_sources, recent_satellite_scans, satellite_cloud_data, us_grid_cells, grid_satellite_matching (ST_DWITHIN), cloud_property_aggregation (cloud_top_height, cloud_phase, optical_depth), final_cloud_composite (dominant_cloud_phase, cloud_height_classification, cloud_thickness_classification).",
    28: "The query uses eight CTEs: us_spatial_bounds, recent_nexrad_precipitation, recent_satellite_precipitation, us_precipitation_grid, grid_nexrad_matching, grid_satellite_matching, fused_precipitation_calculation (FULL OUTER JOIN), final_fused_precipitation (weighted combination by quality weights, precipitation_intensity).",
    29: "The query uses five CTEs: us_spatial_bounds, recent_fire_detections, fire_clustering (ROW_NUMBER for cluster_id), fire_cluster_aggregation (ST_MAKEPOINT for cluster_center_geom, SUM fire_power_mw), fire_intensity_classification (fire_intensity_classification, fire_status).",
    30: "The query uses four CTEs: us_spatial_bounds, recent_nexrad_data, recent_satellite_data, us_composite_grid, grid_data_matching (LEFT JOIN with ST_DWITHIN, AVG for reflectivity/precipitation), composite_calculation (weighted fusion: 0.6 NEXRAD + 0.4 satellite for precipitation, data_source classification).",
}

# db-7: Maritime shipping intelligence (vessel_tracking, port_calls, sailings, carriers)
DB7_DESCRIPTIONS = {
    1: "Fleet managers need visibility into vessel positions, movements, and navigation status to ensure operational safety and efficiency. Real-time tracking data from vessel_tracking, port_calls, sailings, and carriers supports fleet monitoring.",
    2: "Port operations teams manage dozens of port calls daily across multiple terminals. Delays create cascading supply chain effects; management needs quantifiable metrics to identify bottlenecks and improve turnaround times.",
    3: "Logistics planning manages shipping routes across multiple carriers. Rising fuel costs and customer demands for faster delivery require data-driven route optimization and carrier benchmarking.",
    4: "Procurement evaluates carrier contracts annually. Contract renewals and carrier selection require objective performance metrics; management needs standardized reliability scores and rankings to negotiate better terms.",
    5: "Port authority managers oversee operations across terminals. Stakeholders require regular reporting on port performance to justify infrastructure investments and optimize berth allocation.",
    6: "Maritime shipping operations teams maximize fleet efficiency and identify underutilized vessels. Capacity utilization and route efficiency metrics support vessel redeployment decisions.",
    7: "Network planning teams understand complex multi-leg shipping routes and identify inefficient transshipment patterns that increase costs and transit times.",
    8: "Carrier management and procurement teams evaluate vessel performance across carrier partners to inform contract negotiations and identify underperforming assets.",
    9: "Commercial strategy and business development teams understand trade lane demand patterns and identify high-growth corridors for service expansion.",
    10: "Operations and service reliability teams understand why voyages are delayed or fail to complete and which ports or routes have the highest success rates.",
    11: "Maritime shipping operations managers evaluate carrier performance across different routes to make informed decisions about carrier partnerships and contract negotiations.",
    12: "Fleet operations teams monitor vessel movements in real-time to ensure vessels follow optimal routes and maintain efficient speeds for fuel economy and schedule adherence.",
    13: "Port authorities and terminal operators maximize berth utilization while minimizing vessel waiting times and congestion.",
    14: "Shippers and logistics providers require reliable sailing schedules to plan supply chain operations and meet customer commitments.",
    15: "Maritime industry analysts and business development teams understand competitive dynamics across trade routes to identify market opportunities and assess competitive threats.",
    16: "Maritime shipping operations managers optimize vessel routes to reduce operational costs and improve delivery times.",
    17: "Shipping lines operate complex multi-port voyages where port call sequence directly impacts voyage efficiency and profitability. Excessive dwell time and suboptimal sequencing increase costs.",
    18: "Operations teams benchmark individual vessel performance against fleet averages to identify outliers and target interventions for operational excellence.",
    19: "Network planners map port-to-port connections, calculate connectivity metrics, identify hub ports, and optimize network structure.",
    20: "Schedule planning teams calculate actual service frequencies by route, measure schedule consistency, and identify gaps in service coverage.",
    21: "Operations teams predict delay probabilities for upcoming port calls and identify primary risk factors to support mitigation planning.",
    22: "Finance and strategy teams calculate revenue metrics per route, evaluate cost efficiency ratios, and optimize route profitability.",
    23: "Fleet strategy teams quantify relationships between vessel age and operational metrics to establish modernization priorities.",
    24: "Capacity planning teams identify recurring demand patterns by season, month, and week and pinpoint peak shipping periods.",
    25: "Port operators calculate utilization rates for key port resources and evaluate operational efficiency for optimization.",
    26: "Operations teams quantify transit time reliability and schedule predictability across routes for service quality assessment.",
    27: "Strategy teams analyze historical growth patterns, forecast trade volumes, and identify emerging market opportunities for port pair routes.",
    28: "Shipping lines optimize vessel deployment across routes to maximize asset utilization, minimize costs, and meet service commitments.",
    29: "Maritime carriers form strategic alliances to share vessels and coordinate schedules; alliance performance evaluation supports partnership optimization.",
    30: "Maritime shipping executives require integrated visibility across operational, financial, and market dimensions for informed strategic decisions.",
}

DB7_EVIDENCE = {
    1: "The query employs six CTEs: vessel_tracking_cohorts (base extraction), vessel_position_sequences (LAG/LEAD for prev/next position), vessel_movement_calculations (ST_DISTANCE, calculated speed, bearing), vessel_route_deviations (correlated subqueries for nearest route, distance to route, speed/course deviation), vessel_operational_patterns (rolling avg, cumulative distance, window functions), vessel_status_classification (operational_status, route_deviation_status, data_freshness_status CASE expressions).",
    2: "The query uses four CTEs: port_call_cohorts, port_call_delay_calculations (arrival/departure delay, dwell time, EXTRACT EPOCH), port_call_performance_metrics (30-row moving avg, PERCENT_RANK, on_time indicators), port_call_classification (arrival_performance_class, dwell_time_efficiency_class CASE expressions).",
    3: "The query uses six CTEs: route_sailing_analysis, route_port_pair_aggregation (PERCENTILE_CONT, STDDEV), route_efficiency_calculations (transit variance, speed_efficiency_nm_per_day), carrier_route_comparison (correlated subqueries for fastest competitor, RANK within port pair), route_optimization_scoring (weighted optimization_score), route_classification.",
    4: "The query uses six CTEs: carrier_sailing_metrics, carrier_port_call_metrics (on_time counts, delay/dwell AVGs), carrier_performance_aggregation (completion rates, on-time rates), carrier_performance_comparison (AVG OVER for market averages, RANK, PERCENT_RANK), carrier_reliability_scoring (weighted reliability_score), carrier_performance_classification.",
    5: "The query groups port call data by port identifier and terminal, aggregating vessel calls and summing TEUs from sailings joined to port calls. Computes berth utilization and throughput-to-handling efficiency metrics.",
    6: "The query joins vessel_tracking with port_calls and sailings, groups by vessel/carrier/route, computes utilization percentages and efficiency ratios, applies window functions for rolling averages and quartile analysis.",
    7: "The query joins port_calls with sailings to construct sequential port visit chains, uses LAG/LEAD to identify transshipment events (vessel change mid-route), groups by origin-destination pairs and intermediate stops.",
    8: "The query joins vessels with carriers and links to sailings and port_calls, groups by carrier and vessel, computes utilization percentages (capacity vs actual load), schedule adherence, and performance indicators.",
    9: "The query joins port_calls with sailings to identify origin-destination port pairs, groups by port pair, computes total shipments and cargo volume, applies window functions for period-over-period growth and moving averages.",
    10: "The query joins sailings with port_calls to match planned voyages with actual outcomes, calculates completion status (actual vs scheduled), groups by route/carrier/port, computes completion percentages and on-time rates.",
    11: "The query joins carrier, sailings, port_calls, and vessel_tracking, aggregates by carrier and route, computes on-time rates and transit times, uses window functions for competitive rankings and quartile analysis.",
    12: "The query retrieves vessel positions from vessel_tracking, joins with sailings for planned routes, uses ST_DISTANCE for deviation, flags threshold exceedances, applies window functions for rolling speed pattern analysis.",
    13: "The query aggregates port_calls by port and berth, calculates occupancy rates (berth-occupied/time), turnaround and waiting times, uses window functions for peak congestion detection via rolling utilization.",
    14: "The query joins sailings with port_calls to compare scheduled vs actual times, calculates delay durations and severity, computes on-time percentages by carrier/route/period, uses window functions for rolling trends.",
    15: "The query aggregates sailings and port_calls by carrier and route (origin-destination pairs), counts voyages or capacity deployment, computes each carrier's percentage share of total route activity.",
    16: "The query joins vessel_tracking, port_calls, and sailings to construct voyage paths, groups by route and vessel type, computes fuel per nm, transit time, distance, uses window functions for rolling metrics.",
    17: "The query extracts port call sequences from port_calls ordered by timestamp per voyage, uses LAG/LEAD for consecutive port pairs and distance calculation, groups by voyage and port sequence.",
    18: "The query joins vessel_tracking, sailings, and port_calls for each vessel, groups by vessel, calculates KPIs, uses window functions for fleet-average comparison and outlier identification.",
    19: "The query constructs a network graph from sailings and port_calls (ports as nodes, routes as edges), groups by port for connectivity metrics and centrality measures.",
    20: "The query analyzes sailings grouped by route (origin-destination) and time period, calculates service frequencies, schedule consistency, and identifies coverage gaps.",
    21: "The query joins vessel_tracking, port_calls, sailings, and carriers, groups by port/carrier/period, computes delay statistics, uses window functions for rolling delay averages and trend identification.",
    22: "The query joins sailings, port_calls, carriers, and vessel_tracking, groups by route/carrier/vessel type, computes revenue, costs, fuel, port fees, net margin, uses window functions for profitability metrics.",
    23: "The query joins carriers and sailings for vessel metadata (build dates), links to vessel_tracking and port_calls, calculates vessel age, correlates with performance metrics.",
    24: "The query extracts temporal dimensions from port_calls and sailings, groups by year/quarter/month/week/day-of-week, calculates volume metrics and identifies patterns at multiple granularities.",
    25: "The query joins port_calls with vessel_tracking and sailings to reconstruct visit timelines, groups by port/berth/period, calculates utilization rates and efficiency metrics.",
    26: "The query joins vessel_tracking with port_calls and sailings for actual vs scheduled transit times, groups by carrier/route/vessel, computes stddev and coefficient of variation, uses window functions for rolling averages and quartile analysis.",
    27: "The query aggregates sailings and port_calls by port pairs over multiple periods, calculates period-over-period growth, uses window functions for moving averages and YoY comparison, groups by port pairs/carriers/vessel types.",
    28: "The query joins vessel_tracking, sailings, and port_calls with carrier fleet info, groups by vessel type/size/route, calculates utilization and capacity matching, uses window functions for cross-route performance comparison.",
    29: "The query aggregates carriers, sailings, and vessel_tracking by alliance membership, compares solo vs collaborative performance, calculates shared capacity utilization and schedule coordination, uses window functions for member comparison.",
    30: "The query performs complex joins across vessel_tracking, port_calls, sailings, and carriers, groups by time/region/carrier/vessel type/route, computes operational KPIs via aggregate functions, uses window functions for comparative metrics.",
}

DB5_EVIDENCE = {
    1: "The query groups transactions by date and employee_id. It computes each employee's overall average (emp_avg), uses a 7-row window for rolling_avg_7d, counts transactions exceeding emp_avg (above_avg_count), retains the 100 most recent per employee, and excludes days with only one transaction. Output includes record_count, quartiles, stddev, above_avg_count, and avg_rolling_7d.",
    2: "The query groups by month and customer_id. It uses NTILE(6) for sextiles, calculates z-scores per partition, flags outliers (>2 std dev), derives trend_direction via LAG/LEAD delta_value, limits to 70 points per customer, and requires ≥3 monthly records. Aggregates include quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    3: "The query groups by day and employee_id. It uses PERCENTILE_CONT for Q1, median, Q3; computes a 7-row rolling average; segments into septiles (NTILE(7)); flags outliers via z-score; and includes single-transaction days. Output includes quartiles, stddev, outlier count, increasing count, and rolling average.",
    4: "The query groups by week and payment_type. It uses an 8-row rolling window, segments into octiles (NTILE(8)), derives trend_direction from LAG/LEAD, and requires ≥2 weekly records per payment type. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    5: "The query groups by month and location_id. It computes STDDEV for volatility, uses a 9-row rolling window, segments into noniles (NTILE(9)), limits to 100 points per location, and requires ≥3 monthly records. Output includes quartiles, stddev, outlier count, increasing count, and max cumulative sum.",
    6: "The query groups by day and employee_id. It extracts hour and day-of-week, computes z-scores (zero when stddev=0), flags outliers, calculates a 10-row rolling average, and includes single-transaction days. Output includes quartiles, rolling average, outlier count, and increasing count.",
    7: "The query groups by month and customer_id. It employs LAG and LEAD for gap analysis between consecutive periods, derives trend_direction, computes quartiles, and requires ≥3 months of purchase history. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    8: "The query groups by day and payment_type. It calculates z-scores to flag outliers, computes quartiles, derives trend_direction from LAG/LEAD, and requires ≥2 transactions per payment type per day. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    9: "The query groups by day and customer_id. It applies ROW_NUMBER (desc) for recency scoring, uses record count as frequency proxy, ranks by cumulative sum, computes 6-row rolling average, and requires ≥1 record per group. Output includes quartiles, outlier count, increasing count, and rolling average.",
    10: "The query groups by week and customer_id. It calculates increasing_count and trend_direction (cohort-style), derives quartiles, accommodates single-record months for new hires, and requires ≥2 records per group. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    11: "The query groups by day and location_id. It computes delta_value as acceleration indicator, calculates quartiles (PERCENTILE_CONT), counts outliers, and requires ≥2 transactions per location-day. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    12: "The query groups by week and employee_id. It computes PERCENT_RANK for cross-location percentile position, applies DENSE_RANK for tier classification, calculates quartiles, and requires ≥3 transactions per employee-week. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    13: "The query groups by month and payment_type. It computes a rolling average using ROWS BETWEEN, calculates Q1, median, Q3 quartiles, and requires ≥2 records per payment-type-month. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    14: "The query groups by day and customer_id. It extracts hour for peak identification, calculates quartiles, includes single-transaction customer-days, and uses rolling avg and cumulative sum. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    15: "The query groups by day and customer_id (LTV by location). It computes cumulative_sum and max_cumulative as LTV proxies, ranks locations by cumulative sum, calculates quartiles, and requires ≥1 record per group. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    16: "The query groups by week and employee_id. It calculates trend_direction and delta_value for YoY-style growth, computes quartiles, limits to 210 points per employee, and requires ≥2 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    17: "The query groups by day and payment_type. It uses period and payment_type as heatmap axes, calculates quartiles and trend counts, and requires ≥2 records per day-payment group. Output includes quartiles, outlier count, increasing count, rolling avg, and max cumulative sum.",
    18: "The query groups by day and sale_id (customer proxy). It employs PERCENT_RANK for running percentile position and PERCENTILE_CONT for quartile boundaries. Requires ≥1 record per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    19: "The query groups by week and employee_id. It uses DENSE_RANK for location ranking, calculates quartiles, and produces cross-sell-style metrics. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    20: "The query groups by month and employee_id. It uses LAG and LEAD for sequential transaction analysis, calculates time gaps between consecutive transactions, derives trend_direction, and computes quartiles. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    21: "The query groups by day and employee_id. It performs single-pass aggregation: record_count, avg_value, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, max_cumulative. Requires ≥1 record per group. Output includes full dashboard suite of statistics.",
    22: "The query groups by week and customer_id. It employs LAG and LEAD for previous/next month values, calculates delta_value and trend_direction for sequential patterns, and requires ≥2 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    23: "The query groups by month and customer_id. It uses DENSE_RANK and PERCENT_RANK for concentration indices, cumulative_sum for revenue concentration, and requires ≥3 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    24: "The query groups by day and employee_id. It calculates z_score as anomaly metric, aggregates outlier_count, computes quartiles, and requires ≥1 record per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    25: "The query groups by week and location_id. It uses DATE_TRUNC('month') for fiscal period alignment, calculates quartiles (PERCENTILE_CONT), and requires ≥2 records per payment-type-month. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    26: "The query groups by month and employee_id. It calculates record_count (throughput proxy), avg_rolling, max_cumulative, preserves single-transaction months, and requires ≥3 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    27: "The query groups by day and customer_id. It computes trend_direction and increasing_count for payment trend analysis, requires ≥1 record per group, and produces quartiles and cumulative metrics. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    28: "The query groups by week and employee_id. It uses period and employee_id as dimensional axes for pivoting, retains single-record months for complete coverage, and requires ≥2 records per group. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    29: "The query groups by month and customer_id. It calculates trend_direction for funnel stage progression, requires ≥3 records per group, and produces quartiles and cumulative metrics. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
    30: "The query groups by day and sale_id (customer proxy). It calculates quartiles via PERCENTILE_CONT for Q1 and Q3 (IQR support), flags outliers (z-score > 2), and requires ≥3 records per customer-week. Output includes quartiles, stddev, outlier count, increasing count, rolling avg, and max cumulative sum.",
}


def fix_db1(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB1_DESCRIPTIONS and n in DB1_EVIDENCE:
            if q.get("description") != DB1_DESCRIPTIONS[n] or q.get("evidence") != DB1_EVIDENCE[n]:
                q["description"] = DB1_DESCRIPTIONS[n]
                q["evidence"] = DB1_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def fix_db3(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB3_DESCRIPTIONS and n in DB3_EVIDENCE:
            if q.get("description") != DB3_DESCRIPTIONS[n] or q.get("evidence") != DB3_EVIDENCE[n]:
                q["description"] = DB3_DESCRIPTIONS[n]
                q["evidence"] = DB3_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def fix_db4(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB4_DESCRIPTIONS and n in DB4_EVIDENCE:
            if q.get("description") != DB4_DESCRIPTIONS[n] or q.get("evidence") != DB4_EVIDENCE[n]:
                q["description"] = DB4_DESCRIPTIONS[n]
                q["evidence"] = DB4_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def fix_db5(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB5_DESCRIPTIONS and n in DB5_EVIDENCE:
            if q.get("description") != DB5_DESCRIPTIONS[n] or q.get("evidence") != DB5_EVIDENCE[n]:
                q["description"] = DB5_DESCRIPTIONS[n]
                q["evidence"] = DB5_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def fix_db6(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB6_DESCRIPTIONS and n in DB6_EVIDENCE:
            if q.get("description") != DB6_DESCRIPTIONS[n] or q.get("evidence") != DB6_EVIDENCE[n]:
                q["description"] = DB6_DESCRIPTIONS[n]
                q["evidence"] = DB6_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def fix_db7(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB7_DESCRIPTIONS and n in DB7_EVIDENCE:
            if q.get("description") != DB7_DESCRIPTIONS[n] or q.get("evidence") != DB7_EVIDENCE[n]:
                q["description"] = DB7_DESCRIPTIONS[n]
                q["evidence"] = DB7_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-8: Job Market Intelligence (job_postings, applications, skills, user_profiles)
DB8_DESCRIPTIONS = {
    1: "A job marketplace platform needs to connect candidates with relevant opportunities by analyzing user profiles, job postings, required skills, and historical application data.",
    2: "Job seekers need to understand their skill gaps relative to desired positions and receive actionable learning recommendations. The skills database contains hierarchical relationships where advanced skills have prerequisite dependencies that must be learned first.",
    3: "The job market intelligence team needs to identify emerging trends, forecast skill demand, and track salary movements to advise both job seekers and employers on market dynamics.",
    4: "The platform analytics team needs to understand application conversion patterns to optimize the candidate-employer matching process and identify bottlenecks in the hiring funnel.",
    5: "Employers and market analysts need visibility into competitive dynamics among companies in the job marketplace.",
    6: "Job market analysts need to understand regional employment dynamics across different locations, including job density, salary distributions, and remote work patterns.",
    7: "Compensation analysts and hiring managers need to understand how salaries compare across different roles, experience levels, and industries to ensure competitive offers.",
    8: "Platform product managers and workforce analysts need to understand how different user cohorts behave over time—engagement, retention, and career advancement.",
    9: "Talent strategists and training directors need to identify where skill demand from employers exceeds candidate supply, creating market opportunities.",
    10: "Federal employment analysts and career counselors need to understand hiring patterns across federal agencies. The system integrates data from usajobs.gov with federal-specific attributes.",
    11: "The job platform needs to understand how users search for jobs to improve the recommendation engine and user experience.",
    12: "The talent acquisition team needs visibility into which funnel stages cause the most friction in application completion rates.",
    13: "Job seekers ask which additional skills they should learn to maximize career opportunities and earning potential.",
    14: "Hiring managers need to understand inconsistent time-to-fill across roles and departments to reduce recruitment costs.",
    15: "Employers and job seekers need visibility into remote and hybrid work adoption patterns across sectors and regions.",
    16: "The Job Market Intelligence platform ingests data from multiple sources and needs quality reports on extraction metrics and freshness.",
    17: "The job_postings table contains thousands of job titles with inconsistent naming conventions that need normalization and clustering.",
    18: "The applications table tracks outcomes for job applications. Job seekers and employers need to understand success probability and optimizing factors.",
    19: "The job_postings table reveals company hiring activity over time. Analysts need to identify rapidly growing companies and expansion patterns.",
    20: "The skills table captures employer demand over time. Training providers and job seekers need to identify emerging skills and demand trajectories.",
    21: "Job seekers need to understand when to submit applications for maximum success.",
    22: "Professionals considering industry changes need insights into successful transition patterns and career paths.",
    23: "Job candidates and hiring managers need objective salary data to support effective negotiations.",
    24: "Job seekers and employers need to understand supply-demand dynamics in different market segments.",
    25: "Platform operators need to understand how users progress through the job search and application process to optimize conversion.",
    26: "Career services analysts need to help job seekers understand potential career progression paths and advancement opportunities.",
    27: "Market research analysts need to segment the job market into distinct clusters for targeted strategies.",
    28: "Strategic planning analysts need to forecast future market conditions to support proactive business decisions.",
    29: "Data integration specialists need to match job seekers with opportunities across multiple databases, with deduplication and source tracking.",
    30: "Business intelligence directors need a comprehensive executive dashboard synthesizing market performance across all dimensions.",
}

DB8_EVIDENCE = {
    1: "The query joins user_profiles with job_postings and skills tables, groups results by user and job to calculate multi-dimensional match scores, computes skill overlap percentages and gap analysis, evaluates location and salary compatibility using threshold comparisons, applies window functions to rank recommendations per user based on composite scores, and handles NULL values in optional profile fields.",
    2: "The query uses a recursive CTE to traverse the skills hierarchy and identify prerequisite chains, joins user_profiles with job_postings to identify required versus possessed skills, groups by user and skill category to aggregate gap metrics, and applies window functions to sequence learning recommendations.",
    3: "The query aggregates job_postings and applications data by month, location, and skill category using GROUP BY with date functions, calculates period-over-period growth rates using LAG window functions, computes rolling averages and quartile distributions for salary trends, and applies time-series aggregation.",
    4: "The query joins applications with user_profiles and job_postings to create cohort segments based on experience level, location, and industry, groups by cohort and application stage to calculate conversion rates at each funnel stage.",
    5: "The query aggregates job_postings by company to calculate posting volumes and market share percentages, groups applications by company to measure candidate interest and application rates, and applies time-series grouping.",
    6: "The query joins user_profiles, job_postings, skills, and applications tables, groups by geographic dimensions (city, state, region), and computes job counts, average salaries, percentiles, remote work percentages, and application-to-job ratios.",
    7: "The query joins job_postings with skills and related tables, groups by job title, industry, experience level, and company size, and calculates mean, median, percentiles (25th, 50th, 75th, 90th) for salary benchmarking.",
    8: "The query creates cohorts by extracting registration date periods from user_profiles, uses self-joins or window functions to track user activity over subsequent periods, and calculates retention rates and application patterns.",
    9: "The query aggregates skills from job_postings to measure demand and from user_profiles to measure supply, joins these aggregates to quantify market imbalances, and identifies high-demand skills with low supply.",
    10: "The query filters job_postings for federal positions, groups by agency and department, computes pay plan and grade level distributions, and analyzes geographic distribution and hiring trends over time.",
    11: "The query joins user_profiles with applications and job_postings to track search sessions, groups by search criteria and user segments, computes engagement metrics and conversion rates, and applies window functions for rolling search trends.",
    12: "The query joins applications with job_postings and user_profiles to construct the funnel journey, groups by funnel stage and job characteristics, computes stage-by-stage conversion rates and drop-off percentages using aggregates and LAG window functions.",
    13: "The query performs self-joins on the skills table to identify skill pairs within the same job posting or user profile, groups by skill combination and job category, computes co-occurrence frequencies and lift metrics, and calculates average salary premiums by joining with job_postings.",
    14: "The query joins job_postings with applications to calculate time-to-fill (days from posting to acceptance), groups by job category, seniority level, location, and company attributes, and computes velocity metrics using aggregates and window functions.",
    15: "The query groups job_postings by work location type, industry, geography, and time period, computes adoption rates and year-over-year growth, and applies window functions for moving averages and trend analysis.",
    16: "The query groups records by data source and time period, computes extraction success rates, record counts, and data age, and uses window functions for rolling averages and comparative metrics across sources.",
    17: "The query groups job postings by title variations, computes string similarity metrics, aggregates posting counts per variant, applies clustering logic to group similar titles, and uses window functions to rank titles within clusters.",
    18: "The query joins applications with user_profiles, job_postings, and skills to create feature vectors (skill match rate, experience level, application timing), computes aggregates grouped by applicant characteristics and job attributes, and uses window functions for percentile rankings.",
    19: "The query groups job_postings by company and time period, computes hiring volume trends and expansion patterns across locations and departments, and applies window functions for growth rate calculations.",
    20: "The query joins skills with job_postings to track demand over time, groups by skill and time period, computes trend indicators and demand trajectories, and classifies skills by lifecycle stage using aggregates and window functions.",
    21: "The query joins applications with job_postings and user_profiles, groups by time dimensions (hour of day, day of week, time since posting), computes success rate aggregates and response time quartiles, and uses window functions for rolling averages and comparative metrics.",
    22: "The query joins user_profiles with applications and job_postings to track industry changes, groups by source and target industry pairs, computes success rate aggregates and transition frequency counts, and uses window functions for sequential career move analysis.",
    23: "The query joins job_postings with applications, user_profiles, and skills, groups by role, industry, location, and experience level, computes salary percentiles and quartiles via PERCENTILE_CONT, and uses window functions for market positioning and leverage factor aggregation.",
    24: "The query joins applications with job_postings and user_profiles, groups by role, industry, location, and skill categories, computes applicant-to-job ratios and opportunity density, and uses window functions for saturation scoring.",
    25: "The query joins user_profiles with applications and job_postings to reconstruct user journeys, sequences interactions chronologically to build funnel stages, groups by cohort and entry point, and computes conversion rates using LAG for drop-off analysis.",
    26: "The query uses recursive CTEs to trace multi-level career progressions from entry to senior positions, groups by job title sequences and industry verticals, computes aggregate metrics like time-to-promotion and success rates, and applies window functions to rank optimal paths.",
    27: "The query groups data by industry, location_state, work_model, and job_type, computes segment size and growth metrics, calculates quartiles for segment boundaries, and uses window functions to compare segments and compute attractiveness scores.",
    28: "The query groups historical data by month and relevant dimensions, computes rolling aggregates using window functions (LAG, ROWS BETWEEN), calculates year-over-year growth rates, and generates forward projections with confidence intervals.",
    29: "The query uses UNION/UNION ALL to combine results from multiple sources, applies standardization logic for job titles and locations, uses MD5 fingerprinting for deduplication, and applies FIRST_VALUE and source priority ordering.",
    30: "The query builds multiple CTEs (market_overview_metrics, user_engagement_metrics, skill_market_metrics, industry_breakdown, geographic_breakdown, data_source_health, executive_summary), computes volume and efficiency metrics, and uses CROSS JOIN and subqueries for json_object_agg aggregations.",
}


def fix_db8(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB8_DESCRIPTIONS and n in DB8_EVIDENCE:
            if q.get("description") != DB8_DESCRIPTIONS[n] or q.get("evidence") != DB8_EVIDENCE[n]:
                q["description"] = DB8_DESCRIPTIONS[n]
                q["evidence"] = DB8_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-9: Shipping Intelligence (shipments, packages, carriers, zones, rates, tracking, customs)
DB9_DESCRIPTIONS = {
    1: "Shipping operations teams need to optimize carrier selection and reduce costs. Historical data from shipments, carriers, and routes captures performance metrics. Operators need rate comparisons to identify the cheapest and fastest options for each shipment scenario.",
    2: "Logistics planning teams need to understand geographic shipping patterns and optimize delivery times across zones. Zone definitions, transit times, and carrier coverage vary by origin-destination pairs. Zone analysis supports route planning and carrier selection.",
    3: "Customer service and operations teams need proactive visibility into shipment status and potential delivery issues. Tracking event data captures every milestone in the delivery lifecycle. Proactive management reduces customer complaints and exception handling.",
    4: "Data quality teams experience delivery failures and returns due to invalid or incomplete shipping addresses. Records include original and validated addresses. Improving address capture accuracy reduces failed deliveries and return costs.",
    5: "Finance and operations leadership need to control rising shipping costs while maintaining service quality. Data captures actual costs, billed amounts, service levels, and performance. Integrated visibility supports carrier negotiation and cost-effective selection.",
    6: "Logistics operations teams manage high-volume shipping and need to optimize preset configurations. Presets define default package dimensions, weights, and carrier/service. Right-sizing presets reduces wasted spend on oversized configurations.",
    7: "International shipping departments face increasing customs duties and taxes on cross-border shipments. Customs data includes declarations, duty assessments, and clearance status. Optimization through tariff classification or routing can reduce duty exposure.",
    8: "Finance teams notice shipping adjustments and billing discrepancies that result in revenue leakage. Adjustment records capture type, amount, reason, and status. Categorizing and detecting patterns supports cost recovery and prevention.",
    9: "Engineering teams support shipping rate APIs that serve real-time quotes to customers and internal systems. API logs capture request metadata, response times, and error rates. Performance monitoring supports reliability and speed improvements.",
    10: "Executive leadership requires a comprehensive view of shipping operations for strategic decisions about carrier partnerships, pricing, and investments. Data across shipments, carriers, routes, and transactions contains the needed metrics.",
    11: "Logistics teams evaluate packaging efficiency to reduce shipping costs. Carriers use dimensional weight pricing; oversized packages incur surcharges. Right-sizing package configurations minimizes dimensional weight charges.",
    12: "Operations teams need to assess shipping zone coverage to identify underserved geographic areas and expansion opportunities. Zone definitions, shipment destinations, and carrier capabilities inform coverage gaps.",
    13: "Finance and procurement teams are concerned about shipping cost fluctuations affecting budget predictability. Historical rate data and actual costs vary by carrier, route, and time. Volatility analysis supports budgeting and negotiation.",
    14: "Logistics managers need to evaluate carrier performance to inform contract renewals and selection. Shipments track actual delivery times; carriers have SLAs; routes have expected transit times. Performance varies across carriers and service types.",
    15: "Supply chain teams seek to optimize shipping routes to balance cost efficiency with delivery speed. Routes table contains paths with costs and transit times; shipments track historical routing. Route alternatives support trade-off analysis.",
    16: "Shipping operations teams need to understand the composition of shipping costs to identify savings. Costs include base rates, fuel surcharges, accessorial fees, and handling charges. Component breakdown supports targeted optimization.",
    17: "Operations teams need to identify unusual tracking event patterns or anomalies that might indicate problems. Tracking events capture status changes, locations, and timestamps. Anomaly detection enables proactive issue resolution.",
    18: "Data quality and operations teams need to assess address validation accuracy and its impact on delivery performance. Validation results compare input to validated addresses. Correction patterns inform capture improvements.",
    19: "International shipping teams need to identify efficient routes considering cost, delivery time, and customs procedures. International shipments involve customs clearance, duties, and country-specific rules. Route optimization supports cost and speed.",
    20: "Shipping operations need a comparison matrix showing how carrier rates vary across package weights, zones, and service levels. Rate tables differ by carrier with complex pricing rules. Matrix supports carrier selection and negotiation.",
    21: "Shipping operations teams need to optimize packaging costs and reduce wasted space. Historical shipment data includes package dimensions, weights, and costs. Dimension optimization identifies right-sizing opportunities.",
    22: "Logistics operations teams experience customer complaints about delivery delays and need to evaluate carrier performance across zones. Shipment timestamps, carrier assignments, and promised delivery dates support transit time analysis.",
    23: "International shipping divisions seek to reduce customs duty expenses for cross-border shipments. Customs data includes tariff codes (HS codes), duty amounts, and product classifications. Tariff optimization can lower duty rates.",
    24: "Engineering teams have implemented API caching to reduce carrier API load and improve response times. Cache effectiveness varies by request type and route. System logs capture cache hit/miss events and response times.",
    25: "Finance and sales teams require accurate revenue forecasts for quarterly planning and investor reporting. Historical revenue is segmented by carrier, service level, customer segment, and region. Market changes make forecasting critical.",
    26: "Logistics managers need to evaluate whether contracted carriers meet industry benchmarks. Shipments, carriers, and routes data contains performance metrics including on-time delivery, damage rates, and cost efficiency.",
    27: "Supply chain analysts are concerned about rising costs due to dimensional weight pricing. Carriers charge based on package volume; many shipments are billed at dimensional weight instead of actual weight, inflating costs.",
    28: "Transportation managers oversee a network of shipping routes connecting distribution centers to customer locations. Routes contain transit times, distances, fuel costs, and capacity. Some routes underperform with longer transit or higher per-mile costs.",
    29: "Shipping operations work with multiple carriers (UPS, FedEx, USPS, regional) each offering different rates by weight, dimensions, zone, and service. Rate tables are stored separately with complex pricing rules. Manual comparison is time-consuming and error-prone.",
    30: "Directors of logistics need a unified view of the entire shipping operation across carriers, routes, and distribution centers. Data is fragmented across tracking systems, carrier performance databases, and cost accounting. Real-time visibility supports operational improvement.",
}

DB9_EVIDENCE = {
    1: "The query constructs five CTEs: package_dimensions (billable weight, DIM divisor 166), zone_lookup (origin-destination zone), carrier_service_options (CROSS JOIN carriers and services), rate_calculations (subquery for MIN rate by weight), rate_rankings (ROW_NUMBER for cheapest/fastest). Output includes rate_rank, speed_rank, cost_difference_from_cheapest, cost_premium_percentage.",
    2: "The query uses WITH RECURSIVE zone_hierarchy to traverse zone relationships, zone_statistics for aggregate transit metrics, carrier_zone_performance for carrier-by-zone analysis, zone_rankings with ROW_NUMBER and PERCENT_RANK. LATERAL join selects best carrier per zone. Output includes speed_category, consistency_category.",
    3: "The query builds six CTEs: tracking_event_sequence (ROW_NUMBER, LAG, LEAD for event order), event_time_intervals (EXTRACT EPOCH for hours between events), shipment_progress_analysis (MAX CASE for milestone timestamps), historical_delivery_patterns (PERCENTILE_CONT for p95), delivery_prediction (CASE for predicted date), anomaly_detection (delay and anomaly flags).",
    4: "The query builds four CTEs: address_validation_comparison (CASE for address_was_corrected and correction_type), validation_statistics (GROUP BY date, COUNT by status), correction_pattern_analysis (GROUP BY correction_type), validation_quality_metrics (success_rate, dpv_rate, invalid_rate). LATERAL join for most_common_correction_type.",
    5: "The query builds five CTEs: shipment_cost_details, daily_cost_summary (GROUP BY date/carrier/service), carrier_performance_metrics (delivery_success_rate, exception_rate), service_performance_metrics, cost_optimization_opportunities (subquery for alternative_min_rate). Uses ROW_NUMBER for revenue_rank, performance_rank, cost_efficiency_rank.",
    6: "The query builds three CTEs: preset_usage_analysis (JOIN bulk_shipping_presets with shipments, AVG actual vs default), preset_cost_analysis (subquery for optimized_rate, potential_savings_per_shipment), preset_recommendations (CASE for optimization_recommendation). ROW_NUMBER for savings_rank.",
    7: "The query builds five CTEs: international_shipment_details (JOIN international_customs, shipments, packages), customs_value_analysis (PERCENTILE_CONT for median, p95), duty_rate_analysis (GROUP BY country, hs_tariff_code), customs_clearance_performance (clearance_success_rate), customs_optimization_opportunities (deviation_from_avg, cost_category).",
    8: "The query builds five CTEs: adjustment_details (JOIN shipping_adjustments, shipments, packages), adjustment_statistics (PERCENTILE_CONT for median, p95), carrier_adjustment_patterns, discrepancy_analysis (CASE for discrepancy_category, impact_level), cost_recovery_opportunities. Note: cost_recovery_opportunities references adjustment_status which is in adjustment_details; JOIN may use discrepancy_analysis.",
    9: "The query builds five CTEs: api_request_details, api_performance_metrics (PERCENTILE_CONT for p50, p95, p99), hourly_performance_patterns, error_pattern_analysis (GROUP BY error_message), optimization_recommendations (CASE for recommendation). LATERAL joins for peak_error_hour and most_common_error.",
    10: "The query builds six CTEs: daily_shipment_summary, revenue_trend_analysis (LAG for previous_day, week_ago, month_ago; AVG OVER ROWS BETWEEN for 7-day and 30-day), carrier_performance_summary, service_performance_summary, revenue_growth_metrics (day_over_day, week_over_week, month_over_month), dashboard_summary (scalar subqueries for top_carrier, top_service).",
    11: "The query builds four CTEs: package_dimension_analysis (dimensional_weight_lbs = L×W×H/166, billable_weight_lbs), dimensional_weight_impact (subqueries for cost_at_actual_weight, cost_at_billable_weight), optimization_opportunities (optimization_category), package_configuration_recommendations (SQRT/POWER for recommended_max_dimension). ROW_NUMBER for optimization_priority_rank.",
    12: "The query uses WITH RECURSIVE zone_coverage_map to expand coverage to adjacent zones, zip_prefix_coverage (GROUP BY origin/destination prefix), coverage_gaps (CASE for coverage_category), carrier_coverage_comparison (STRING_AGG, has_good_coverage, has_no_coverage). Window functions for destination_count_for_origin.",
    13: "The query aggregates shipping costs by carrier and route over time, calculates volatility (STDDEV, coefficient of variation), uses LAG and ROWS BETWEEN for rolling averages and period-over-period changes, identifies seasonal patterns, PERCENTILE_CONT for quartiles. Handles NULL in historical rate data.",
    14: "The query joins shipments with carriers and routes, groups by carrier and service level, calculates delivery time metrics (AVG, PERCENTILE_CONT), computes on-time delivery rates against SLA, uses ROW_NUMBER and window functions for ranking and rolling performance trends.",
    15: "The query evaluates alternative routes between origin-destination pairs, groups shipments by route, calculates total costs and average transit times, cost-per-day metrics, uses window functions for efficiency scores combining cost and time, identifies Pareto-optimal routes, PERCENTILE_CONT for quartiles.",
    16: "The query joins shipment and cost tables, groups by cost component type and carrier, computes aggregate totals and percentages, uses window functions for running totals and period comparisons, PERCENTILE_CONT for quartile analysis. Handles NULL in optional cost fields.",
    17: "The query analyzes tracking event sequences, groups by shipment and carrier, computes event timing and frequency aggregates, uses LAG/LEAD for rolling averages and deviation patterns, identifies anomaly flags based on event gaps or exception counts.",
    18: "The query joins address validation results with shipment outcomes, groups by validation status and correction type, computes success rates and correction impact on delivery, uses window functions for trend analysis. Handles NULL for optional validation fields.",
    19: "The query joins international shipments with customs and route data, groups by origin-destination country pairs, computes cost and transit time aggregates, factors in customs clearance days and duty amounts, uses window functions for route ranking and trade-off analysis.",
    20: "The query builds a matrix by CROSS JOIN or pivoting carrier rate tables across weight brackets, zones, and service levels. Uses PERCENTILE_CONT or similar for rate distributions. Window functions for comparative rankings across dimensions.",
    21: "The query joins shipments with packages, groups by product category and package size range, calculates volume efficiency ratios (product vs package volume), PERCENTILE_CONT for quartiles, window functions to compare against optimal benchmarks. Aggregates potential savings (actual vs projected cost).",
    22: "The query joins shipments with carriers and routes, filters for completed deliveries, groups by shipping zone and carrier, calculates average actual vs expected transit times, variance metrics, window functions for rolling 30-day averages and carrier ranking within zone.",
    23: "The query joins shipment data with customs declarations and tariff code reference tables, groups by product type, tariff code, and destination country, calculates aggregate duty amounts and average duty rates, compares against alternative tariff codes, window functions for product ranking.",
    24: "The query joins API request logs with cache performance metrics and carrier cost data, groups by request type, route popularity, and time windows, calculates cache hit rates and miss rates, window functions for trend analysis and cost savings quantification.",
    25: "The query extracts historical revenue from shipments and billing, groups by month, carrier, service level, customer segment, calculates YoY and MoM growth rates, applies time-series aggregations for seasonal patterns, uses window functions for trend projection and confidence intervals.",
    26: "The query joins shipment data with carrier information and industry benchmark tables, groups by carrier and service type, computes aggregate metrics (avg delivery time, on-time percentage, cost per shipment), PERCENT_RANK for percentile rankings vs industry quartiles. Handles NULL for incomplete data.",
    27: "The query calculates dimensional weight (L×W×H/divisor) per shipment, compares to actual weight, groups by product category and package type, computes cost difference and optimization potential, uses window functions for savings ranking. Identifies shipments charged at DIM weight.",
    28: "The query joins routes with shipment performance data, groups by origin-destination and carrier, computes efficiency scores (transit time, fill rate, per-mile cost), uses window functions for performance ranking and optimization opportunity identification.",
    29: "The query unions or joins rate tables from all carriers, applies carrier-specific pricing logic (base rates, surcharges, volume discounts), uses window functions (MIN, ROW_NUMBER) to identify best rate per shipment scenario while considering service level requirements.",
    30: "The query builds multiple CTEs (base_data, aggregated_metrics, performance_analysis, optimization_recommendations) joining shipments, packages, carriers, service types. Computes total_revenue, delivery_success_rate, ROW_NUMBER for revenue_rank and cost_rank, CASE for performance_category. Consolidates key metrics into single result set.",
}

# db-10: Marketing Intelligence (retail pricing, inventory, products, product_pricing, retailers, stores)
# All 30 queries share the same 5-CTE structure: base_analysis, aggregated_metrics, temporal_analysis, trend_calculations, market_intelligence, final_analysis
DB10_EVIDENCE = "The query builds five CTEs. base_analysis joins products, product_pricing, retailers, stores, and product_inventory. aggregated_metrics groups by category, subcategory, brand, price_month and computes product/retailer/store counts, avg/median/min/max price, stddev, and in_stock/out_of_stock counts. temporal_analysis uses LAG and LEAD for prev/next month prices, a 12-month moving average (ROWS BETWEEN 11 PRECEDING), and price_volatility_12m. trend_calculations adds mom_price_change (percent) and availability_rate. market_intelligence derives price_trend (strong_increase, moderate_increase, stable, moderate_decrease, strong_decrease), availability_classification, price_rank (ROW_NUMBER), and price_percentile (PERCENT_RANK). final_analysis rounds and selects output columns."

DB10_DESCRIPTIONS = {
    1: "Pricing analysts monitor competitive pricing across retailers and regions to inform strategy. Product prices vary by store and time; category and brand breakdowns support positioning decisions.",
    2: "Supply chain teams anticipate stockouts and optimize inventory allocation. Inventory and pricing data by product, retailer, and store support restocking and geographic distribution analysis.",
    3: "Market intelligence teams assess retailer performance relative to competitors across product categories. Share and ranking metrics by category and time support competitive positioning.",
    4: "Consumer insights teams identify deals and promotional opportunities across retailers. Price drops and temporal patterns drive purchase decisions and alert triggers.",
    5: "Merchandising and planning teams optimize inventory buying and promotional calendars. Category trends, seasonal patterns, and demand forecasts support buying decisions.",
    6: "Marketing teams evaluate effectiveness across segments and time periods. Aggregated metrics by category, brand, and month support campaign and budget decisions.",
    7: "Marketing leadership needs segment behavior and ROI insights for budget allocation. Channel, segment, and quarter breakdowns support optimization.",
    8: "Digital marketing divisions demonstrate campaign performance across channels. Comparative statistics and trends support quarterly business reviews.",
    9: "Marketing analytics teams deliver segment profitability and campaign efficiency insights. Holistic views by segment and time support annual planning.",
    10: "Senior management assesses channel effectiveness for budget reallocation. Multi-dimensional performance metrics guide investment decisions.",
    11: "Marketing teams evaluate campaign effectiveness across channels and segments. Performance metrics with statistical breakdowns support optimization.",
    12: "Marketing operations needs cross-channel performance visibility for acquisition cost optimization. Segment and campaign aggregations with trend analysis support decisions.",
    13: "CMOs present quarterly marketing performance to the board. Integrated campaign and segment views support executive reporting.",
    14: "Marketing analytics teams deliver weekly performance reviews to campaign managers. Granular tactic insights identify underperformers and successes.",
    15: "Leadership conducts annual planning and assesses channel effectiveness and segment profitability. Data-driven assessment supports strategic decisions.",
    16: "Marketing intelligence teams manage campaign performance across channels. Comparative and trend-based metrics support optimization.",
    17: "Marketing operations tracks campaign performance across digital and traditional channels. Multi-table data supports comprehensive analysis.",
    18: "Marketing teams need cross-segment and cross-channel performance visibility. Aggregated metrics with trend indicators support budget and tactic decisions.",
    19: "Marketing analytics teams identify high-value segments and underperforming channels. Segmentation analysis informs fiscal year strategy.",
    20: "Marketing leadership requires customer acquisition cost and lifetime value visibility across segments. Budget allocation optimization depends on segment-level metrics.",
    21: "Marketing teams evaluate campaign effectiveness across segments and channels. Comprehensive metrics support optimization decisions.",
    22: "Marketing leadership requires acquisition cost and lifetime value visibility across segments. Segment-level metrics support budget allocation.",
    23: "Digital marketing teams assess campaign performance against KPIs for quarterly reviews. Benchmark and historical comparisons support evaluation.",
    24: "Analytics teams identify high-value segments and underperforming channels for fiscal strategy. Segmentation analysis guides investment.",
    25: "Executive leadership requires holistic marketing effectiveness view for strategic planning. Investment returns and improvement opportunities inform decisions.",
    26: "Marketing intelligence teams maintain campaign and metrics data for effectiveness evaluation. Comprehensive reports support ROI analysis.",
    27: "Marketing intelligence divisions store campaign, CTR, conversion, and segment data for decision making. Multi-dimensional KPIs support analysis.",
    28: "Marketing analytics platforms aggregate multi-channel campaign data with metrics and segments. Trend analysis and comparative indicators support evaluation.",
    29: "Marketing operations teams manage campaign, metric, and segment data for effectiveness tracking. Standardized reports support portfolio health monitoring.",
    30: "Marketing intelligence functions maintain integrated campaign, metric, and segment datasets across channels. Multi-dimensional aggregations and trend indicators support analysis.",
}


def fix_db9(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB9_DESCRIPTIONS and n in DB9_EVIDENCE:
            if q.get("description") != DB9_DESCRIPTIONS[n] or q.get("evidence") != DB9_EVIDENCE[n]:
                q["description"] = DB9_DESCRIPTIONS[n]
                q["evidence"] = DB9_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def fix_db10(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB10_DESCRIPTIONS:
            new_desc = DB10_DESCRIPTIONS[n]
            if q.get("description") != new_desc or q.get("evidence") != DB10_EVIDENCE:
                q["description"] = new_desc
                q["evidence"] = DB10_EVIDENCE
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-11: Parking intelligence (parking_utilization, parking_facilities, cities, traffic_volume_data, events, airports)
DB11_DESCRIPTIONS = {
    1: "Parking intelligence platforms track utilization and occupancy across metropolitan areas. Management needs to identify high-potential markets for facility expansion and understand demand patterns geographically and temporally.",
    2: "Parking operations compete with multiple facilities in each geographic cluster. Teams need to understand competitive positioning to optimize pricing and maximize revenue.",
    3: "Major events like concerts, sports games, and conferences create significant parking demand spikes that require proactive capacity and pricing management.",
    4: "Airport parking facilities experience highly seasonal demand correlated with passenger flight volumes, holidays, and travel patterns. Utilization data tracks short-term, long-term, and economy lots.",
    5: "Urban traffic volume serves as a leading indicator of parking demand. Understanding this relationship enables strategic facility placement and demand forecasting.",
    6: "Parking operations teams need to optimize pricing strategies across demographic segments to increase revenue while maintaining competitive market penetration.",
    7: "Business development teams require a comprehensive understanding of distinct market segments to allocate resources effectively and maximize revenue across customer clusters.",
    8: "Operations teams experience unpredictable parking capacity issues, with some lots consistently overutilized while others remain underused.",
    9: "Strategic planning teams evaluate potential geographic markets for expansion and need a systematic framework to assess opportunity size, competitive dynamics, and risks.",
    10: "Finance teams require accurate revenue forecasts for budgeting and resource planning. Historical parking revenue data shows seasonal patterns and trends that need systematic modeling.",
    11: "Parking management companies operate multiple lots across the city and need to understand competitive position relative to other providers in overlapping zones.",
    12: "Business districts experience varying parking demand throughout the week, influenced by office schedules, retail activity, and entertainment venues.",
    13: "Parking businesses offer monthly subscription passes and transient options. Understanding customer lifetime value and retention patterns is essential for resource allocation and marketing optimization.",
    14: "Electric vehicle adoption is accelerating. Parking lots with EV charging capabilities are experiencing increased demand.",
    15: "Parking lots accept both advance reservations and walk-in customers. Reserved spaces guarantee revenue but may leave capacity unused; walk-ins provide flexibility but introduce revenue uncertainty.",
    16: "Parking management systems need to optimize revenue during high-demand periods while preventing capacity bottlenecks. Historical data contains timestamped entry/exit records and lot capacities.",
    17: "Operations teams need to correlate parking demand with temporal patterns (hour of day, day of week) for shift planning and operational scheduling.",
    18: "Capacity planners need to identify which lots are undersupplied relative to demand and prioritize facility expansion.",
    19: "Marketing teams segment customers by behavioral patterns (visit frequency, duration, payment method) for personalized engagement and dynamic pricing.",
    20: "Revenue managers need to understand price elasticity—how demand responds to price changes—to set optimal rates across lots, zones, and time periods.",
    21: "Parking intelligence operates across multiple MSAs. Teams need to evaluate regional performance to identify high-potential markets for expansion.",
    22: "Operations experience fluctuating demand patterns influenced by seasonal factors such as holidays, weather, and local events. Time-series forecasting supports operational planning.",
    23: "Platforms monitor thousands of parking events daily. Anomalous patterns (unexpected occupancy spikes, duration outliers, irregular revenue) may indicate operational issues, fraud, or emerging demand shifts.",
    24: "Parking businesses serve diverse customers with varying behaviors, frequency patterns, duration preferences, and price sensitivities. Behavioral segmentation supports personalized marketing and dynamic pricing.",
    25: "Dynamic pricing strategies balance demand and maximize revenue. Understanding price elasticity—how demand responds to price changes—is critical for setting optimal rates.",
    26: "Operations teams experience frequent capacity issues and need to identify which lots are undersupplied relative to demand.",
    27: "Business development teams plan geographic expansion and need to understand current market penetration rates across existing zones.",
    28: "Finance and operations teams need to maximize return on facility assets by understanding which locations generate the most revenue relative to physical footprint.",
    29: "Executive leadership requires a unified view of parking operations performance across customer, financial, operational, and market dimensions for strategic decision-making.",
    30: "Data engineering teams have noticed increasing query latency as data volumes have grown. Complex analytical queries joining parking_events with lots and zones are experiencing performance degradation.",
}

DB11_EVIDENCE = {
    1: "The query constructs CTEs: city_demographic_cohorts (cities + MSA), parking_facility_aggregations, utilization_metrics, city_utilization_aggregations, traffic_correlation_analysis, market_demand_scoring (weighted demand and growth scores), ranked_markets (ROW_NUMBER, PERCENT_RANK, LAG, LEAD, AVG, STDDEV). Output includes demand_score, growth_potential_score, expansion_priority, market_tier.",
    2: "The query uses facility_location_clusters (ST_Distance for nearby facilities), pricing_analysis (ROW_NUMBER for recency), competitive_clusters (ARRAY_AGG, FILTER, ST_Distance < 500m), utilization_by_facility, market_share_calculation, pricing_optimization_recommendations. Output includes recommended_rate, estimated_revenue_impact, competitive_advantage_score.",
    3: "The query builds upcoming_events, historical_event_patterns (AVG, PERCENTILE_CONT by event_type/day/hour), venue_parking_analysis (ST_Distance, nearby facilities), event_demand_forecast, demand_supply_analysis, pricing_recommendations. Output includes forecasted_parking_demand, supply_status, recommended_event_rate.",
    4: "The query joins airport_passenger_volumes, airport_parking_facilities, monthly_utilization_patterns, seasonal_pattern_analysis (seasonal_multiplier), passenger_correlation_analysis, revenue_optimization. Uses PERCENTILE_CONT, AVG, CASE for seasonal pricing. Output includes recommended_seasonal_rate, season_category.",
    5: "The query uses traffic_monitoring_locations (ST_MakePoint), nearby_parking_facilities (ST_Distance < 500m), hourly_utilization_by_facility, traffic_parking_correlation (correlation coefficient formula), demand_forecasting_model. Output includes correlation_coefficient, forecasted_occupancy_rate.",
    6: "The query builds demographic_segments (income, age, employment CASE), facility_pricing_by_city, utilization_by_demographic, demographic_correlation (revenue_per_capita, price_sensitivity_index), segment_optimization. Output includes recommended_hourly_rate, market_penetration_score.",
    7: "The query uses city_characteristics, utilization_metrics, normalized_characteristics (MIN/MAX OVER for 0-1 scale), segment_assignment (CASE for Premium Urban, Urban Professional, etc.), segment_profiles, segment_optimization. ROW_NUMBER for segment_rank. Output includes revenue_potential_score, recommended_segment_rate.",
    8: "The query builds hourly_utilization_base, temporal_aggregations (AVG, PERCENTILE_CONT, STDDEV by facility/hour/dow/month), moving_averages (ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING), seasonal_decomposition (trend, seasonal, residual), anomaly_detection (ABS(residual) > 2*stddev). Output includes is_anomaly, anomaly_type, trend_direction.",
    9: "The query aggregates parking_events by geographic dimensions (zones, lots, regions), joins with lots and zones, calculates market size (transaction volume, revenue density, growth rates). Window functions rank by opportunity score, compute risk factors (revenue volatility). Output includes expansion targets and risk assessment.",
    10: "The query aggregates historical revenue by time period (daily, weekly, monthly). Uses window functions for moving averages, exponential smoothing, year-over-year comparisons. Calculates standard errors and confidence intervals from historical variance. Output includes revenue forecasts with confidence bounds.",
    11: "The query joins parking_events with lots and zones, aggregates utilization by provider and zone. Computes market share percentages via window functions, rolling 3-month averages, quartile analysis. COALESCE for NULL zone assignments. Output includes market share, competitive recommendations.",
    12: "The query segments parking_events by business district zones. Groups by hour and day for demand patterns. Uses window functions for moving averages, RANK(), PERCENT_RANK(). Correlates occupancy with zone characteristics (commercial, retail, mixed-use). Output includes peak demand periods, dynamic pricing opportunities.",
    13: "The query aggregates parking_events by customer and month. Uses PARTITION BY customer_id for retention cohorts, LAG/LEAD for tenure, cumulative revenue for CLV. Output includes churn risk factors, retention metrics.",
    14: "The query filters parking_events to EV charging spots, joins with lots. Calculates utilization rates, revenue per charging space. Window functions for month-over-month growth, rolling averages. Projects future demand. Output includes expansion recommendations.",
    15: "The query segments parking_events by reservation status (pre-booked vs walk-in). Joins with lots and zones. Calculates revenue per type, average duration, no-show rates. Window functions for expected vs actual. Output includes optimal reservation allocation.",
    16: "The query segments parking_events by hour and day of week. Joins with lots and zones. Window functions for rolling 3-hour average occupancy. Computes occupancy quartiles, actual vs capacity ratios. Flags hours exceeding 85% for premium pricing. Output includes peak period identification.",
    17: "The query extracts hour and day-of-week for temporal context. Groups by period and facility. Uses window functions (rolling avg, cumulative sum, LAG, LEAD). Output includes temporal correlation metrics.",
    18: "The query joins parking_events with lots and zones, aggregates demand by facility and time period. Computes occupancy rates, peak utilization. Window functions for rolling average trends, quartile analysis. Output includes supply-demand gaps, expansion prioritization.",
    19: "The query groups parking_events by customer. Computes total visits, average duration, preferred time windows, day-of-week patterns, total spend. Uses NTILE or quartile functions for behavioral classification. Output includes segment profiles.",
    20: "The query joins parking_events with lots and zones. Groups by lot, zone, time period, price tier. Computes demand at different price levels. Window functions for percentage change in price and demand. Output includes elasticity estimates, revenue impact.",
    21: "The query joins parking_events with lots and zones by MSA. Groups by MSA. Computes total events, avg occupancy, revenue, utilization quartiles. Window functions for rolling averages, trending markets. Output includes regional performance rankings.",
    22: "The query extracts timestamps, groups by hour/day/week/month. Uses ROWS BETWEEN for moving averages. Identifies seasonal components by day-of-week, month, hour. Decomposes into seasonal, trend, residual. Output includes time-series forecast components.",
    23: "The query aggregates by lot, zone, time period. Computes mean, stddev, quartile boundaries. Window functions for rolling 7-day and 30-day statistics. Flags values exceeding 2 std dev. Output includes anomaly flags, baseline metrics.",
    24: "The query groups parking_events by customer. Computes visits, duration, time windows, day-of-week patterns, spend, avg transaction value. Uses NTILE or quartile for classification. Output includes behavioral segment profiles.",
    25: "The query joins parking_events with lots and zones. Groups by lot, zone, time period, price tier. Computes demand metrics at different price levels. Window functions for percentage change in price and demand. Output includes elasticity and revenue impact.",
    26: "The query joins parking_events with lots and zones. Aggregates demand by facility and time period. Computes occupancy rates, peak utilization, unfulfilled demand. Window functions for rolling averages, quartile analysis. Output includes supply-demand gaps, expansion prioritization.",
    27: "The query aggregates parking_events by zone geography. Computes unique users, event volumes. Groups by zone and time. Uses LAG for growth rates. Calculates market share percentage. Rolling averages, quartile rankings. COALESCE for NULL. Output includes penetration rates, growth trajectories.",
    28: "The query joins parking_events revenue with lots facility dimensions. Groups by lot. Sums revenue, divides by square footage. Window functions for percentile rankings, comparative metrics. Output includes revenue per square foot, bottom-quartile identification.",
    29: "The query uses multiple CTEs for dimensional metrics: customer (unique users, visit frequency, retention), revenue (transactions, growth rates), operational (occupancy, turnover), geographic (zones, market coverage). Window functions for rankings. Output includes integrated dashboard metrics.",
    30: "The query examines execution patterns by grouping parking_events by time periods. Computes row counts, join cardinalities, aggregation complexity. Window functions for response time trends. CTEs for table scan costs, join efficiency. Output includes optimization recommendations.",
}


def fix_db11(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB11_DESCRIPTIONS and n in DB11_EVIDENCE:
            if q.get("description") != DB11_DESCRIPTIONS[n] or q.get("evidence") != DB11_EVIDENCE[n]:
                q["description"] = DB11_DESCRIPTIONS[n]
                q["evidence"] = DB11_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-12: Credit card and rewards optimization (credit_cards, transactions, rewards, CFPB, offers)
DB12_DESCRIPTIONS = {
    1: "A credit card user maintains multiple cards with varying reward structures across different merchants and spending categories. They want to understand whether they are maximizing their rewards or leaving money on the table by using suboptimal cards for specific purchases.",
    2: "A credit card user is planning shopping trips or evaluating spending opportunities in their geographic area. They want to know which nearby merchants offer the best rewards potential when paired with their existing credit cards, and whether there are location-specific offers they should activate.",
    3: "Credit card issuers frequently provide targeted offers such as cash back bonuses, statement credits, or elevated rewards at specific merchants. A user with multiple credit cards needs to track which offers are available across their portfolio, determine eligibility based on card type and account status, and prioritize which offers to activate to maximize savings given their typical spending patterns.",
    4: "Credit card users want to make informed decisions not just based on rewards and fees, but also on issuer reliability and customer service quality. The Consumer Financial Protection Bureau (CFPB) maintains a public database of consumer complaints against financial institutions. By analyzing complaint patterns, volumes, response quality, and trends, users can assess issuer risk and avoid cards from banks with poor customer service track records or increasing complaint trajectories.",
    5: "The Federal Reserve publishes aggregate consumer credit data including revolving credit balances, delinquency rates, charge-off rates, and credit utilization across different consumer segments and time periods. Analyzing this macroeconomic data helps credit card users, financial advisors, and industry analysts understand broader market trends, identify how different demographic segments are managing credit, and anticipate economic conditions that affect credit availability and pricing.",
    6: "Credit card enthusiasts managing multiple card applications need to track their eligibility under Chase's 5/24 rule, which denies applications to consumers who have opened 5 or more credit cards across all issuers in the past 24 months. Understanding application timing and eligibility windows is critical for optimizing approval success rates.",
    7: "Credit card holders with multiple premium cards face significant annual fee burdens that may not be justified by the rewards and benefits earned. Evaluating whether each card's annual fee is offset by its value generation is essential for portfolio optimization and renewal decisions.",
    8: "New credit card signups typically offer lucrative signup bonuses contingent on meeting minimum spend requirements within specified timeframes (usually 3-6 months). Cardholders managing multiple new cards need to track spend progress against these requirements to ensure bonus capture while optimizing spending allocation across cards.",
    9: "Credit card users want to maximize rewards by using the optimal card for each merchant based on category bonuses, promotional rates, and spending patterns.",
    10: "Several credit cards offer rotating quarterly bonus categories (e.g., 5% cash back on up to $1,500 in combined purchases in categories that change each quarter after activation). Cardholders need to track which categories are active each quarter across multiple cards, analyze their spending patterns by category, and strategically allocate spending to maximize bonus earnings while staying within quarterly caps.",
    11: "The finance team is reviewing quarterly credit card expenses to identify cost reduction opportunities.",
    12: "The consumer credit team manages a diverse portfolio of credit card products and needs to assess whether customers are appropriately diversified across card types (cash back, travel rewards, business cards) or over-concentrated in specific products. This analysis helps evaluate portfolio risk, identify underutilized card products, and inform marketing strategies for card acquisition.",
    13: "As international spending increases among cardholders, foreign transaction fees (typically 1-3% per transaction) have become a significant cost. The operations team needs to identify which cards and customers are incurring the highest foreign transaction fees and evaluate whether switching to no-foreign-fee cards or adjusting travel card usage could generate meaningful savings.",
    14: "Many premium credit cards charge annual fees for authorized users (additional cardholders on an account), ranging from $0 to $175+ per user.",
    15: "Credit utilization (the percentage of available credit being used) is a critical metric that affects credit scores and borrowing costs. The credit risk team needs to monitor utilization across the portfolio to identify customers using too much of their available credit (high utilization hurts credit scores and indicates potential default risk) or too little (underutilized credit represents opportunity costs).",
    16: "The rewards program manager needs to understand how cardholders are utilizing their accumulated points across various redemption channels (cash back, travel, gift cards, statement credits) to optimize reward offerings and identify which redemption options drive the most engagement.",
    17: "The partnerships team manages relationships with airline, hotel, and retail transfer partners where cardholders can convert reward points at various exchange rates, and needs visibility into which partnerships deliver the most value and customer engagement to inform contract renewals and identify underperforming partners.",
    18: "The customer retention and growth team wants to proactively identify cardholders whose spending behavior suggests they would derive more value from a different card tier—either upgrading high-spenders to premium cards with better rewards but higher fees, or downgrading low-utilization customers to no-fee cards to reduce churn—while maximizing customer lifetime value and satisfaction.",
    19: "The credit risk and customer service teams need real-time visibility into how cardholders are utilizing their available credit limits across different time periods (daily, monthly, billing cycle) to identify potential overextension or underutilization.",
    20: "Many customers maintain multiple card products (primary, authorized users, business cards, household members) that should be viewed holistically for relationship management, and the account management team needs a unified view of household-level spending and rewards.",
    21: "The credit card marketing team needs to monitor offer lifecycles to ensure timely renewals and prevent gaps in promotional campaigns.",
    22: "The rewards operations team is reviewing the financial impact of statement credit redemptions as customers increasingly prefer cash-back style rewards over points or miles.",
    23: "The product management team is evaluating the portfolio's card network distribution as processing fees and acceptance rates vary significantly across networks.",
    24: "The product development team is debating whether to expand the metal card lineup given the significantly higher manufacturing costs ($15-20 per metal card vs $1-2 for plastic).",
    25: "The business card division is underperforming compared to consumer cards, with lower activation rates and spend velocity.",
    26: "The credit card operations team needs to evaluate the secured card program's effectiveness in helping customers build credit and transition to standard credit products.",
    27: "The customer success team wants to help cardholders understand how their credit card behavior affects their creditworthiness. Many customers don't realize that high utilization rates or missed payments can significantly impact credit scores.",
    28: "The rewards program manager has identified that millions of points expire unused each quarter, representing both lost customer value and missed engagement opportunities. Customers often don't realize their points have expiration dates until it's too late.",
    29: "The product management team is reviewing the credit card portfolio to ensure competitive positioning and clear differentiation between card tiers (standard, gold, platinum, secured). With 15+ card products, a structured comparison of key terms and benefits is needed.",
    30: "Executive leadership needs a single, comprehensive metric to assess the overall health of the credit card business across multiple dimensions including credit risk, customer engagement, profitability, and operational efficiency.",
}

DB12_EVIDENCE = {
    1: "The query joins transaction, card, and rewards data to match spending patterns with reward structures. It groups by category and merchant to identify optimal cards, computes aggregate reward amounts and lost opportunity costs, uses window functions to rank cards by savings potential within each category.",
    2: "The query performs geospatial joins to identify merchants within a specified radius, calculates distances using latitude/longitude coordinates, matches merchants with card reward rates and category bonuses, aggregates expected rewards based on historical or projected spend, and ranks by reward potential.",
    3: "The query joins card accounts with available offers using eligibility criteria such as card product type and account status, filters by activation windows, aggregates transaction spend by offer category, computes remaining spend to threshold, and uses window functions to rank offers by estimated value.",
    4: "The query aggregates CFPB complaint data by issuer and time period, computes complaint counts and resolution rates, uses window functions for rolling trends and year-over-year comparison, calculates risk scores from frequency and severity, and joins with card data for issuer-level recommendations.",
    5: "The query aggregates consumer credit data by segment and time period, computes delinquency and charge-off rates, uses window functions for seasonal decomposition and trend analysis, calculates utilization bands, and applies statistical methods for predictive indicators.",
    6: "The query calculates rolling 24-month application counts using window functions partitioned by applicant, filters applications by date ranges to determine current eligibility status, identifies gaps in application history to recommend optimal timing windows, computes days until eligibility restoration, and aggregates Chase-specific application patterns.",
    7: "The query aggregates annual fees by card and year, sums all rewards earned and redeemed per card using joins to rewards tables, calculates monetary value of benefits utilized (lounge access, credits, insurance), computes net value as total rewards plus benefits minus annual fees, uses window functions to compare year-over-year value trends, and calculates break-even spending thresholds.",
    8: "The query joins card opening dates with bonus terms to identify active bonus periods, aggregates transaction spending by card since opening date to calculate progress toward minimum spend, computes remaining spend needed and days until deadline, and uses window functions for prioritization.",
    9: "The query aggregates historical transactions by merchant to calculate total spending and frequency, joins merchant data with category mappings to identify applicable bonus categories, calculates effective reward rates per card-merchant pair accounting for base rates and category bonuses, uses window functions for predictive scores and rankings.",
    10: "The query retrieves quarterly bonus category schedules for all applicable cards, aggregates historical transactions by category and quarter to identify spending patterns, computes spend against quarterly caps, and uses window functions to prioritize category activation.",
    11: "The query joins the transactions table with cards and calculates aggregate metrics (total spend, transaction count, average transaction amount) grouped by spending category. It computes quartile distributions to identify outlier categories, applies window functions to calculate each category's percentage of total spend, and ranks categories by spend volume.",
    12: "The query groups cards by card type, issuer, and status (active/inactive), computing counts and percentages for each segment. It uses window functions to calculate concentration ratios (percentage of portfolio in each card type) and comparative metrics such as average credit limits and utilization rates across card categories. CTEs separate active and total card populations.",
    13: "The query filters transactions for foreign purchases (where transaction country differs from card country or currency conversion occurred), joins with the cards table to retrieve foreign transaction fee rates, and calculates total fees paid by card, by customer, and by merchant category. Window functions compute rolling 12-month fee totals and compare against hypothetical zero-fee scenarios.",
    14: "The query joins the cards table with transaction data, grouping by primary cardholder and authorized user status. It calculates total authorized user fees paid annually, counts the number of authorized users per account, aggregates transaction activity (count and volume) attributed to each authorized user, and uses window functions to compute cost-per-transaction and compare spending activity.",
    15: "The query joins cards with current balance information, calculating utilization rate (current balance divided by credit limit) for each card. It groups accounts by utilization bands (0-10%, 10-30%, 30-50%, 50-100%, over 100%) and uses window functions to calculate rolling average utilization over 3, 6, and 12 months to identify trends.",
    16: "The query joins the rewards and transactions tables to link redemptions with earning patterns, groups by redemption type and time period (monthly or quarterly), calculates aggregate metrics including total points redeemed and dollar values, computes conversion rates and percentile distributions using window functions, and applies rolling averages to detect seasonal trends.",
    17: "The query joins rewards data with partner transfer tables and card profiles, groups by partner name and transfer destination category, computes total points transferred and number of unique customers using each partner, calculates average transfer amounts and effective exchange rates using aggregate functions, and employs window functions to rank partners by popularity and compare quarter-over-quarter growth.",
    18: "The query joins transactions, cards, and rewards tables to build comprehensive customer profiles, calculates total annual spending by category and rewards earned per customer, compares current annual fees against reward value generated, groups cardholders by current card tier, and uses window functions to compute spending percentiles within each tier for upgrade/downgrade recommendations.",
    19: "The query aggregates transaction amounts from the transactions table grouped by card and time period, joins with card limit information from the cards table, calculates running totals using window functions to track cumulative spending within billing cycles, and computes utilization percentages and remaining available credit.",
    20: "The query joins multiple tables including customer profiles, card accounts, transactions, and rewards using hierarchical relationships (primary account holder, authorized users, household links), groups transactions and rewards by customer profile while maintaining card-level detail through CTEs or subqueries, and calculates aggregate household metrics.",
    21: "The query joins the offers table with cards and transactions data, filters for active offers, groups by offer ID and expiration date, calculates days until expiration using date functions, counts associated active cards per offer, and ranks offers by urgency using window functions ordered by expiration date.",
    22: "The query joins the rewards table with transactions and cards tables, filters for redemption type equal to statement credit, groups by card type, customer segment, and time period (monthly), computes aggregate metrics including total credits issued and average credit amount, and calculates month-over-month growth rates using LAG window functions.",
    23: "The query joins cards, transactions, and network fee tables, groups by card network and merchant category, calculates total transaction volume and count per network, computes average processing fees and acceptance decline rates, determines market share percentage using SUM window functions, and ranks networks by performance.",
    24: "The query segments cards by material type (metal vs plastic) using a CASE statement, joins with transactions and customer tables, groups by card material and card product, calculates average monthly spend per card, annual fee revenue, retention rate after year one, and customer lifetime value using a CLV formula with discount rate. Window functions support comparative rankings.",
    25: "The query filters for business card types, joins cards with transactions and business customer profile tables, groups by card product, business size (revenue bands), and merchant category, calculates total spend and average transaction size per category, computes credit utilization percentage, and determines rewards earned and redemption rates.",
    26: "The query joins card account data with customer profiles and card type transitions, filters for secured card originations, calculates time-to-graduation using date differences, computes graduation rates by grouping on customer segment and original card type, and uses window functions to track progression milestones.",
    27: "The query joins credit score snapshots with transaction and payment history tables, calculates utilization rates as balance divided by credit limit by month, segments customers into utilization bands (low, medium, high), uses window functions to compute score changes over 3, 6, and 12-month periods, and groups by utilization band and payment status.",
    28: "The query filters the rewards table for points with expiration dates in future windows, groups by customer ID and expiration date, sums points by expiration bucket (30/60/90 days), joins with customer profile to get contact information and tier status, calculates total point value at risk using redemption rates, and uses window functions for prioritization.",
    29: "The query selects from the card agreements table, pivots key terms (APR, annual fee, balance transfer fee, rewards rate, credit limit ranges) by product name, joins with features table to append benefits like travel insurance or concierge service, groups by card product type and tier, and calculates average APRs and fee ranges.",
    30: "The query constructs a multi-layered calculation using CTEs: first CTE computes credit metrics (delinquency rate, charge-off rate, utilization), second CTE computes engagement metrics (transaction volume, redemption rates), third CTE computes profitability metrics, and final SELECT combines dimensions with window functions for weighted composite scoring.",
}


def fix_db12(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB12_DESCRIPTIONS and n in DB12_EVIDENCE:
            if q.get("description") != DB12_DESCRIPTIONS[n] or q.get("evidence") != DB12_EVIDENCE[n]:
                q["description"] = DB12_DESCRIPTIONS[n]
                q["evidence"] = DB12_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-13: AI Benchmark Marketing (ai_models, model_performance_metrics, benchmark_evaluations)
DB13_DESCRIPTIONS = {
    1: "AI product managers need to understand which models lead in intelligence, speed, and price-performance. The AI Benchmark Marketing database contains benchmark results across multiple dimensions for competitive positioning.",
    2: "Pricing strategists need to understand how pricing decisions correlate with market outcomes. The database tracks historical pricing and market performance metrics including adoption rates and market share.",
    3: "Research analysts compare performance patterns across model families (GPT, Claude, Llama) to identify strengths and weaknesses. The benchmark database contains evaluation results across reasoning, coding, and language understanding.",
    4: "Compliance officers must ensure models meet government-mandated benchmark standards across jurisdictions. The database contains results from government-specified evaluation frameworks including safety and transparency scores.",
    5: "Market intelligence analysts forecast which newly released models will achieve strong adoption. Historical data shows performance characteristics correlate with adoption success; forecasting informs investment and partnership decisions.",
    6: "The AI marketing team needs to understand how models evolve through their performance lifecycle to identify improvement, stagnation, or decline patterns and inform strategic investment decisions.",
    7: "Product managers need visibility into how their models' market positions shift relative to competitors to inform marketing spend, feature prioritization, and competitive positioning strategies.",
    8: "Research teams need to understand which benchmark performances are correlated across the model ecosystem to identify redundant metrics, discover underlying factors, and optimize benchmark selection.",
    9: "The revenue operations team needs to understand how pricing decisions affect revenue generation and market adoption to optimize pricing tiers, identify revenue leakage, and maximize profitability.",
    10: "The AI research team needs to rigorously compare performance across model families with statistically sound evidence to validate architectural choices, support marketing claims, and guide development priorities.",
    11: "Stakeholders need visibility into how benchmark results and model performance align with regulatory requirements. The compliance team requires a scorecard to assess regulatory risk across models.",
    12: "The marketing team needs to forecast which models will gain market adoption based on benchmark performance. Correlation between performance metrics and adoption patterns informs go-to-market strategy.",
    13: "Customers and internal teams need a clear view of how AI models rank across benchmarks. A dynamic leaderboard with performance tiers helps users quickly identify top performers and compare capabilities.",
    14: "Customers making purchasing decisions need to understand the value proposition of different models by comparing performance capabilities against pricing for ROI assessment.",
    15: "Decision-makers need to compare models across multiple performance dimensions simultaneously. Weighted composite scoring across accuracy, latency, throughput, and cost-efficiency supports holistic evaluation.",
    16: "AI product managers need to understand performance trajectories across benchmarks to predict future outcomes and plan resource allocation.",
    17: "AI products compete in a crowded marketplace where benchmark performance influences adoption. Competitive intelligence on market-wide performance and positioning drives strategy.",
    18: "As the benchmark suite expands and influences business decisions, evaluation quality and statistical validity must be ensured through integrity assessment.",
    19: "AI models progress through an adoption funnel from benchmark evaluation to production deployment. Conversion rates between stages and drop-off identification support funnel optimization.",
    20: "Product and engineering teams need clear, data-driven improvement recommendations. Models show varying performance across benchmarks; gap analysis identifies shortfalls versus targets and competitors.",
    21: "The AI Benchmark Marketing team needs to understand how pricing changes affect demand. Historical pricing and usage data reveal elasticity patterns critical for pricing strategy and revenue forecasting.",
    22: "AI model developers and customers need to assess whether models perform consistently across benchmark tests or show significant variance. Consistency patterns validate reliability and guide benchmark selection.",
    23: "The AI development organization tracks models through lifecycle stages from experimental to production. Performance evolution across stages enables resource allocation and release decisions.",
    24: "Marketing and strategy teams need visibility into competitive positioning. Performance data from multiple providers enables market share analysis and competitive trend identification.",
    25: "The benchmark governance team must assess statistical reliability and reproducibility of evaluations. Multiple runs may yield varying results; quantifying reliability with confidence intervals is essential for credibility.",
    26: "The AI operations team monitors models across benchmarks and needs to identify which models behave abnormally compared to peers or historical baselines for anomaly investigation.",
    27: "Marketing and business development teams need to understand platform performance across markets. Customer data and adoption metrics span regions and segments; penetration insights reveal growth opportunities.",
    28: "The engineering team plans optimization initiatives and needs to prioritize improvements that deliver the highest performance gains relative to development effort and resource costs.",
    29: "The AI governance committee conducts quarterly model reviews. A holistic evaluation framework beyond single metrics provides multi-dimensional scoring across technical performance, efficiency, and business value.",
    30: "Customer success and solutions architecture teams recommend appropriate models for diverse use cases. Each use case has unique requirements; a systematic framework for matching models to requirements is needed.",
}

DB13_EVIDENCE = {
    1: "The query joins benchmark, model, and metric tables, groups results by model and benchmark category, computes aggregate statistics including mean intelligence scores and percentile rankings, applies window functions to calculate competitive positioning metrics and quartile distributions for price-performance.",
    2: "The query performs time-series analysis by grouping models by release date and family, uses window functions with LAG to calculate period-over-period price changes and percentage deltas, computes rolling 3-month and 6-month average prices, joins with market share and adoption metrics tables.",
    3: "The query joins model metadata with benchmark results, groups by model family and benchmark category, computes aggregate statistics including mean scores, standard deviation, and variance for each family-category combination, performs statistical significance testing.",
    4: "The query filters benchmark results to include only government-designated evaluations, joins with regulatory requirement tables containing compliance thresholds, calculates risk scores based on deviation from mandated thresholds.",
    5: "The query joins historical adoption data with benchmark performance metrics, groups by model cohorts with similar release timeframe, uses window functions for trend analysis and adoption trajectory projection.",
    6: "The query groups benchmark results by model and time period, calculates performance aggregates and quartiles, applies window functions for rolling averages and period-over-period changes, performs clustering on trajectory patterns to group similar models, handles NULL values in joins.",
    7: "The query joins benchmark, model, and metrics data to calculate market share by aggregating usage or performance indicators, groups by time period and model, uses window functions to compute market share changes, competitive rank movements, and rolling market concentration metrics.",
    8: "The query pivots benchmark results to create a matrix structure with models as rows and benchmarks as columns, computes pairwise correlation coefficients between benchmark scores across the model population, applies window functions for rolling correlations and temporal stability.",
    9: "The query joins pricing, model performance, and revenue data, groups by pricing tier, model, and time period, calculates KPIs including revenue per model and price elasticity, uses window functions for period-over-period revenue changes and rolling averages.",
    10: "The query groups benchmark results by model family and relevant dimensions, calculates aggregate metrics including means, standard deviations, and sample sizes, computes statistical test results (t-statistics, p-values, confidence intervals), uses window functions for percentile rankings.",
    11: "The query joins benchmark, model, and metrics tables to collect compliance-related data, groups by regulatory category and model type, computes aggregate compliance scores and risk levels using quartile analysis, applies window functions for rolling compliance trends and risk rankings.",
    12: "The query combines historical benchmark data with adoption indicators, groups by model family and time period, calculates performance aggregates and variance, uses window functions for rolling adoption rates and performance trends, performs correlation analysis between performance and adoption.",
    13: "The query retrieves benchmark scores across all models and test categories, groups by benchmark type and model, computes aggregate performance scores and percentile rankings, uses window functions to assign dynamic ranks and calculate moving averages, applies quartile-based logic to classify models into performance tiers.",
    14: "The query joins benchmark performance data with pricing information, groups by model and pricing tier, computes performance-to-price ratios and value metrics, uses window functions to rank models by ROI within price brackets and calculate competitive positioning scores.",
    15: "The query consolidates benchmark results from multiple test categories and metrics tables, groups by model and performance dimension, computes normalized scores for each dimension, uses window functions for percentile ranks and rolling performance trends, applies weighting factors for composite multi-dimensional scores.",
    16: "The query joins benchmark results with model and metric metadata, groups by time periods and model dimensions, calculates rolling averages using window functions to smooth volatility, computes period-over-period growth rates, applies statistical trend analysis and quartile calculations.",
    17: "The query performs cross-model comparisons by joining benchmark results across vendors and types, aggregates performance metrics by market segments and benchmark categories, uses window functions for percentile rankings and market share metrics, computes performance gaps between models.",
    18: "The query aggregates benchmark results by evaluation methodology and metric type, calculates statistical validity indicators (standard deviations, coefficient of variation, confidence intervals), groups by benchmark dimensions, uses window functions to identify outliers and consistency patterns.",
    19: "The query segments models and benchmarks by adoption stage, aggregates user activity and evaluation metrics at each funnel level, uses window functions to calculate stage-to-stage conversion rates and time-to-conversion metrics.",
    20: "The query joins benchmark results with target thresholds and competitive baselines, calculates performance deltas across dimensions, groups by model type, benchmark category, and metric, uses window functions for gap quantification and prioritization.",
    21: "The query joins benchmark and model tables with pricing and usage metrics, groups by model category and time period, calculates price-demand correlation coefficients and elasticity ratios, computes rolling averages, applies quartile segmentation, uses window functions for time-series demand forecasting.",
    22: "The query aggregates performance metrics from multiple benchmark tables using UNION or JOIN, groups by model and benchmark category, calculates coefficient of variation and standard deviation across benchmarks, employs window functions for performance ranks and rank consistency identification.",
    23: "The query joins model metadata with benchmark results and release stage information, uses CASE statements to classify models into lifecycle stages, groups performance metrics by model family and stage, calculates stage-over-stage improvements using LAG window functions, computes percentile rankings.",
    24: "The query aggregates benchmark submissions across model providers, groups by provider organization and time periods, calculates market share percentages from submission volumes and top performance counts, uses window functions for quarter-over-quarter growth rates and rolling market share trends.",
    25: "The query aggregates multiple evaluation runs for each model-benchmark combination, groups by model, benchmark, and evaluation configuration, calculates mean scores and standard deviations across runs, computes 95% confidence intervals using t-distribution statistics, derives reliability coefficients from inter-run variance.",
    26: "The query aggregates performance metrics by model and benchmark dimensions, calculates mean, standard deviation, and quartiles (Q1, Q3, IQR) to establish normal ranges, applies window functions to compute z-scores and percentile rankings, flags data points outside 1.5*IQR boundaries for outlier detection.",
    27: "The query joins benchmark, model, and customer data tables, groups by geographic dimensions and demographic attributes, calculates penetration metrics including adoption rates and market share percentages, employs window functions for regional rankings and growth rate computation.",
    28: "The query analyzes performance metrics across models and benchmarks, identifies bottlenecks by comparing actual results against optimal baselines, calculates potential improvement magnitude using statistical aggregations, estimates implementation costs, computes benefit-to-cost ratios for prioritization.",
    29: "The query joins benchmark results with model metadata and business metrics, groups by model and evaluation dimension, computes dimension-specific scores using weighted aggregations, applies window functions for percentile rankings within each dimension and composite scoring.",
    30: "The query categorizes use cases by requirement profiles, aggregates model performance metrics across relevant benchmarks grouped by model family and capability dimensions, applies filtering to eliminate models failing mandatory requirements, calculates match scores using weighted criteria.",
}


def fix_db13(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB13_DESCRIPTIONS and n in DB13_EVIDENCE:
            if q.get("description") != DB13_DESCRIPTIONS[n] or q.get("evidence") != DB13_EVIDENCE[n]:
                q["description"] = DB13_DESCRIPTIONS[n]
                q["evidence"] = DB13_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-14: Cloud Instance Cost (multi-cloud AWS/Azure/GCP)
DB14_DESCRIPTIONS = {
    1: "Organizations using multiple cloud providers (AWS, Azure, GCP) need to optimize spending by identifying equivalent instances across providers. Finance and infrastructure teams require matched instances with cost savings, performance benchmarks, and actionable optimization recommendations.",
    2: "Cloud instance pricing fluctuates over time due to market conditions and provider changes. Finance teams need historical pricing patterns and multi-period forecasts for budget planning and cost projections.",
    3: "Organizations evaluating reserved instance (RI) commitments need ROI analysis. Reserved instances require upfront or long-term commitments in exchange for discounts versus on-demand pricing.",
    4: "Spot instances offer significant discounts (up to 90%) but can be interrupted with short notice. Engineering teams need cost-benefit analysis and risk modeling for fault-tolerant workloads.",
    5: "Cloud providers charge different prices for identical instance types across regions. Infrastructure teams operating globally need cross-region cost comparisons to optimize placement while considering data transfer and compliance.",
    6: "Engineering teams need to understand the relationship between instance performance metrics and costs to optimize resource allocation and identify cost-efficient configurations.",
    7: "Cloud operations teams conduct quarterly reviews to determine which instance families provide the best cost-to-performance ratio for standardization decisions.",
    8: "Finance teams need to project cloud infrastructure costs for the next fiscal quarter based on historical spending patterns to prepare budgets and identify potential overruns.",
    9: "Enterprise architecture teams evaluating multi-cloud strategy need to compare current costs with projected costs across AWS, Azure, and GCP for workload distribution decisions.",
    10: "CFOs require multi-year financial analysis of cloud investments to evaluate net present value of commitment options (on-demand vs reserved vs savings plans) for capital planning.",
    11: "Cloud infrastructure teams need to identify overprovisioned, underutilized instances leading to unnecessary spending and right-sizing recommendations.",
    12: "Finance teams noticing unexpected monthly cloud bill fluctuations need proactive cost anomaly detection before issues escalate.",
    13: "Organizations running many on-demand instances with consistent usage patterns need reserved instance purchase recommendations to capture up to 70% savings.",
    14: "Engineering teams want to leverage spot instances for cost savings on fault-tolerant workloads but need interruption risk analysis to ensure acceptable reliability.",
    15: "Multi-cloud strategy requires understanding equivalent instance offerings across AWS, Azure, and Google Cloud for provider selection and cost-effective workload placement.",
    16: "Cloud operations teams need to identify optimal instance configurations offering the best balance between cost and performance (pareto frontier).",
    17: "Cloud providers regularly deprecate older instance types, forcing migrations. Operations teams need cost impact and usage analysis to support migration planning.",
    18: "Burstable instances (e.g., AWS T-series) offer savings for variable CPU workloads but excessive bursting can cause credit depletion and throttling. Teams need cost and burst utilization analysis.",
    19: "GPU instances are among the most expensive cloud resources for ML, rendering, and compute workloads. Teams need cost and utilization analysis for optimization.",
    20: "Storage costs accumulate from block volumes, snapshots, and archives. Organizations often have unused volumes, excessive snapshots, and improper tiering leading to unnecessary spending.",
    21: "Cloud infrastructure teams need network cost analysis across instances to identify high-bandwidth consumers and optimize data transfer expenses.",
    22: "Finance teams require cost allocation reports to attribute cloud expenses to departments, cost centers, and projects for budget tracking and chargeback.",
    23: "Cloud operations teams need visibility into complete cost lifecycle of instances from creation to termination for TCO understanding and retirement optimization.",
    24: "FinOps teams need to quantify cost optimization opportunities by scoring instances on utilization, rightsizing potential, reserved coverage, and idle resource identification.",
    25: "Cloud architecture teams evaluating workload migrations need a side-by-side comparison matrix of instance types for cost-effectiveness, performance, and operational metrics.",
    26: "Cloud infrastructure involves dependency chains (e.g., app servers depending on databases). Teams need recursive dependency analysis to trace relationships and aggregate costs across the tree.",
    27: "Organizations purchase reserved instances for cost reduction but unused or underutilized reserved capacity represents wasted commitments. Teams need utilization analysis.",
    28: "Spot instances offer significant savings but come with price volatility and availability risks. Teams need price volatility analysis to quantify fluctuations and assess cost-effectiveness.",
    29: "Cloud providers charge different rates for identical instance types across regions. Multi-region deployments need regional cost differences for workload placement and migration decisions.",
    30: "Executives and finance teams require a holistic view of cloud spending synthesizing total expenditure, trends, service breakdowns, regional distribution, anomalies, forecasts, and efficiency metrics.",
}

DB14_EVIDENCE = {
    1: "The query builds eight CTEs. provider_instance_base normalizes specs (memory, vCPU ratio) and joins cloud_instances, cloud_providers, cloud_regions, instance_families. instance_performance_scores aggregates CoreMark and FFmpeg FPS benchmarks into a composite score. instance_pricing_aggregated uses MIN(CASE...) for on-demand, reserved 1yr/3yr, spot pricing. cost_performance_ratios computes cost-per-performance and performance-per-dollar. instance_specification_clusters uses COUNT/RANK OVER (PARTITION BY vCPU and memory buckets). recursive_instance_matching (WITH RECURSIVE) matches instances across providers within 10% tolerance. cross_provider_optimization and final_optimization_recommendations compute price differences, monthly savings, and ROW_NUMBER ranking.",
    2: "The query uses WITH RECURSIVE pricing_time_series to build monthly time series from historical_pricing. base_instance_data and pricing_aggregations compute min, max, avg, median, STDDEV. price_trend_analysis joins with instance data. trend_classification uses CASE for volatility buckets and AVG/RANK window functions. forecast_preparation computes forecast_price_next_month/quarter/year and price_deviation_from_provider_avg_pct.",
    3: "The query uses base_instance_data and chained CTEs (cte_2 through cte_8) selecting from cloud_instances. final_analysis selects from cte_8. Structure supports ROI modeling; placeholder for full reserved vs on-demand comparison logic.",
    4: "The query uses base_instance_data and chained CTEs selecting from cloud_instances. Structure supports spot vs on-demand cost-benefit and risk modeling; placeholder for full implementation.",
    5: "The query uses base_instance_data and chained CTEs. Structure supports regional pricing metrics and window-based rankings; placeholder for full cross-region comparison.",
    6: "The query uses base_instance_data and chained CTEs. Structure supports correlation between performance and cost; placeholder for statistical correlation and quartile analysis.",
    7: "The query uses base_instance_data and chained CTEs. Structure supports aggregation by instance family, RANK/DENSE_RANK for efficiency ordering; placeholder for full cost-per-capacity logic.",
    8: "The query uses base_instance_data and chained CTEs. Structure supports time-series extraction, moving averages (ROWS BETWEEN), LAG/LEAD for growth rates; placeholder for full forecast logic.",
    9: "The query uses base_instance_data and chained CTEs. Structure supports cross-provider joins, CASE for provider-specific mappings; placeholder for full migration comparison.",
    10: "The query uses base_instance_data and chained CTEs. Structure supports grouping by commitment type, window functions for trend extrapolation, discount rate calculations; placeholder for full DCF logic.",
    11: "The query uses base_instance_data and chained CTEs. Structure supports joins with usage metrics, utilization percentiles, threshold comparisons; placeholder for full right-sizing logic.",
    12: "The query uses base_instance_data and chained CTEs. Structure supports rolling 30-day AVG/STDDEV, z-scores, IQR outlier detection; placeholder for full anomaly logic.",
    13: "The query uses base_instance_data and chained CTEs. Structure supports usage consistency metrics, percentile functions, break-even calculations; placeholder for full RI recommendation logic.",
    14: "The query uses base_instance_data and chained CTEs. Structure supports interruption frequency, time-to-replacement window functions; placeholder for full spot risk logic.",
    15: "The query uses base_instance_data and chained CTEs. Structure supports normalization CTEs, fuzzy matching on vCPU/memory within tolerance; placeholder for full cross-provider matching.",
    16: "The query uses base_instance_data and chained CTEs. Structure supports cost-per-performance ratios, window ranking for non-dominated pareto frontier; placeholder for full analysis.",
    17: "The query uses base_instance_data and chained CTEs. Structure supports filtering deprecated instances, joins with costs/usage, migration cost comparison; placeholder for full impact logic.",
    18: "The query uses base_instance_data and chained CTEs. Structure supports filtering burstable types, CPU credit metrics, window functions for sustained burst patterns; placeholder for full analysis.",
    19: "The query uses base_instance_data and chained CTEs. Structure supports filtering GPU types, quartile calculations for utilization segmentation; placeholder for full GPU cost logic.",
    20: "The query uses base_instance_data and chained CTEs. Structure supports joins with storage volumes, grouping by type/attachment/age, growth trend windows; placeholder for full storage analysis.",
    21: "The query uses base_instance_data and chained CTEs. Structure supports filtering network cost types, grouping by region/instance type, month-over-month window functions; placeholder for full network logic.",
    22: "The query uses base_instance_data and chained CTEs. Structure supports tag extraction, grouping by department/cost center/project, percentage allocation; placeholder for full allocation logic.",
    23: "The query uses base_instance_data and chained CTEs. Structure supports creation_date/termination_date duration, lifecycle phase grouping, aggregate lifetime costs; placeholder for full lifecycle logic.",
    24: "The query uses base_instance_data and chained CTEs. Structure supports utilization thresholds, rightsizing comparisons, optimization score calculation; placeholder for full scoring logic.",
    25: "The query uses base_instance_data and chained CTEs. Structure supports grouping by instance_type/family, median hourly rates, cost-per-performance ratios; placeholder for full matrix logic.",
    26: "The query uses WITH RECURSIVE instance_dependency_tree to traverse instance_comparison_matrix from parent to child. Anchor selects current-generation instances; recursive join limits level < 5. Chained CTEs propagate dependency tree for cost aggregation.",
    27: "The query uses base_instance_data and chained CTEs. Structure supports reserved inventory joins with usage, utilization percentage (hours used vs reserved), cost savings comparison; placeholder for full RI utilization logic.",
    28: "The query uses base_instance_data and chained CTEs. Structure supports spot price aggregation, STDDEV/coefficient of variation, rolling averages; placeholder for full volatility logic.",
    29: "The query uses base_instance_data and chained CTEs. Structure supports grouping by region/instance type/pricing model, window ranking for cost efficiency, percentage differences; placeholder for full cross-region logic.",
    30: "The query uses base_instance_data and chained CTEs. Structure supports multi-dimensional grouping (region, instance type, pricing model, department, time period), aggregate metrics; placeholder for full dashboard logic.",
}


def fix_db14(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB14_DESCRIPTIONS and n in DB14_EVIDENCE:
            if q.get("description") != DB14_DESCRIPTIONS[n] or q.get("evidence") != DB14_EVIDENCE[n]:
                q["description"] = DB14_DESCRIPTIONS[n]
                q["evidence"] = DB14_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


# db-15: Electricity and solar rebate (rates, rebates, installations, consumption, utilities)
DB15_DESCRIPTIONS = {
    1: "The electricity and solar rebate business manages data across rebates, installations, and consumption patterns to support rebate eligibility determination and solar installation operations. Strategic rate analysis informs pricing and investment decisions.",
    2: "The electricity and solar rebate platform handles complex rate structures where customers face tiered pricing based on consumption levels and time-of-use (TOU) rates that vary by hour and season. Understanding cost under different scenarios supports customer optimization.",
    3: "The electricity and solar rebate business tracks incentives from federal tax credits, state programs, and utility-specific rebates to help customers maximize solar installation savings. Rebate stacking strategies identify optimal combinations.",
    4: "Electricity and solar rebate operations require understanding historical rate movements to forecast future costs, assess market volatility, and inform strategic planning for solar investment timing.",
    5: "The electricity and solar rebate business operates across multiple states and utility territories where rate structures vary significantly, impacting solar investment returns and competitive positioning.",
    6: "Utility companies in the electricity and solar rebate market need to understand their competitive position to inform pricing strategies and market positioning.",
    7: "Energy providers offer multiple rate codes (tiered, time-of-use, flat-rate) to different customer segments. Understanding which rate structures gain market share is critical for revenue optimization and customer acquisition.",
    8: "Homeowners and businesses considering solar installations need to understand financial viability, particularly how rebate programs affect return on investment and time to break even.",
    9: "Energy markets vary significantly by state due to regulatory environments, resource availability, and competitive dynamics. Analysts need cross-state rate comparisons to identify threats, expansion opportunities, and regional pricing trends.",
    10: "Utilities implement increasingly complex rate structures with multiple tiers, time-of-use pricing, and demand charges. Understanding which structures deliver value without excessive complexity is essential for customer satisfaction and operational efficiency.",
    11: "The utility company manages multiple electricity and solar rebate programs that evolve over time, with different expiration dates and eligibility criteria. Historical trend analysis supports program lifecycle management.",
    12: "Electricity rates vary significantly across service territories. Understanding geographic patterns in rate structures and customer consumption supports pricing strategy optimization.",
    13: "The utility offers dozens of different rate codes serving various customer segments (residential, commercial, time-of-use, tiered). Portfolio analysis supports rationalization and optimization.",
    14: "Customers with solar installations benefit from net metering, which credits excess electricity sent to the grid. Understanding installation economics—costs, rebates, energy savings, net metering credits—is essential for advisors and program design.",
    15: "Electricity rates fluctuate due to fuel costs, regulatory changes, seasonal demand, and time-of-use pricing. Both utility and customers face risks from rate volatility—customers experience bill unpredictability; utility faces revenue uncertainty.",
    16: "The utility company needs to understand how different customer segments are distributed across electricity rate types to optimize pricing strategies and targeted marketing campaigns.",
    17: "The utility company operates in a competitive market and needs to benchmark its electricity rates against neighboring utilities to ensure competitive pricing while maintaining profitability.",
    18: "Customers installing solar panels may qualify for multiple rebates simultaneously (federal, state, utility, equipment-specific). The utility needs to identify optimal rebate stacking strategies.",
    19: "The utility industry is transitioning to time-of-use and tiered rate structures. The company needs to track how quickly customers adopt new rate codes versus remaining on legacy plans.",
    20: "Solar rebate programs are funded at federal, state, and utility levels, with significant variation in participation rates and average rebate amounts across states. Geographic performance analysis supports program management.",
    21: "The utility company needs to forecast electricity rate trends to support strategic pricing decisions and customer communication planning.",
    22: "The utility provider manages multiple rate codes across customer segments and needs to optimize its rate portfolio to balance revenue goals with customer satisfaction and competitive positioning.",
    23: "As solar installations grow, the utility needs to understand rebate market dynamics including program utilization, remaining incentive budgets, and competitive positioning to manage program costs.",
    24: "The utility operates across multiple service regions with varying rate structures, competitive landscapes, and regulatory environments. Understanding regional rate competitiveness supports strategic decisions.",
    25: "The utility offers various rate structures including tiered, time-of-use, and flat rates to different customer segments. Performance analysis supports cost efficiency and structure optimization.",
    26: "The electricity and solar rebate program maintains a complex hierarchical rate code structure where rate plans can inherit from parent rate codes across multiple levels. Hierarchy analysis supports structure understanding.",
    27: "The electricity and solar rebate operations team needs to understand rate performance across multiple dimensions: geography, customer segments, time periods, and rate plan types.",
    28: "The solar rebate program operates in a competitive market where multiple utilities and energy providers offer similar incentives. Competitive analysis supports program positioning.",
    29: "The service territory spans diverse geographic regions with varying electricity costs, consumption patterns, and solar adoption rates. Geographic clustering identifies regional patterns and anomalies.",
    30: "The enterprise manages complex rate structures across multiple customer segments, geographic territories, and product offerings in the electricity and solar rebate domain. Senior leadership requires consolidated strategic dashboards.",
}

DB15_EVIDENCE = {
    1: "The query groups data by relevant geographic and utility dimensions, computes summary statistics including aggregates and quartile distributions, applies window functions to calculate rolling averages and comparative metrics across time periods and regions, and implements robust NULL handling in joins to ensure data completeness across date ranges.",
    2: "The query recursively processes rate tier structures, groups data by consumption levels and time periods, computes cost aggregates for each scenario and quartile distribution of outcomes, employs window functions to calculate rolling usage patterns and comparative cost metrics across rate plans, and handles edge cases including NULL values in join conditions and boundary date ranges.",
    3: "The query groups incentive data by source type and relevant customer dimensions, computes aggregate rebate amounts and quartile distributions to identify typical and exceptional savings opportunities, uses window functions to calculate rolling incentive trends and comparative savings metrics across regions and time periods, and implements NULL-safe joins.",
    4: "The query groups historical rate data by relevant time dimensions and market segments, computes statistical aggregates including mean, standard deviation, and quartile distributions to measure central tendency and spread, applies window functions to calculate rolling averages, year-over-year comparisons, and moving volatility metrics across time periods, and handles edge cases such as NULL values in historical records.",
    5: "The query groups rate data by geographic dimensions including state, utility territory, and market segment, computes comparison aggregates and quartile benchmarks to position each market relative to peers, utilizes window functions to calculate cross-market rankings, regional averages, and comparative growth metrics over time, and implements robust NULL handling in geographic joins.",
    6: "The query joins rebate, installation, and consumption tables to create a unified dataset. It groups data by utility and relevant time periods to compute aggregate performance metrics such as average rates, rebate participation, and customer adoption. Window functions calculate percentile rankings and quartiles to position each utility against peers. Rolling averages identify trends over time.",
    7: "The query aggregates customer and consumption data grouped by rate code and utility to calculate market share percentages. It computes adoption rates by dividing customers on each rate code by total customers within each utility and across the market. Window functions rank rate codes by popularity and calculate cumulative market share. Handles NULL or inactive rate codes.",
    8: "The query joins solar installation records with rebate disbursements and ongoing consumption data to build a complete financial picture. It calculates initial investment costs (installation minus rebates), estimates annual energy savings by multiplying production by avoided electricity rates, and computes simple payback and NPV using appropriate discount rates.",
    9: "The query aggregates rate and consumption data grouped by state and utility to calculate average rates, rate ranges, and customer-weighted average prices. It uses window functions to rank states by rate competitiveness and calculate regional percentiles. Subqueries or CTEs compute year-over-year rate changes.",
    10: "The query analyzes rate structure definitions to compute complexity scores based on factors like number of pricing tiers, presence of time-of-use periods, and demand charge components. It groups by rate code and applies scoring logic.",
    11: "The query joins rebates, installations, and consumption tables on relevant keys with NULL-safe handling. It groups data by time periods and program dimensions to compute aggregate metrics such as total rebate amounts, application counts, and approval rates. Window functions calculate rolling averages and year-over-year comparisons. Date logic identifies programs nearing expiration.",
    12: "The query joins customer, consumption, rate, and geographic tables using zip code as the primary dimension. It groups data by zip code and computes aggregated metrics including average rates, total consumption, customer counts, and solar installation penetration. Window functions rank zip codes by performance indicators and calculate percentile distributions. Statistical measures identify outlier zip codes.",
    13: "The query aggregates data from rate schedules, customer assignments, and consumption tables grouped by rate code. It computes diversity metrics including customer count per rate, revenue contribution, concentration indices (HHI), and usage pattern variance. Window functions calculate each rate's share of total portfolio and rank rates by multiple dimensions. Quartile analysis segments rates into performance tiers.",
    14: "The query joins solar installation records with consumption data, rebate payments, utility rates, and net metering credits. It groups by installation and time periods to calculate metrics including total installation cost, rebate amounts received, energy produced, energy consumed, net metering credits earned, and grid electricity costs avoided. Window functions compute cumulative financial flows and identify payback periods.",
    15: "The query analyzes historical rate data grouped by rate code and time periods. It computes volatility metrics including standard deviation, coefficient of variation, rate change frequency, and maximum single-period changes. Window functions calculate rolling volatility measures and compare current volatility to historical baselines. Statistical tests identify significant volatility.",
    16: "The query joins rebate, installation, and consumption tables, groups customers by rate type and demographic segments, computes aggregate counts and percentages for each segment, calculates quartile distributions to identify concentration patterns, and uses window functions to compare segment performance metrics against overall averages. Handles NULL values in optional fields and filters for active rate codes.",
    17: "The query joins utility rate tables across multiple providers, groups rates by utility and rate type, computes average and median rates for each utility, calculates percentile rankings to determine competitive positioning, uses window functions to compute rolling averages and year-over-year rate changes, and applies benchmarking calculations to show how each utility's rates compare to market averages.",
    18: "The query identifies all active rebate programs, cross-references customer eligibility criteria across multiple rebate tables, groups rebates by customer and installation type, computes total savings for each valid rebate combination while respecting stacking restrictions, uses window functions to rank combinations by total savings amount, and aggregates the maximum possible savings per customer.",
    19: "The query joins customer enrollment records with rate code definitions across utilities, groups customers by rate code type and utility, calculates adoption rates as the percentage of eligible customers enrolled in each rate code, computes market penetration by comparing current enrollments to total addressable customer base, and uses window functions to track adoption trends over time.",
    20: "The query joins rebate applications with customer location data, groups rebates by state and utility service territory, computes aggregate metrics including total rebate amounts, application counts, approval rates, and average rebate values per state, calculates quartile distributions to identify high and low performing regions, and uses window functions to rank states by program performance.",
    21: "The query aggregates historical rate data by time periods and rate categories, calculates statistical measures including moving averages and growth rates, applies window functions to compute rolling trends and year-over-year comparisons, and handles NULL values in temporal joins to ensure complete time series coverage.",
    22: "The query groups customers and consumption data by rate code and customer segment, computes aggregate metrics including revenue per customer and penetration rates, uses window functions to rank rate codes by performance indicators and calculate market share within segments, and applies quartile analysis to identify high and low performers while handling edge cases in customer transitions.",
    23: "The query aggregates rebate application and installation data by program type, geographic region, and time period, calculates utilization rates and remaining budget allocations, employs window functions to track cumulative redemption patterns and forecast depletion timelines, and handles NULL values in eligibility criteria joins.",
    24: "The query groups rate and customer data by geographic region and rate category, calculates average rates and rate distributions within each region, uses window functions to compute market share percentages and rank regions by competitiveness metrics, and performs comparative analysis across regions while handling differences in rate structure definitions and NULL values in regional boundary assignments.",
    25: "The query groups consumption and billing data by rate structure type and customer characteristics, computes aggregate metrics including revenue yield, cost-to-serve ratios, and customer retention rates, applies window functions to calculate efficiency quartiles and benchmark performance across structures, and handles edge cases such as hybrid rate customers and NULL values in cost allocation joins.",
    26: "The query uses recursive CTEs to traverse the rate code hierarchy from top-level parent codes down through all descendant levels, joining rebate, installation, and consumption tables as needed. It groups results by rate code level and hierarchy path, computes aggregate metrics at each level including customer counts and usage volumes, and applies window functions to calculate cumulative metrics across the hierarchy.",
    27: "The query joins rebate eligibility, solar installation, and consumption data across common keys, then groups by multiple dimensions such as region, customer segment, rate type, and time period. It computes aggregate statistics including average rates, total revenue, customer counts, and usage volumes, calculates quartile distributions to identify rate outliers, and applies window functions to generate cross-dimensional comparisons.",
    28: "The query joins solar installation records with rebate eligibility and consumption data to calculate program performance metrics. It groups by program type, geographic market, and customer segment to enable competitive comparisons, computes aggregate metrics including average rebate amounts, participation rates, installation counts, and cost per watt, and applies window functions to calculate market share and competitive positioning.",
    29: "The query aggregates rebate, installation, and consumption data by geographic dimensions such as zip code, county, and service region. It groups by geographic hierarchies to analyze rate distributions at multiple geographic scales, computes statistical aggregates including average rates, rate variance, customer density, and consumption intensity by region, and applies window functions to calculate regional rankings and clustering metrics.",
    30: "The query integrates data from rebate eligibility, solar installations, and consumption systems through comprehensive joins on customer and time dimensions. It groups by enterprise-relevant dimensions including customer segment, product line, geography, and time period to enable strategic analysis, computes aggregate metrics across dimensions, and applies window functions for cross-dimensional comparisons and trend analysis.",
}


def fix_db15(path: Path) -> bool:
    with open(path) as f:
        data = json.load(f)
    changed = False
    for q in data.get("queries", []):
        n = q.get("number")
        if n in DB15_DESCRIPTIONS and n in DB15_EVIDENCE:
            if q.get("description") != DB15_DESCRIPTIONS[n] or q.get("evidence") != DB15_EVIDENCE[n]:
                q["description"] = DB15_DESCRIPTIONS[n]
                q["evidence"] = DB15_EVIDENCE[n]
                changed = True
    if changed:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated {path}")
    return changed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix description vs evidence in queries.json")
    parser.add_argument("--dbs", type=int, nargs="*", help="DB numbers (e.g. 1 2 6). Default: all 1-16")
    parser.add_argument("--skip-db1", action="store_true", help="Skip db-1 (already has manual mappings)")
    args = parser.parse_args()

    dbs = args.dbs if args.dbs else list(range(1, 17))
    if args.skip_db1 and 1 in dbs:
        dbs = [n for n in dbs if n != 1]
    any_changed = False
    for n in dbs:
        db_dir = SOURCE / f"db-{n}"
        qd = get_queries_dir(db_dir)
        src = qd / "queries.json"
        if not src.exists():
            continue
        if n == 1:
            any_changed |= fix_db1(src)
        elif n == 3:
            any_changed |= fix_db3(src)
        elif n == 4:
            any_changed |= fix_db4(src)
        elif n == 5:
            any_changed |= fix_db5(src)
        elif n == 6:
            any_changed |= fix_db6(src)
        elif n == 7:
            any_changed |= fix_db7(src)
        elif n == 8:
            any_changed |= fix_db8(src)
        elif n == 9:
            any_changed |= fix_db9(src)
        elif n == 10:
            any_changed |= fix_db10(src)
        elif n == 11:
            any_changed |= fix_db11(src)
        elif n == 12:
            any_changed |= fix_db12(src)
        elif n == 13:
            any_changed |= fix_db13(src)
        elif n == 14:
            any_changed |= fix_db14(src)
        elif n == 15:
            any_changed |= fix_db15(src)
        else:
            any_changed |= fix_db_heuristic(src)
    if not any_changed:
        print("No changes made.", file=sys.stderr)


if __name__ == "__main__":
    main()
