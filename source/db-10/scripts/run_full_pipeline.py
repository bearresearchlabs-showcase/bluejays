#!/usr/bin/env python3
"""
Full pipeline: Extract, Transform, and Validate data for db-10
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
db_dir = script_dir.parent

def run_extraction():
    """Run data extraction"""
    print("="*70)
    print("STEP 1: Data Extraction")
    print("="*70)
    
    result = subprocess.run(
        [sys.executable, str(script_dir / "extract_large_dataset.py")],
        cwd=db_dir,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"⚠️  Extraction completed with exit code {result.returncode}")
    else:
        print("✓ Extraction completed")
    
    return result.returncode == 0

def run_transformation():
    """Run data transformation"""
    print("\n" + "="*70)
    print("STEP 2: Data Transformation")
    print("="*70)
    
    result = subprocess.run(
        [sys.executable, str(script_dir / "transform_and_load_data.py")],
        cwd=db_dir,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"⚠️  Transformation completed with exit code {result.returncode}")
    else:
        print("✓ Transformation completed")
    
    return result.returncode == 0

def run_validation():
    """Run database validation"""
    print("\n" + "="*70)
    print("STEP 3: Database Validation")
    print("="*70)
    
    root_dir = db_dir.parent
    result = subprocess.run(
        [sys.executable, str(root_dir / "scripts" / "validate.py"), "db-10"],
        cwd=root_dir,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✓ Validation PASSED")
    else:
        print(f"✗ Validation FAILED (exit code {result.returncode})")
    
    return result.returncode == 0

def main():
    print("="*70)
    print("Full Pipeline: Extract → Transform → Validate")
    print("="*70)
    
    # Step 1: Extract
    extraction_ok = run_extraction()
    
    # Step 2: Transform
    transformation_ok = run_transformation()
    
    # Step 3: Validate
    validation_ok = run_validation()
    
    # Summary
    print("\n" + "="*70)
    print("Pipeline Summary")
    print("="*70)
    print(f"Extraction:    {'✓ PASS' if extraction_ok else '✗ FAIL'}")
    print(f"Transformation: {'✓ PASS' if transformation_ok else '✗ FAIL'}")
    print(f"Validation:    {'✓ PASS' if validation_ok else '✗ FAIL'}")
    print("="*70)
    
    if extraction_ok and transformation_ok and validation_ok:
        print("\n✓ All steps completed successfully!")
        return 0
    else:
        print("\n⚠️  Some steps had issues - check output above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
