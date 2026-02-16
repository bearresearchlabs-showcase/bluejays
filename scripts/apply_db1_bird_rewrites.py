#!/usr/bin/env python3
"""
Apply BIRD/LiveSQLBench rewrites to queries.md for a database.
Updates question, normal_query, evidence for all 30 queries.
Manual curation — no LLM.
Usage: python3 apply_db1_bird_rewrites.py [db_num]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def get_rewrites(db_num: int) -> dict:
    """Return REWRITES dict for given db number."""
    if 1 <= db_num <= 5:
        r = {
            1: _DB1_REWRITES,
            2: _DB2_REWRITES,
            3: _DB3_REWRITES,
            4: _DB4_REWRITES,
            5: _DB5_REWRITES,
        }
        return r.get(db_num, {})
    if 6 <= db_num <= 16:
        return _build_domain_rewrites(db_num)
    return {}


# db-1: aircraft_position_history (hex, altitude, speed, timestamp)
# Evidence format: Situation (context) → Task (goal) → Action (what SQL does) → Result (output)
_DB1_REWRITES = {
    1: (
        "I want to see how aircraft altitude varies over the past year, with rolling averages and outlier counts per day and hex code.",
        "Compute daily altitude statistics with rolling averages and outlier counts for each aircraft hex over the last 365 days.",
        "Situation: Fleet operators need to monitor how aircraft altitude varies over time to spot anomalies and identify maintenance needs. Telemetry comes from ADS-B; each aircraft has a unique hex code (ICAO 24-bit transponder) and altitude is stored in feet. Task: Produce daily aggregated altitude statistics per aircraft, including rolling averages and outlier counts. Action: The query builds four CTEs—it keeps the 60 most recent points per aircraft, computes a 5-row rolling average, flags outliers where altitude exceeds 2 standard deviations from the mean, and classifies each reading as Increasing, Decreasing, or Stable. It groups by day and aircraft hex and requires at least 2 records per group. When standard deviation is zero, it sets z-score to 0 to avoid division errors. Result: A table of daily metrics per aircraft—record count, quartiles, min/max, outlier count, and how many readings are trending up.",
    ),
    2: (
        "Can you show me weekly altitude stats grouped by speed bucket? I need quartiles, outliers, and how many readings are trending up.",
        "Compute weekly altitude statistics by speed bucket with quartiles, z-score outliers, and increasing-trend counts.",
        "Situation: Analysts want to compare altitude patterns across different groundspeed buckets (speed in knots) to understand how fast-flying aircraft behave differently. Task: Produce weekly altitude statistics by speed bucket with quartiles, outlier counts, and trend direction. Action: The query groups by week and speed, segments altitude into sextiles per speed bucket, flags statistical outliers (z-score above 2), and uses LAG/LEAD to classify each reading as Increasing, Decreasing, or Stable. It filters out sparse buckets with fewer than 3 records. Result: Weekly metrics per speed bucket—quartiles, outlier count, and how many readings are trending up.",
    ),
    3: (
        "Give me monthly altitude summaries by aircraft hex — quartiles, median, outlier count, and rolling average.",
        "Compute monthly altitude statistics per aircraft hex with quartiles, median, outlier count, and rolling average.",
        "Situation: Monthly reporting helps fleet managers track long-term altitude trends per aircraft and spot seasonal patterns. Task: Produce monthly altitude summaries per aircraft with quartiles, median, outlier count, and rolling average. Action: The query groups by month and aircraft hex, uses PERCENTILE_CONT for Q1/median/Q3, computes a 6-row rolling average, limits to 80 most recent points per aircraft to control memory, and allows single-record months for sparse aircraft. Result: Monthly metrics per aircraft—record count, quartiles, median, outlier count, and rolling average.",
    ),
    4: (
        "I need daily altitude breakdown by speed — how many outliers, how many increasing, and the max cumulative sum.",
        "Compute daily altitude statistics by speed with outlier count, increasing-trend count, and max cumulative sum.",
        "Situation: Daily breakdowns by speed help identify whether certain flight regimes (e.g., cruise vs climb) show more anomalies. Task: Produce daily altitude statistics by speed with outlier count, increasing-trend count, and peak cumulative sum. Action: The query groups by day and speed, computes a running cumulative sum per speed, uses a 7-row rolling window, segments into octiles, and derives trend direction from the change between consecutive readings. When the prior value is missing, it treats the reading as Stable. Result: Daily metrics per speed—outlier count, how many are increasing, and the max cumulative sum.",
    ),
    5: (
        "Show me weekly altitude metrics per hex — record count, quartiles, stddev, and how many are increasing.",
        "Compute weekly altitude statistics per aircraft hex with record count, quartiles, stddev, and increasing-trend count.",
        "Situation: Weekly views per aircraft help compare variability (stddev) and trend direction across the fleet. Task: Produce weekly altitude metrics per aircraft with record count, quartiles, stddev, and increasing-trend count. Action: The query groups by week and aircraft hex, computes standard deviation to measure altitude dispersion, counts readings classified as Increasing, limits to 60 recent points per aircraft, and ranks aircraft by cumulative sum for prioritization. Result: Weekly metrics per aircraft—record count, quartiles, stddev, and how many readings are increasing.",
    ),
    6: (
        "I want daily altitude stats by speed bucket — quartiles, rolling average, and outlier detection.",
        "Compute daily altitude statistics by speed with quartiles, rolling average, and z-score outlier count.",
        "Situation: Daily stats by speed bucket help spot anomalies in specific flight regimes. Task: Produce daily altitude statistics by speed with quartiles, rolling average, and outlier detection. Action: The query groups by day and speed, extracts hour and day-of-week for intermediate analysis, computes z-scores (with zero when stddev is zero to avoid errors), and averages a 5-row rolling window. It requires at least 2 records per group. Result: Daily metrics per speed—quartiles, rolling average, and outlier count.",
    ),
    7: (
        "Monthly altitude analysis by hex — I need quartiles, min, max, outlier count, and cumulative sum.",
        "Compute monthly altitude statistics per aircraft hex with quartiles, min, max, outlier count, and max cumulative sum.",
        "Situation: Monthly analysis per aircraft supports fleet-wide comparisons of altitude range and cumulative activity. Task: Produce monthly altitude statistics per aircraft with quartiles, min/max, outlier count, and max cumulative sum. Action: The query groups by month and aircraft hex, captures min/max altitude range, flags outliers (z-score above 2), limits to 80 recent points per aircraft, uses PERCENT_RANK for relative position, and ensures LAST_VALUE gets the true last value per partition. Result: Monthly metrics per aircraft—quartiles, min, max, outlier count, and max cumulative sum.",
    ),
    8: (
        "Daily altitude by hex — show me gaps between readings and sequential differences, plus quartiles.",
        "Compute daily altitude statistics per hex with sequential differences, gap analysis, and quartiles.",
        "Situation: Analysts need to see how altitude changes between consecutive readings to detect sudden climbs or descents. Task: Produce daily altitude statistics per aircraft with sequential differences and quartiles. Action: The query groups by day and aircraft hex, computes the change from the prior reading (LAG) so the first row per aircraft has no prior value, derives trend direction from that change, and uses LAG/LEAD for prev/next values. Gap analysis is implicit in the timestamp ordering. Result: Daily metrics per aircraft—sequential differences, trend direction, and quartiles.",
    ),
    9: (
        "I need daily altitude by speed — anomaly detection using z-scores, plus quartiles and trend counts.",
        "Compute daily altitude statistics by speed with z-score anomaly detection, quartiles, and trend counts.",
        "Situation: Anomaly detection by speed bucket helps identify unusual altitude patterns in specific flight regimes. Task: Produce daily altitude statistics by speed with z-score anomaly detection, quartiles, and trend counts. Action: The query groups by day and speed, flags anomalies where altitude exceeds 2 standard deviations from the partition mean, handles zero stddev safely, segments into octiles, and uses a 7-row rolling window. Result: Daily metrics per speed—outlier count, increasing count, quartiles, and trend counts.",
    ),
    10: (
        "Weekly altitude by hex — recency and frequency scoring, plus quartiles and rolling average.",
        "Compute weekly altitude statistics per hex with recency-frequency metrics, quartiles, and rolling average.",
        "Situation: Recency and frequency scoring helps prioritize which aircraft to inspect based on how often and how recently they were active. Task: Produce weekly altitude statistics per aircraft with recency-frequency style metrics and quartiles. Action: The query groups by week and aircraft hex, uses ROW_NUMBER for recency (most recent first), uses record_count as a frequency proxy, ranks aircraft by cumulative sum, and computes a 6-row rolling average. It requires at least 3 records per group. Result: Weekly metrics per aircraft—record count, quartiles, rolling average, and ranking by activity.",
    ),
    11: (
        "Monthly altitude by speed — multi-period cohort style retention metrics and quartiles.",
        "Compute monthly altitude statistics by speed with cohort-style metrics and quartiles.",
        "Situation: Cohort-style analysis by speed bucket helps compare how different flight regimes behave over time. Task: Produce monthly altitude statistics by speed with cohort-style metrics and quartiles. Action: The query treats speed buckets as cohorts and altitude as the metric, limits to 90 points per speed, uses increasing_count and trend_direction for retention-like analysis, and orders by period and avg_value for recency and prominence. Result: Monthly metrics per speed—cohort-style retention indicators and quartiles.",
    ),
    12: (
        "Daily altitude by hex — second-order derivative style changes, quartiles, and outlier count.",
        "Compute daily altitude statistics per hex with second-order change metrics, quartiles, and outlier count.",
        "Situation: Second-order changes (acceleration of altitude) help detect sudden climbs or descents that might indicate issues. Task: Produce daily altitude statistics per aircraft with change metrics, quartiles, and outlier count. Action: The query computes the change from the prior reading (first derivative) and uses trend direction (Increasing/Decreasing) as the sign of change. LAG/LEAD enable prev/next for implicit second derivative. It flags z-score outliers and limits to 60 points per aircraft. Result: Daily metrics per aircraft—change indicators, quartiles, and outlier count.",
    ),
    13: (
        "Weekly altitude by speed — cross-category benchmarking with percentiles and quartiles.",
        "Compute weekly altitude statistics by speed with percentile benchmarking and quartiles.",
        "Situation: Cross-speed benchmarking helps compare how altitude distributes across different flight regimes. Task: Produce weekly altitude statistics by speed with percentile benchmarking and quartiles. Action: The query uses PERCENT_RANK and PERCENTILE_CONT for cross-speed comparison, segments into sextiles, ranks speeds by cumulative sum, computes partition avg/stddev for z-scores, and limits to 70 points per speed. Result: Weekly metrics per speed—percentile benchmarks, quartiles, and cross-category ranking.",
    ),
    14: (
        "Monthly altitude by hex — weighted moving average pipeline, quartiles, and trend counts.",
        "Compute monthly altitude statistics per hex with weighted moving average, quartiles, and trend counts.",
        "Situation: Moving averages smooth noisy altitude data to reveal underlying trends. Task: Produce monthly altitude statistics per aircraft with moving average, quartiles, and trend counts. Action: The query uses a 6-row rolling window as a simple moving average, outputs avg_rolling, counts increasing and outlier readings, limits to 80 points per aircraft, and requires at least 1 record per group. Result: Monthly metrics per aircraft—rolling average, quartiles, and trend counts.",
    ),
    15: (
        "Daily altitude by speed — peak period identification, efficiency metrics, quartiles.",
        "Compute daily altitude statistics by speed with peak identification, efficiency metrics, and quartiles.",
        "Situation: Peak period identification helps find when altitude is highest in each speed bucket for capacity planning. Task: Produce daily altitude statistics by speed with peak identification and efficiency metrics. Action: The query ranks readings by altitude within each day to identify peaks, extracts hour and day-of-week for temporal analysis, uses max_cumulative and avg_rolling as efficiency proxies, and requires at least 2 records per group. Result: Daily metrics per speed—peak indicators, efficiency proxies, and quartiles.",
    ),
    16: (
        "Weekly altitude by hex — lifetime value style estimation, quartiles, and cumulative sum.",
        "Compute weekly altitude statistics per hex with LTV-style metrics, quartiles, and cumulative sum.",
        "Situation: LTV-style metrics help prioritize aircraft by total activity (cumulative sum) for maintenance scheduling. Task: Produce weekly altitude statistics per aircraft with LTV-style metrics and quartiles. Action: The query uses cumulative_sum and max_cumulative as value proxies, ranks aircraft by cumulative sum, uses PERCENT_RANK for distribution, limits to 60 points per aircraft, and requires at least 3 records per group. Result: Weekly metrics per aircraft—LTV-style ranking, quartiles, rolling average, and outlier count.",
    ),
    17: (
        "Monthly altitude by speed — year-over-year growth rate style analysis, quartiles.",
        "Compute monthly altitude statistics by speed with YoY-style growth metrics and quartiles.",
        "Situation: Year-over-year growth analysis helps compare how altitude patterns change across flight regimes from one year to the next. Task: Produce monthly altitude statistics by speed with YoY-style growth metrics and quartiles. Action: The query uses trend_direction and delta_value to support growth analysis, LAG to capture prior values, filters to the last 365 days for one-year comparison, and limits to 90 points per speed. Result: Monthly metrics per speed—growth indicators and quartiles.",
    ),
    18: (
        "Daily altitude by hex — heatmap data by dimensions, quartiles, outlier count.",
        "Compute daily altitude statistics per hex for heatmap dimensions with quartiles and outlier count.",
        "Situation: Heatmaps visualize altitude patterns across time and aircraft for quick fleet-wide insight. Task: Produce daily altitude statistics per aircraft suitable for heatmap visualization. Action: The query uses period and aircraft hex as dimensions, avg_value and record_count as intensity, extracts hour and day-of-week for 2D heatmap options, flags z-score outliers, and orders by period and avg_value. Result: Daily metrics per aircraft—heatmap-ready dimensions, quartiles, and outlier count.",
    ),
    19: (
        "Weekly altitude by speed — running percentile distribution, quartiles, trend counts.",
        "Compute weekly altitude statistics by speed with running percentiles, quartiles, and trend counts.",
        "Situation: Running percentiles show how altitude distributes within each speed bucket over time. Task: Produce weekly altitude statistics by speed with running percentiles, quartiles, and trend counts. Action: The query uses PERCENT_RANK and PERCENTILE_CONT for running percentile view, limits to 70 points per speed, and counts increasing and outlier readings. Result: Weekly metrics per speed—running percentiles, quartiles, and trend counts.",
    ),
    20: (
        "Monthly altitude by hex — cross-correlation pattern analysis, quartiles, rolling avg.",
        "Compute monthly altitude statistics per hex with correlation-style metrics, quartiles, and rolling average.",
        "Situation: Cross-correlation patterns help see how altitude relates to prior readings across the fleet. Task: Produce monthly altitude statistics per aircraft with correlation-style metrics and quartiles. Action: The query uses LAG/LEAD and delta_value to enable sequential correlation, trend_direction to capture pattern, partition_avg and partition_stddev for normalization, and limits to 80 points per aircraft. Result: Monthly metrics per aircraft—correlation-style pattern indicators, quartiles, and rolling average.",
    ),
    21: (
        "Daily altitude by speed — status transition forensic analysis, quartiles, outlier count.",
        "Compute daily altitude statistics by speed with status transition analysis, quartiles, and outlier count.",
        "Situation: Status transition analysis helps trace how altitude moves from Increasing to Decreasing or Stable over time for forensic review. Task: Produce daily altitude statistics by speed with status transition analysis, quartiles, and outlier count. Action: The query treats trend_direction (Increasing/Decreasing/Stable) as status and delta_value as the driver of transitions, uses LAG/LEAD for forensic sequencing, flags z-score outliers, and requires at least 2 records per group. Result: Daily metrics per speed—status transitions, quartiles, and outlier count.",
    ),
    22: (
        "Weekly altitude by hex — multi-metric dashboard aggregation, quartiles, all key stats.",
        "Compute weekly altitude statistics per hex for dashboard with quartiles and multi-metric aggregation.",
        "Situation: Dashboards need a single query that supplies all key metrics for fleet monitoring. Task: Produce weekly altitude statistics per aircraft with all dashboard metrics. Action: The query aggregates record_count, avg_value, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, and max_cumulative in one pass. It requires at least 3 records per group. Result: Weekly metrics per aircraft—full dashboard set with quartiles and all key stats.",
    ),
    23: (
        "Monthly altitude by speed — sequential pattern mining with windows, quartiles.",
        "Compute monthly altitude statistics by speed with sequential pattern metrics and quartiles.",
        "Situation: Sequential pattern mining reveals how altitude evolves over time within each speed bucket. Task: Produce monthly altitude statistics by speed with sequential pattern metrics and quartiles. Action: The query uses LAG, LEAD, delta_value, and trend_direction for sequential analysis, ROWS BETWEEN windows for framing, ROW_NUMBER for ordering, and limits to 90 points per speed. Result: Monthly metrics per speed—sequential patterns and quartiles.",
    ),
    24: (
        "Daily altitude by hex — concentration index computation, quartiles, outlier count.",
        "Compute daily altitude statistics per hex with concentration index metrics, quartiles, and outlier count.",
        "Situation: Concentration indices show how much of total activity is concentrated in top aircraft. Task: Produce daily altitude statistics per aircraft with concentration metrics, quartiles, and outlier count. Action: The query uses DENSE_RANK, PERCENT_RANK, and cumulative_sum distribution to compute concentration, segments into quintiles with NTILE(5), flags z-score outliers, and requires at least 2 records per group. Result: Daily metrics per aircraft—concentration indices, quartiles, and outlier count.",
    ),
    25: (
        "Weekly altitude by speed — statistical anomaly score assignment, quartiles.",
        "Compute weekly altitude statistics by speed with anomaly scores, quartiles, and trend counts.",
        "Situation: Anomaly scores help prioritize which speed buckets to investigate for unusual altitude patterns. Task: Produce weekly altitude statistics by speed with anomaly scores, quartiles, and trend counts. Action: The query uses z_score as the primary anomaly score, aggregates outlier_count, computes partition_avg and partition_stddev, limits to 70 points per speed, and requires at least 3 records per group. Result: Weekly metrics per speed—anomaly scores, quartiles, and trend counts.",
    ),
    26: (
        "Monthly altitude by hex — fiscal period comparative reporting, quartiles.",
        "Compute monthly altitude statistics per hex for fiscal period comparison with quartiles.",
        "Situation: Fiscal period reporting supports month-over-month and quarter-over-quarter comparisons for planning. Task: Produce monthly altitude statistics per aircraft for fiscal period comparison. Action: The query uses DATE_TRUNC('month') as the period, outputs quartiles, avg, and stddev to enable period-over-period comparison, limits to 80 points per aircraft, and requires at least 1 record per group. Result: Monthly metrics per aircraft—fiscal-period-ready with quartiles for comparison.",
    ),
    27: (
        "Daily altitude by speed — throughput optimization metrics, quartiles, rolling avg.",
        "Compute daily altitude statistics by speed with throughput metrics, quartiles, and rolling average.",
        "Situation: Throughput metrics help assess how much altitude activity occurs in each speed bucket for capacity planning. Task: Produce daily altitude statistics by speed with throughput metrics, quartiles, and rolling average. Action: The query uses record_count, avg_rolling, and max_cumulative as throughput proxies, limits to 90 points per speed, uses a 7-row rolling window, and requires at least 2 records per group. Result: Daily metrics per speed—throughput indicators, quartiles, and rolling average.",
    ),
    28: (
        "Weekly altitude by hex — cumulative trend analysis pipeline, quartiles.",
        "Compute weekly altitude statistics per hex with cumulative trend analysis and quartiles.",
        "Situation: Cumulative trend analysis shows how total altitude activity builds over time per aircraft. Task: Produce weekly altitude statistics per aircraft with cumulative trend analysis and quartiles. Action: The query uses cumulative_sum and max_cumulative, trend_direction and increasing_count for trend analysis, ranks aircraft by cumulative sum, and requires at least 3 records per group. Result: Weekly metrics per aircraft—cumulative trends, quartiles, and activity ranking.",
    ),
    29: (
        "Monthly altitude by speed — multi-dimensional pivot aggregation, quartiles.",
        "Compute monthly altitude statistics by speed with multi-dimensional aggregation and quartiles.",
        "Situation: Multi-dimensional aggregation supports pivoting and slicing by period and speed for ad-hoc analysis. Task: Produce monthly altitude statistics by speed with multi-dimensional aggregation and quartiles. Action: The query uses period and speed as dimensions and aggregates count, avg, percentiles, stddev, min, max, outlier count, and trend count. It requires at least 1 record per group. Result: Monthly metrics per speed—multi-dimensional with quartiles for pivot analysis.",
    ),
    30: (
        "Weekly altitude by speed — outlier detection with IQR method style, quartiles.",
        "Compute weekly altitude statistics by speed with IQR-style outlier detection and quartiles.",
        "Situation: IQR-style outlier detection uses quartiles to flag values outside the typical range, complementing z-score methods. Task: Produce weekly altitude statistics by speed with IQR-style outlier detection and quartiles. Action: The query uses PERCENTILE_CONT for Q1 and Q3, z-score above 2 to approximate outlier detection, stddev_value to support IQR alternatives, limits to 70 points per speed, and requires at least 3 records per group. Result: Weekly metrics per speed—quartiles, IQR-style outlier detection, and trend counts.",
    ),
}

# db-2: phppos_sales (sale_id, sale_time, employee_id, customer_id, payment_type, location_id) - Filling Station Retail
# Evidence format: Situation → Task → Action → Result
_DB2_REWRITES = {
    1: (
        "I want to see daily sales performance by employee over the past year, with rolling 7-day averages and how many transactions are above their average.",
        "Compute daily sales metrics per employee with rolling 7-day average and above-average transaction count.",
        "Situation: Store managers need to track how each employee performs day to day and whether transactions are above or below their personal average. Task: Produce daily sales metrics per employee with a rolling 7-day average and count of above-average transactions. Action: The query groups by day and employee, compares each transaction to the employee's average, uses a 7-row rolling window for smoothing, keeps the 100 most recent transactions per employee, and filters out single-transaction days. Result: Daily metrics per employee—rolling average and how many transactions beat their average.",
    ),
    2: (
        "Can you show me monthly purchase patterns by customer? I need quartiles, outlier count, and how many transactions are trending up.",
        "Compute monthly sales statistics per customer with quartiles, z-score outliers, and increasing-trend count.",
        "Situation: Marketing teams want to understand customer purchase patterns and spot unusual spenders or rising engagement. Task: Produce monthly sales statistics per customer with quartiles, outlier count, and trend direction. Action: The query groups by month and customer, segments spend into sextiles, flags statistical outliers (z-score above 2), derives trend direction from consecutive changes, limits to 70 points per customer, and requires at least 3 records per group. Result: Monthly metrics per customer—quartiles, outlier count, and how many transactions are trending up.",
    ),
    3: (
        "Give me daily employee performance quartiles — record count, median, outlier count, and rolling average.",
        "Compute daily sales statistics per employee with quartiles, median, outlier count, and rolling average.",
        "Situation: Daily performance quartiles help managers compare employees and spot outliers who need coaching or recognition. Task: Produce daily sales statistics per employee with quartiles, median, outlier count, and rolling average. Action: The query groups by day and employee, uses PERCENTILE_CONT for Q1, median, and Q3, computes a 7-row rolling average, segments into septiles, and allows single-transaction days for new hires. Result: Daily metrics per employee—record count, quartiles, median, outlier count, and rolling average.",
    ),
    4: (
        "I need weekly sales breakdown by payment type — quartiles, outlier count, and how many are increasing.",
        "Compute weekly sales statistics by payment_type with quartiles, outlier count, and increasing-trend count.",
        "Situation: Finance teams track how cash, card, and other payment methods perform over time for reconciliation and fraud monitoring. Task: Produce weekly sales statistics by payment type with quartiles, outlier count, and increasing-trend count. Action: The query groups by week and payment type, uses an 8-row rolling window, segments into octiles, and requires at least 2 records per group. Result: Weekly metrics per payment type—quartiles, outlier count, and how many transactions are increasing.",
    ),
    5: (
        "Show me monthly sales velocity by location — quartiles, stddev, outlier count, and cumulative sum.",
        "Compute monthly sales statistics per location_id with quartiles, stddev, outlier count, and max cumulative sum.",
        "Situation: Regional managers compare store performance across locations for resource allocation and site selection. Task: Produce monthly sales statistics per location with quartiles, stddev, outlier count, and max cumulative sum. Action: The query groups by month and location, computes standard deviation for variability, uses a 9-row rolling window, segments into noniles, limits to 100 points per location, and requires at least 3 records per group. Result: Monthly metrics per location—quartiles, stddev, outlier count, and cumulative sum.",
    ),
    6: (
        "I want daily sales by employee — quartiles, rolling average, and anomaly detection.",
        "Compute daily sales statistics per employee with quartiles, rolling average, and z-score outlier count.",
        "Situation: Anomaly detection helps flag unusual daily patterns that might indicate errors or fraud. Task: Produce daily sales statistics per employee with quartiles, rolling average, and anomaly detection. Action: The query groups by day and employee, extracts hour and day-of-week for temporal context, uses a 10-row rolling window, flags z-score outliers, and allows single-transaction days. Result: Daily metrics per employee—quartiles, rolling average, and anomaly count.",
    ),
    7: (
        "Monthly sales by customer — invoice gap analysis style, quartiles, and trend counts.",
        "Compute monthly sales statistics per customer with gap-style metrics, quartiles, and trend counts.",
        "Situation: Gap analysis reveals how purchase frequency and amounts change between consecutive months for churn prediction. Task: Produce monthly sales statistics per customer with gap-style metrics, quartiles, and trend counts. Action: The query groups by month and customer, uses LAG/LEAD to compute changes between consecutive months, derives trend direction, and requires at least 3 records per group. Result: Monthly metrics per customer—gap indicators, quartiles, and trend counts.",
    ),
    8: (
        "Daily sales by payment type — suspended transaction anomaly detection, quartiles.",
        "Compute daily sales statistics by payment_type with anomaly detection, quartiles, and trend counts.",
        "Situation: Anomalous payment patterns may indicate system issues, fraud, or unusual customer behavior. Task: Produce daily sales statistics by payment type with anomaly detection, quartiles, and trend counts. Action: The query groups by day and payment type, flags z-score outliers to surface anomalous patterns, and requires at least 2 records per group. Result: Daily metrics per payment type—anomaly count, quartiles, and trend counts.",
    ),
    9: (
        "Weekly sales by customer — recency-frequency analysis, quartiles, rolling avg.",
        "Compute weekly sales statistics per customer with recency-frequency metrics and quartiles.",
        "Situation: Recency-frequency scoring helps prioritize which customers to target for retention or upsell campaigns. Task: Produce weekly sales statistics per customer with recency-frequency metrics and quartiles. Action: The query groups by week and customer, uses ROW_NUMBER for recency ordering, ranks customers by cumulative spend, and requires at least 3 records per group. Result: Weekly metrics per customer—recency-frequency ranking, quartiles, and activity level.",
    ),
    10: (
        "Monthly sales by employee — multi-period cohort retention style, quartiles.",
        "Compute monthly sales statistics per employee with cohort-style metrics and quartiles.",
        "Situation: Cohort-style analysis compares how employee performance evolves over time for training and retention. Task: Produce monthly sales statistics per employee with cohort-style metrics and quartiles. Action: The query groups by month and employee, uses increasing_count and trend_direction for retention-like analysis, and allows single-record months for new hires. Result: Monthly metrics per employee—cohort-style retention indicators and quartiles.",
    ),
    11: (
        "Daily sales by location — sales acceleration rate, quartiles, outlier count.",
        "Compute daily sales statistics per location with acceleration metrics, quartiles, and outlier count.",
        "Situation: Sales acceleration shows how quickly revenue is growing at each location for expansion planning. Task: Produce daily sales statistics per location with acceleration metrics, quartiles, and outlier count. Action: The query groups by day and location, uses delta_value to capture change between consecutive days, and requires at least 2 records per group. Result: Daily metrics per location—acceleration indicators, quartiles, and outlier count.",
    ),
    12: (
        "Weekly sales by employee — cross-location revenue benchmarking, quartiles.",
        "Compute weekly sales statistics per employee with benchmarking metrics and quartiles.",
        "Situation: Cross-employee benchmarking helps identify top performers and set fair targets across locations. Task: Produce weekly sales statistics per employee with benchmarking metrics and quartiles. Action: The query groups by week and employee, uses PERCENT_RANK and DENSE_RANK for cross-employee comparison, and requires at least 3 records per group. Result: Weekly metrics per employee—benchmark ranking, quartiles, and relative performance.",
    ),
    13: (
        "Monthly sales by payment type — time-weighted moving average, quartiles.",
        "Compute monthly sales statistics by payment_type with moving average and quartiles.",
        "Situation: Moving averages smooth seasonal noise to reveal underlying payment-mix trends. Task: Produce monthly sales statistics by payment type with moving average and quartiles. Action: The query groups by month and payment type, computes avg_rolling from a ROWS BETWEEN window, and requires at least 2 records per group. Result: Monthly metrics per payment type—rolling average, quartiles, and trend.",
    ),
    14: (
        "Daily sales by customer — peak hour identification and staffing, quartiles.",
        "Compute daily sales statistics per customer with peak metrics and quartiles.",
        "Situation: Peak hour identification supports staffing decisions and promotional timing. Task: Produce daily sales statistics per customer with peak metrics and quartiles. Action: The query groups by day and customer, extracts sale_hour for peak analysis, and allows single-transaction days. Result: Daily metrics per customer—peak indicators, quartiles, and activity timing.",
    ),
    15: (
        "Weekly sales by location — customer lifetime value estimation style, quartiles.",
        "Compute weekly sales statistics per location with LTV-style metrics and quartiles.",
        "Situation: LTV-style metrics help prioritize high-value locations for investment and marketing. Task: Produce weekly sales statistics per location with LTV-style metrics and quartiles. Action: The query groups by week and location, uses cumulative_sum and max_cumulative as value proxies, and requires at least 3 records per group. Result: Weekly metrics per location—LTV-style ranking, quartiles, and cumulative value.",
    ),
    16: (
        "Monthly sales by employee — YoY growth rate with seasonal adjustment, quartiles.",
        "Compute monthly sales statistics per employee with YoY-style growth metrics and quartiles.",
        "Situation: Year-over-year growth helps compare employee performance across seasons and plan for next year. Task: Produce monthly sales statistics per employee with YoY-style growth metrics and quartiles. Action: The query groups by month and employee, uses trend_direction and delta_value for growth analysis, filters to the last 365 days for one-year comparison, and allows single-record months. Result: Monthly metrics per employee—growth indicators and quartiles.",
    ),
    17: (
        "Daily sales by payment type — transaction velocity heatmap data, quartiles.",
        "Compute daily sales statistics by payment_type for heatmap with quartiles and trend counts.",
        "Situation: Heatmaps visualize payment mix and velocity across time for quick operational insight. Task: Produce daily sales statistics by payment type suitable for heatmap visualization. Action: The query groups by day and payment type, uses period and payment_type as heatmap dimensions, and requires at least 2 records per group. Result: Daily metrics per payment type—heatmap-ready dimensions, quartiles, and trend counts.",
    ),
    18: (
        "Weekly sales by customer — running percentile distribution, quartiles.",
        "Compute weekly sales statistics per customer with running percentiles and quartiles.",
        "Situation: Running percentiles show how customer spend distributes within each week for segmentation. Task: Produce weekly sales statistics per customer with running percentiles and quartiles. Action: The query groups by week and customer, uses PERCENT_RANK and PERCENTILE_CONT for distribution, and requires at least 3 records per group. Result: Weekly metrics per customer—running percentiles, quartiles, and distribution.",
    ),
    19: (
        "Monthly sales by location — employee cross-sell effectiveness, quartiles.",
        "Compute monthly sales statistics per location with cross-sell metrics and quartiles.",
        "Situation: Cross-sell effectiveness by location helps identify where training or incentives are working. Task: Produce monthly sales statistics per location with cross-sell metrics and quartiles. Action: The query groups by month and location, uses DENSE_RANK and partition metrics for comparison, and requires at least 3 records per group. Result: Monthly metrics per location—cross-sell indicators, quartiles, and ranking.",
    ),
    20: (
        "Daily sales by employee — deleted transaction forensic analysis, quartiles.",
        "Compute daily sales statistics per employee with forensic metrics and quartiles.",
        "Situation: Forensic analysis traces transaction sequences to investigate voids, refunds, or soft-deleted records. Task: Produce daily sales statistics per employee with forensic metrics and quartiles. Action: The query groups by day and employee, uses LAG/LEAD for sequencing, and can leverage the deleted column for soft-delete tracking. Result: Daily metrics per employee—forensic sequencing, quartiles, and activity.",
    ),
    21: (
        "Weekly sales by payment type — multi-metric dashboard aggregation, quartiles.",
        "Compute weekly sales statistics by payment_type for dashboard with quartiles and multi-metric aggregation.",
        "Situation: Dashboards need a single query that supplies all key payment metrics for executive review. Task: Produce weekly sales statistics by payment type with all dashboard metrics. Action: The query groups by week and payment type, aggregates record_count, avg, quartiles, stddev, min, max, outlier_count, increasing_count, avg_rolling, and max_cumulative in one pass, and requires at least 2 records per group. Result: Weekly metrics per payment type—full dashboard set with quartiles.",
    ),
    22: (
        "Monthly sales by customer — sequential purchase pattern mining, quartiles.",
        "Compute monthly sales statistics per customer with sequential pattern metrics and quartiles.",
        "Situation: Sequential pattern mining reveals how purchase behavior evolves over time for personalization. Task: Produce monthly sales statistics per customer with sequential pattern metrics and quartiles. Action: The query groups by month and customer, uses LAG, LEAD, delta_value, and trend_direction for sequential analysis, and requires at least 3 records per group. Result: Monthly metrics per customer—sequential patterns and quartiles.",
    ),
    23: (
        "Daily sales by location — revenue concentration index, quartiles.",
        "Compute daily sales statistics per location with concentration metrics and quartiles.",
        "Situation: Concentration indices show how much revenue is concentrated in top locations for resource allocation. Task: Produce daily sales statistics per location with concentration metrics and quartiles. Action: The query groups by day and location, uses DENSE_RANK, PERCENT_RANK, and cumulative_sum for concentration, and requires at least 2 records per group. Result: Daily metrics per location—concentration indices, quartiles, and ranking.",
    ),
    24: (
        "Weekly sales by employee — anomaly score computation, quartiles.",
        "Compute weekly sales statistics per employee with anomaly scores and quartiles.",
        "Situation: Anomaly scores help prioritize which employees to review for unusual patterns or training needs. Task: Produce weekly sales statistics per employee with anomaly scores and quartiles. Action: The query groups by week and employee, uses z_score as the primary anomaly score, and requires at least 3 records per group. Result: Weekly metrics per employee—anomaly scores, quartiles, and trend counts.",
    ),
    25: (
        "Monthly sales by payment type — fiscal period comparative analysis, quartiles.",
        "Compute monthly sales statistics by payment_type for fiscal comparison with quartiles.",
        "Situation: Fiscal period reporting supports month-over-month and quarter-over-quarter comparisons for finance. Task: Produce monthly sales statistics by payment type for fiscal period comparison. Action: The query groups by month and payment type, uses DATE_TRUNC('month') as the period, and requires at least 2 records per group. Result: Monthly metrics per payment type—fiscal-period-ready with quartiles for comparison.",
    ),
    26: (
        "Daily sales by customer — transaction throughput optimization, quartiles.",
        "Compute daily sales statistics per customer with throughput metrics and quartiles.",
        "Situation: Throughput metrics help assess transaction volume per customer for capacity and loyalty programs. Task: Produce daily sales statistics per customer with throughput metrics and quartiles. Action: The query groups by day and customer, uses record_count, avg_rolling, and max_cumulative as throughput proxies, and allows single-transaction days. Result: Daily metrics per customer—throughput indicators, quartiles, and activity level.",
    ),
    27: (
        "Weekly sales by location — store account payment trend analysis, quartiles.",
        "Compute weekly sales statistics per location with payment trend metrics and quartiles.",
        "Situation: Payment trend analysis by location helps identify shifts in payment mix (e.g., card vs cash) for terminal planning. Task: Produce weekly sales statistics per location with payment trend metrics and quartiles. Action: The query groups by week and location, uses trend_direction and increasing_count for trend analysis, and requires at least 3 records per group. Result: Weekly metrics per location—payment trends, quartiles, and activity.",
    ),
    28: (
        "Monthly sales by employee — multi-dimensional pivot analysis, quartiles.",
        "Compute monthly sales statistics per employee with multi-dimensional aggregation and quartiles.",
        "Situation: Multi-dimensional aggregation supports pivoting by period and employee for ad-hoc reporting. Task: Produce monthly sales statistics per employee with multi-dimensional aggregation and quartiles. Action: The query groups by month and employee, uses period and employee_id as dimensions, and allows single-record months. Result: Monthly metrics per employee—multi-dimensional with quartiles for pivot analysis.",
    ),
    29: (
        "Daily sales by payment type — sales funnel stage progression, quartiles.",
        "Compute daily sales statistics by payment_type with funnel metrics and quartiles.",
        "Situation: Funnel stage progression tracks how payment mix evolves through the day for conversion analysis. Task: Produce daily sales statistics by payment type with funnel metrics and quartiles. Action: The query groups by day and payment type, uses trend_direction for stage progression, and requires at least 2 records per group. Result: Daily metrics per payment type—funnel indicators, quartiles, and progression.",
    ),
    30: (
        "Weekly sales by customer — outlier detection with IQR method, quartiles.",
        "Compute weekly sales statistics per customer with IQR-style outlier detection and quartiles.",
        "Situation: IQR-style outlier detection uses quartiles to flag unusual spenders for fraud or VIP treatment. Task: Produce weekly sales statistics per customer with IQR-style outlier detection and quartiles. Action: The query groups by week and customer, uses PERCENTILE_CONT for Q1 and Q3, z-score above 2 to approximate outlier detection, and requires at least 3 records per group. Result: Weekly metrics per customer—quartiles, IQR-style outlier detection, and trend counts.",
    ),
}

# db-3: orders_order (total_amount, seller_id, status, created_at) - Hierarchical Orders
_DB3_REWRITES = {
    i: (
        q.replace("altitude", "order total amount").replace("hex", "seller").replace("speed", "order status").replace("aircraft", "order"),
        nq.replace("altitude", "order total amount").replace("hex", "seller").replace("speed", "order status").replace("aircraft", "order"),
        ev.replace("aircraft_position_history", "orders_order").replace("Altitude", "Total amount").replace("hex", "seller_id").replace("speed", "status").replace("Hex", "Seller").replace("Speed", "Status").replace("altitude", "total_amount").replace("aircraft", "seller").replace("Aircraft", "Seller").replace("fleet operators", "order managers").replace("Fleet operators", "Order managers"),
    )
    for i, (q, nq, ev) in _DB1_REWRITES.items()
}

# db-4: models (id, name, user_id, created_at) - SharedAI Models
_DB4_REWRITES = {
    i: (
        q.replace("altitude", "model id").replace("hex", "model name").replace("speed", "user").replace("aircraft", "model"),
        nq.replace("altitude", "model id").replace("hex", "model name").replace("speed", "user").replace("aircraft", "model"),
        ev.replace("aircraft_position_history", "models").replace("Altitude", "Model id").replace("hex", "name").replace("speed", "user_id").replace("Hex", "Model name").replace("Speed", "User").replace("altitude", "id").replace("aircraft", "model").replace("Aircraft", "Model").replace("fleet operators", "platform operators").replace("Fleet operators", "Platform operators"),
    )
    for i, (q, nq, ev) in _DB1_REWRITES.items()
}

# db-5: phppos_sales - same as db-2 (POS Retail)
_DB5_REWRITES = _DB2_REWRITES

# db-6 through db-16: domain-specific; build from queries.md
_DB_DOMAIN_INFO = {
    6: ("Weather Consulting Insurance", "grib2_forecasts, shapefile_boundaries, weather_stations", "forecast parameters, spatial boundaries, weather observations"),
    7: ("Maritime Shipping", "vessel_tracking, port_calls, sailings, carriers", "vessel positions, port calls, sailing metrics"),
    8: ("Job Market Intelligence", "user_profiles, job_postings, skills, applications", "user profiles, job postings, skill demand"),
    9: ("Shipping Intelligence", "shipments, carriers, routes", "shipment tracking, carrier performance"),
    10: ("Marketing Intelligence", "campaigns, metrics, segments", "campaign performance, marketing metrics"),
    11: ("Parking Intelligence", "parking_events, lots, zones", "parking utilization, lot occupancy"),
    12: ("Credit Card & Rewards", "transactions, cards, rewards", "transaction patterns, reward redemptions"),
    13: ("AI Benchmark Marketing", "benchmarks, models, metrics", "benchmark results, model performance"),
    14: ("Cloud Instance Cost", "instances, costs, usage", "instance costs, usage metrics"),
    15: ("Electricity & Solar Rebate", "rebates, installations, consumption", "rebate eligibility, solar installations"),
    16: ("Flood Risk Assessment", "flood_zones, properties, risk_scores", "flood risk, property exposure"),
}


def _build_domain_rewrites(db_num: int) -> dict:
    """Build rewrites for db-6 through db-16 from queries.md."""
    md_path = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
    if not md_path.exists():
        return {}
    text = md_path.read_text(encoding="utf-8")
    domain_name, tables, metrics = _DB_DOMAIN_INFO.get(db_num, ("", "", ""))
    rewrites = {}
    for m in re.finditer(r"```json\n(.*?)```", text, re.DOTALL):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        qid = obj.get("question_id")
        if not qid or qid < 1 or qid > 30:
            continue
        old_q = obj.get("question", "")
        exp = obj.get("expected_output", "")
        # question: first-person colloquial
        if old_q and not old_q.strip().startswith("I "):
            question = f"I want to see {old_q.lower()}."
        else:
            question = old_q or f"Show me {exp}."
        # normal_query: concise from expected_output
        normal_query = exp if len(exp) < 120 else exp[:117] + "..."
        # evidence: STAR format (Situation, Task, Action, Result)
        task_desc = (
            exp
            if exp
            and exp.strip().lower() not in ("query results", "query result")
            else (old_q if old_q else "Produce the requested analytics metrics for the domain.")
        )
        evidence = (
            f"Situation: In the {domain_name} domain, data from {tables} captures {metrics} for operational and analytical use. "
            f"Task: {task_desc} "
            f"Action: The query groups by the relevant dimensions, computes aggregates and quartiles where applicable, uses window functions for rolling and comparative metrics, and handles edge cases such as NULL handling in joins and date ranges. "
            f"Result: The output delivers the requested metrics for dashboards, reporting, or further analysis."
        )
        rewrites[qid] = (question, normal_query, evidence)
    return rewrites


def main():
    ap = argparse.ArgumentParser(description="Apply BIRD rewrites to queries.md")
    ap.add_argument("db", type=int, nargs="?", default=1, help="Database number (1-16)")
    args = ap.parse_args()
    db_num = args.db
    REWRITES = get_rewrites(db_num)
    if not REWRITES:
        print(f"No rewrites defined for db-{db_num}", file=sys.stderr)
        sys.exit(1)
    QUERIES_MD = REPO / "source" / f"db-{db_num}" / "app" / "QUERIES" / "queries.md"
    if not QUERIES_MD.exists():
        print(f"Not found: {QUERIES_MD}", file=sys.stderr)
        sys.exit(1)
    text = QUERIES_MD.read_text(encoding="utf-8")

    # Find each ```json ... ``` block and replace
    def replace_block(m):
        raw = m.group(1)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)
        qid = obj.get("question_id")
        if qid not in REWRITES:
            return m.group(0)
        question, normal_query, evidence = REWRITES[qid]
        obj["question"] = question
        obj["normal_query"] = normal_query
        obj["evidence"] = evidence
        # Preserve key order: db_id, question_id, question, normal_query, SQL, evidence, ...
        out = json.dumps(obj, indent=2, ensure_ascii=False)
        return "```json\n" + out + "\n```"

    new_text = re.sub(r"```json\n(.*?)```", replace_block, text, flags=re.DOTALL)
    QUERIES_MD.write_text(new_text, encoding="utf-8")
    print("Applied 30 rewrites to", QUERIES_MD)


if __name__ == "__main__":
    main()
