#!/usr/bin/env python3
"""
Poll data extraction until all databases reach 1GB+.
Monitors progress and restarts expansion as needed.
"""
import subprocess
import time
from pathlib import Path
import sys

BASE = Path("/Users/machine/Documents/AQ/db")

def get_total_size(db_num):
    """Get total size of data files for a database."""
    data_dir = BASE / f"db-{db_num}" / "data"
    total = 0
    for file in data_dir.glob("*.sql"):
        if file.is_file():
            total += file.stat().st_size
    for file in data_dir.glob("*.dump"):
        if file.is_file():
            total += file.stat().st_size
    return total

def check_process_running(process_name):
    """Check if a process is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def start_expansion():
    """Start data expansion process."""
    script_path = BASE / "scripts" / "expand_data_extraction.py"
    if script_path.exists():
        subprocess.Popen(
            ["python3", str(script_path)],
            cwd=str(BASE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    return False

def monitor_extraction():
    """Monitor extraction until completion."""
    print("=" * 70)
    print("Polling Data Extraction Until Completion")
    print("=" * 70)
    
    target_gb = 1.0
    check_interval = 10  # seconds
    last_status = {}
    expansion_started = False
    
    while True:
        # Get current sizes
        sizes = {}
        all_complete = True
        
        for db_num in [1, 2, 3, 4, 5]:
            size_bytes = get_total_size(db_num)
            size_gb = size_bytes / (1024 ** 3)
            size_mb = size_bytes / (1024 ** 2)
            sizes[db_num] = {
                'bytes': size_bytes,
                'gb': size_gb,
                'mb': size_mb
            }
            
            if size_gb < target_gb:
                all_complete = False
        
        # Print status
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n[{timestamp}] Status Check:")
        
        # Check if expansion process is running
        is_running = check_process_running("expand_data_extraction")
        print(f"  Expansion Process: {'Running' if is_running else 'Stopped'}")
        print(f"  Database Sizes:")
        
        for db_num in [1, 2, 3, 4, 5]:
            status = "✅" if sizes[db_num]['gb'] >= target_gb else "⚠️"
            prev_gb = last_status.get(db_num, {}).get('gb', 0)
            change = sizes[db_num]['gb'] - prev_gb
            change_str = f" (+{change:.3f}GB)" if change > 0 else ""
            
            print(f"    {status} db-{db_num}: {sizes[db_num]['mb']:.2f}MB ({sizes[db_num]['gb']:.3f}GB){change_str}")
        
        # Check completion
        if all_complete:
            print("\n" + "=" * 70)
            print("✅ EXTRACTION COMPLETE - All databases at 1GB+")
            print("=" * 70)
            print("\nFinal Sizes:")
            for db_num in [1, 2, 3, 4, 5]:
                print(f"  db-{db_num}: {sizes[db_num]['gb']:.3f}GB ({sizes[db_num]['mb']:.2f}MB)")
            break
        
        # Start expansion if not running and targets not met
        if not is_running and not all_complete:
            if not expansion_started:
                print("\n⚠️  Starting expansion process...")
                start_expansion()
                expansion_started = True
                time.sleep(5)  # Wait for process to start
            else:
                # Check if we should restart (if no progress for a while)
                if last_status:
                    progress_made = any(
                        sizes[db]['gb'] > last_status.get(db, {}).get('gb', 0)
                        for db in [1, 2, 3, 4, 5]
                    )
                    if not progress_made:
                        print("\n⚠️  No progress detected, restarting expansion...")
                        start_expansion()
                        time.sleep(5)
        
        last_status = sizes
        time.sleep(check_interval)

if __name__ == '__main__':
    try:
        monitor_extraction()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        sys.exit(0)
