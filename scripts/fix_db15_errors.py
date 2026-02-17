#!/usr/bin/env python3
"""
Fix db-15 query errors
"""
import re
from pathlib import Path

def fix_all():
    queries_file = Path('db-15/queries/queries.md')
    content = queries_file.read_text()
    original = content
    
    # Query 3: Fix roa.utility_id -> roa.utility_code
    content = re.sub(
        r'\broa\.utility_id\b',
        r'roa.utility_code',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 4: Fix EXTRACT(EPOCH FROM (her.effective_date - MIN(...)))
    # Need to ensure MIN is properly cast
    content = re.sub(
        r'EXTRACT\(EPOCH FROM \(her\.effective_date - MIN\(([^)]+)\)\)\)',
        r'EXTRACT(EPOCH FROM (her.effective_date - (SELECT MIN(\1) FROM historical_electricity_rates her2 WHERE her2.utility_id = her.utility_id AND her2.rate_code_id = her.rate_code_id)))',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 5: Fix s.state_code -> s.state_id or s.state_name
    # Need to check context - likely should be state_id
    content = re.sub(
        r'\bs\.state_code\b',
        r's.state_id',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 8: Fix npva.year -> npva.year_num
    content = re.sub(
        r'\bnpva\.year\b(?!_num)',
        r'npva.year_num',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 11: Fix ambiguous avg_days_until_expiration
    # Need to qualify with table alias - check which CTE has it
    # final_expiration_intelligence has it, so use fei.avg_days_until_expiration
    content = re.sub(
        r'(?<!\.)\bavg_days_until_expiration\b(?!\s*FROM)',
        r'fei.avg_days_until_expiration',
        content,
        flags=re.IGNORECASE
    )
    
    # Query 13: Fix ambiguous diversity_score
    # final_portfolio_analysis has it, so use fpa.diversity_score
    content = re.sub(
        r'(?<!\.)\bdiversity_score\b(?!\s*FROM)',
        r'fpa.diversity_score',
        content,
        flags=re.IGNORECASE
    )
    
    if content != original:
        queries_file.write_text(content)
        return ["db-15"]
    return []

if __name__ == '__main__':
    import os
    os.chdir(Path(__file__).parent.parent)
    fixes = fix_all()
    if fixes:
        print(f"Fixed: {', '.join(fixes)}")
    else:
        print("No fixes needed")
