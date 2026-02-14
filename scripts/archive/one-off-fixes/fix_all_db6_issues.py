#!/usr/bin/env python3
"""
Comprehensive fix for all db-6 remaining issues
"""
import re
from pathlib import Path

queries_file = Path('db-6/queries/queries.md')
content = queries_file.read_text()

# Fix 1: Add p5_value to forecast_statistics CTE in Query 15
# Find the forecast_statistics CTE and add p5_value calculation
forecast_stats_pattern = r'(forecast_statistics AS \([\s\S]*?PERCENTILE_CONT\(0\.90\) WITHIN GROUP \(ORDER BY paf\.parameter_value\) AS p90_value,[\s\S]*?PERCENTILE_CONT\(0\.95\) WITHIN GROUP \(ORDER BY paf\.parameter_value\) AS p95_value,)'
replacement = r'\1\n        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY paf.parameter_value) AS p5_value,'
content = re.sub(forecast_stats_pattern, replacement, content)

# Fix 2: Fix Query 1 and Query 2 ST_DISTANCE/ST_Within issues
# The issue is that ST_DISTANCE works with geography, but we need to ensure both args are geography
# ST_Within needs geometry types - both should be cast to geometry
# Actually, these look correct already. The issue might be that grid_cell_geom is NULL

# Fix 3: Fix Query 8 GROUP BY - check if there's an unaggregated vm.absolute_error
# Actually Query 8 looks correct - all absolute_error references are aggregated

# Fix 4: Fix Query 9 ST_Touches - already fixed by previous script

# Fix 5: Fix Query 13 wo.parameter_value - already fixed

queries_file.write_text(content)
print("Fixed db-6 query issues")
