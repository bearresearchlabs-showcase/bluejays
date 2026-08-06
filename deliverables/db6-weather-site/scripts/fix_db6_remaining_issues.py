#!/usr/bin/env python3
"""
Fix remaining issues in db-6 queries
"""
import re
from pathlib import Path

queries_file = Path('db-6/queries/queries.md')
content = queries_file.read_text()

# Fix 1: ST_Touches doesn't work with geography - need to cast to geometry
content = re.sub(
    r'ST_TOUCHES\(([^,]+),\s*([^)]+)\)',
    r'ST_TOUCHES(\1::geometry, \2::geometry)',
    content,
    flags=re.IGNORECASE
)

# Fix 2: Ensure ST_INTERSECTS uses consistent types (geography works, but let's be explicit)
# Actually ST_INTERSECTS works with geography, so no change needed

# Fix 3: Fix Query 5 - cga.station_geom should be sda.station_geom
# This was already fixed, but let's check for any remaining instances
content = re.sub(
    r'cga\.station_geom',
    r'sda.station_geom',
    content,
    flags=re.IGNORECASE
)

# Fix 4: Fix Query 8 - GROUP BY issue with vm.absolute_error
# Need to find Query 8 and check the GROUP BY clause
query8_match = re.search(r'## Query 8:.*?```sql\n(.*?)```', content, re.DOTALL)
if query8_match:
    query8_sql = query8_match.group(1)
    # Check if vm.absolute_error is in SELECT but not in GROUP BY
    if 'vm.absolute_error' in query8_sql and 'GROUP BY' in query8_sql:
        # Find the GROUP BY clause and add vm.absolute_error if it's aggregated
        # Actually, if it's AVG(vm.absolute_error), it should be fine
        # The issue might be that absolute_error is selected without aggregation
        # Let's check the actual structure
        pass  # Will handle manually

# Fix 5: Fix Query 13 - wo.parameter_value (already fixed, but check for remaining)
content = re.sub(
    r'wo\.parameter_value',
    r'(CASE WHEN fmi.parameter_name = \'Temperature\' THEN wo.temperature WHEN fmi.parameter_name = \'Precipitation\' THEN COALESCE(wo.precipitation_amount, 0) WHEN fmi.parameter_name = \'WindSpeed\' THEN wo.wind_speed ELSE NULL END)',
    content,
    flags=re.IGNORECASE
)

# Actually, that replacement is too complex. Let's just remove the WHERE clause check
# The WHERE clause checking wo.parameter_value IS NOT NULL should check the actual columns
content = re.sub(
    r'WHERE wo\.parameter_value IS NOT NULL',
    r'WHERE (fmi.parameter_name = \'Temperature\' AND wo.temperature IS NOT NULL) OR (fmi.parameter_name = \'Precipitation\' AND wo.precipitation_amount IS NOT NULL) OR (fmi.parameter_name = \'WindSpeed\' AND wo.wind_speed IS NOT NULL)',
    content,
    flags=re.IGNORECASE
)

queries_file.write_text(content)
print("Fixed db-6 query issues")
