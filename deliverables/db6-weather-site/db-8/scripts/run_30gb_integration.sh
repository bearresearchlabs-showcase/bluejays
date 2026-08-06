#!/bin/bash
# Master script to run 30GB data integration process
# Coordinates all phases of data loading and validation

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$DB_DIR/logs"
LOG_FILE="$LOG_DIR/30gb_integration_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"

echo "=========================================="
echo "30GB Data Integration Process"
echo "=========================================="
echo "Log file: $LOG_FILE"
echo ""

# Function to log and execute
run_step() {
    local step_name="$1"
    local command="$2"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting: $step_name" | tee -a "$LOG_FILE"
    echo "Command: $command" | tee -a "$LOG_FILE"
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Completed: $step_name" | tee -a "$LOG_FILE"
        return 0
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILED: $step_name" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Step 1: Generate synthetic data (all in one run)
echo "Phase 1: Generating Synthetic Data (~35GB)"
run_step "Generate All Data" "cd '$DB_DIR' && python3 scripts/generate_synthetic_data.py --companies 500000 --users 2000000 --jobs 5000000 --applications 15000000 --recommendations 50000000 --output-dir data/generated"

# Step 2: Transform data (clean, normalize, enrich)
echo ""
echo "Phase 2: Data Transformation"
run_step "Transform Data" "cd '$DB_DIR' && python3 scripts/data_transformation_pipeline.py --input-dir data/generated --output-dir data/transformed"

# Step 3: Load data in batches (use transformed data)
echo ""
echo "Phase 3: Bulk Loading Data"
# Use transformed files if they exist, otherwise use generated files
DATA_DIR="data/transformed"
if [ ! -f "$DB_DIR/$DATA_DIR/companies_transformed.csv" ]; then
    DATA_DIR="data/generated"
fi

run_step "Load Companies" "cd '$DB_DIR' && python3 scripts/bulk_load_data.py --file $DATA_DIR/companies*.csv --table companies --columns 'company_id,company_name,company_name_normalized,industry,company_size,headquarters_city,headquarters_state,headquarters_country,website_url,linkedin_url,description,founded_year,employee_count,revenue_range,is_federal_agency,agency_code,data_source,company_rating,total_reviews,created_at,updated_at' --batch-size 10000"
run_step "Load Users" "cd '$DB_DIR' && python3 scripts/bulk_load_data.py --file $DATA_DIR/user_profiles*.csv --table user_profiles --columns 'user_id,email,full_name,location_city,location_state,location_country,location_latitude,location_longitude,current_job_title,current_company,years_experience,education_level,resume_text,linkedin_url,github_url,portfolio_url,preferred_work_model,salary_expectation_min,salary_expectation_max,preferred_locations,profile_completeness_score,is_active,created_at,updated_at,last_active_at' --batch-size 10000"
run_step "Load Jobs" "cd '$DB_DIR' && python3 scripts/bulk_load_data.py --file $DATA_DIR/job_postings*.csv --table job_postings --columns 'job_id,company_id,job_title,job_title_normalized,job_description,job_type,work_model,location_city,location_state,location_country,location_latitude,location_longitude,salary_min,salary_max,salary_currency,salary_type,posted_date,expiration_date,application_url,application_method,is_active,is_federal_job,usajobs_id,agency_name,pay_plan,grade_level,data_source,source_url,view_count,application_count,match_score_avg,created_at,updated_at' --batch-size 5000"
run_step "Load Applications" "cd '$DB_DIR' && python3 scripts/bulk_load_data.py --file $DATA_DIR/job_applications*.csv --table job_applications --columns 'application_id,user_id,job_id,application_status,application_date,submitted_at,status_updated_at,cover_letter_text,resume_version,match_score,application_method,application_reference_id,notes,created_at,updated_at' --batch-size 10000"
run_step "Load Recommendations" "cd '$DB_DIR' && python3 scripts/bulk_load_data.py --file $DATA_DIR/job_recommendations*.csv --table job_recommendations --columns 'recommendation_id,user_id,job_id,match_score,skill_match_score,location_match_score,salary_match_score,experience_match_score,work_model_match_score,recommendation_reason,recommendation_rank,is_liked,is_applied,is_dismissed,recommendation_date,expires_at,created_at' --batch-size 10000"

# Step 4: Run data quality validation
echo ""
echo "Phase 4: Data Quality Validation"
run_step "Data Quality Check" "cd '$DB_DIR' && python3 scripts/data_quality_framework.py"

# Step 5: Pull data from internet sources (public APIs, no keys required)
echo ""
echo "Phase 5: Pull Data from Internet Sources"
run_step "Pull Internet Data" "cd '$DB_DIR' && python3 scripts/pull_internet_data.py --output-dir data/internet_pulled --target-gb 1.0"

# Step 6: Transform internet-pulled data
echo ""
echo "Phase 6: Transform Internet Data"
if [ -d "$DB_DIR/data/internet_pulled" ] && [ "$(ls -A $DB_DIR/data/internet_pulled 2>/dev/null)" ]; then
    run_step "Transform Internet Data" "cd '$DB_DIR' && python3 scripts/data_transformation_pipeline.py --input-dir data/internet_pulled --output-dir data/internet_transformed"
else
    echo "No internet-pulled data found, skipping transformation"
fi

# Step 7: Run incremental updates (if APIs configured) - Pull real data from APIs
echo ""
echo "Phase 7: Incremental Updates (API Data Pull)"
if [ -n "$USAJOBS_API_KEY" ]; then
    run_step "USAJobs Incremental Update" "cd '$DB_DIR' && python3 scripts/incremental_update.py"
else
    echo "Skipping incremental updates (API keys not configured)"
fi

# Step 8: Verify data volume meets 10-30GB requirement
echo ""
echo "Phase 8: Data Volume Verification"
run_step "Verify Data Volume" "cd '$DB_DIR' && python3 scripts/verify_data_volume.py --data-dir data"

echo ""
echo "=========================================="
echo "30GB Data Integration Complete"
echo "=========================================="
echo "Check log file for details: $LOG_FILE"
echo ""
echo "Data Volume Summary:"
echo "  - Generated files: data/generated/"
echo "  - Transformed files: data/transformed/"
echo "  - Internet-pulled files: data/internet_pulled/"
echo "  - Internet-transformed files: data/internet_transformed/"
echo "  - Total target: Minimum 1 GB"
echo ""
echo "To verify volume: python3 scripts/verify_data_volume.py --data-dir data"
