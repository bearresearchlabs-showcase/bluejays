import re
import os
from collections import defaultdict

def reduce_data_sql(input_file, output_file, sample_rate=0.15):
    current_table = None
    table_rows = defaultdict(list)
    table_insert_patterns = defaultdict(list)
    in_insert = False
    current_insert = []
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            if line_num % 1000000 == 0:
                print(f"  Processed {line_num:,} lines...")
            
            stripped = line.strip()
            
            if stripped.startswith('INSERT INTO'):
                if current_table and current_insert:
                    table_insert_patterns[current_table].append('\n'.join(current_insert))
                current_insert = [line]
                in_insert = True
                match = re.match(r'INSERT INTO\s+(\w+)', line, re.IGNORECASE)
                if match:
                    current_table = match.group(1)
            elif in_insert:
                current_insert.append(line)
                if stripped.endswith(';'):
                    in_insert = False
                    if current_table:
                        table_insert_patterns[current_table].append('\n'.join(current_insert))
                    current_insert = []
            elif stripped.startswith('--'):
                if current_table and current_insert:
                    table_insert_patterns[current_table].append('\n'.join(current_insert))
                    current_insert = []
                in_insert = False
    
    if current_table and current_insert:
        table_insert_patterns[current_table].append('\n'.join(current_insert))
    
    print(f"\nFound {len(table_insert_patterns)} tables")
    for table, inserts in table_insert_patterns.items():
        print(f"  {table}: {len(inserts)} INSERT statements")
    
    print(f"\nSampling {sample_rate*100:.1f}% of data...")
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("-- Sample Data for Flood Risk Assessment Database\n")
        out.write("-- Compatible with PostgreSQL\n")
        out.write("-- Production sample data for physical climate risk assessment system\n")
        out.write(f"-- Reduced dataset: {sample_rate*100:.1f}% sample for submission (target < 500MB)\n\n")
        
        for table, inserts in table_insert_patterns.items():
            out.write(f"\n-- Insert {table}\n")
            sample_count = max(1, int(len(inserts) * sample_rate))
            sampled = inserts[:sample_count]
            
            for insert_stmt in sampled:
                if 'VALUES' in insert_stmt:
                    lines = insert_stmt.split('\n')
                    values_start_idx = None
                    for i, line in enumerate(lines):
                        if 'VALUES' in line.upper():
                            values_start_idx = i
                            break
                    
                    if values_start_idx is not None:
                        header = '\n'.join(lines[:values_start_idx+1])
                        values_lines = lines[values_start_idx+1:]
                        
                        values_rows = []
                        current_row = []
                        for vline in values_lines:
                            vline_stripped = vline.strip()
                            if vline_stripped.startswith('('):
                                current_row = [vline]
                            elif current_row:
                                current_row.append(vline)
                                if vline_stripped.endswith('),') or vline_stripped.endswith(');'):
                                    values_rows.append('\n'.join(current_row))
                                    current_row = []
                        
                        if values_rows:
                            sample_rows = max(1, int(len(values_rows) * sample_rate))
                            sampled_values = values_rows[:sample_rows]
                            
                            out.write(header + '\n')
                            for i, row in enumerate(sampled_values):
                                if i < len(sampled_values) - 1:
                                    if not row.rstrip().endswith(','):
                                        row = row.rstrip() + ','
                                out.write(row + '\n')
                        else:
                            out.write(insert_stmt)
                    else:
                        out.write(insert_stmt)
                else:
                    out.write(insert_stmt)
    
    input_size = os.path.getsize(input_file) / (1024*1024*1024)
    output_size = os.path.getsize(output_file) / (1024*1024)
    print(f"\nCompleted!")
    print(f"  Input size: {input_size:.2f} GB")
    print(f"  Output size: {output_size:.2f} MB")
    print(f"  Reduction: {(1 - output_size/(input_size*1024))*100:.1f}%")

if __name__ == '__main__':
    input_file = 'db-16/data/data.sql'
    output_file = 'db-16/package/data.sql'
    sample_rate = 0.090
    
    reduce_data_sql(input_file, output_file, sample_rate)
