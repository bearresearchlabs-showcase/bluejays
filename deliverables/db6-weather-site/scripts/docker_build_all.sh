#!/bin/bash
# Build all Docker containers for db-* databases with enhanced reporting

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Create logs directory
mkdir -p docker/build_logs

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

# Results tracking
declare -A BUILD_RESULTS
declare -A BUILD_TIMES
declare -A IMAGE_SIZES
BUILD_ERRORS=()
BUILD_WARNINGS=()

echo "=================================================================================="
echo "BUILDING ALL DOCKER CONTAINERS"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Function to get image size
get_image_size() {
    local image_name=$1
    docker images --format "{{.Size}}" "$image_name:latest" 2>/dev/null || echo "0B"
}

# Function to check if Dockerfile exists
check_dockerfile() {
    local db_name=$1
    if [ ! -f "docker/Dockerfile.$db_name" ]; then
        echo "ERROR: Dockerfile not found: docker/Dockerfile.$db_name"
        BUILD_ERRORS+=("$db_name: Dockerfile not found")
        return 1
    fi
    return 0
}

# Build each container
for db_name in "${DATABASES[@]}"; do
    echo ""
    echo "=================================================================================="
    echo "Building $db_name..."
    echo "=================================================================================="
    
    # Check Dockerfile exists
    if ! check_dockerfile "$db_name"; then
        BUILD_RESULTS["$db_name"]="FAILED"
        continue
    fi
    
    # Record start time
    START_TIME=$(date +%s)
    
    # Build container with logging
    LOG_FILE="docker/build_logs/${db_name}_build.log"
    if docker build -f "docker/Dockerfile.$db_name" -t "$db_name:latest" . > "$LOG_FILE" 2>&1; then
        END_TIME=$(date +%s)
        BUILD_TIME=$((END_TIME - START_TIME))
        BUILD_TIMES["$db_name"]=$BUILD_TIME
        
        # Get image size
        IMAGE_SIZE=$(get_image_size "$db_name")
        IMAGE_SIZES["$db_name"]=$IMAGE_SIZE
        
        # Check for warnings in log
        if grep -qi "warning" "$LOG_FILE"; then
            BUILD_WARNINGS+=("$db_name: Build completed with warnings (check $LOG_FILE)")
        fi
        
        BUILD_RESULTS["$db_name"]="SUCCESS"
        echo "✅ Built $db_name successfully"
        echo "   Build time: ${BUILD_TIME}s"
        echo "   Image size: $IMAGE_SIZE"
    else
        END_TIME=$(date +%s)
        BUILD_TIME=$((END_TIME - START_TIME))
        BUILD_TIMES["$db_name"]=$BUILD_TIME
        BUILD_RESULTS["$db_name"]="FAILED"
        BUILD_ERRORS+=("$db_name: Build failed (check $LOG_FILE)")
        echo "❌ Failed to build $db_name"
        echo "   Check log: $LOG_FILE"
    fi
done

# Generate summary
echo ""
echo "=================================================================================="
echo "BUILD SUMMARY"
echo "=================================================================================="
echo "End time: $(date)"
echo ""

# Count successes and failures
SUCCESS_COUNT=0
FAILED_COUNT=0

for db_name in "${DATABASES[@]}"; do
    if [ "${BUILD_RESULTS[$db_name]}" = "SUCCESS" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "✅ $db_name: SUCCESS (${BUILD_TIMES[$db_name]}s, ${IMAGE_SIZES[$db_name]})"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "❌ $db_name: FAILED (${BUILD_TIMES[$db_name]}s)"
    fi
done

echo ""
echo "Total: $SUCCESS_COUNT successful, $FAILED_COUNT failed"

# Report warnings
if [ ${#BUILD_WARNINGS[@]} -gt 0 ]; then
    echo ""
    echo "WARNINGS:"
    for warning in "${BUILD_WARNINGS[@]}"; do
        echo "  ⚠️  $warning"
    done
fi

# Report errors
if [ ${#BUILD_ERRORS[@]} -gt 0 ]; then
    echo ""
    echo "ERRORS:"
    for error in "${BUILD_ERRORS[@]}"; do
        echo "  ❌ $error"
    done
fi

# Check image sizes
echo ""
echo "IMAGE SIZE ANALYSIS:"
for db_name in "${DATABASES[@]}"; do
    if [ "${BUILD_RESULTS[$db_name]}" = "SUCCESS" ]; then
        SIZE="${IMAGE_SIZES[$db_name]}"
        # Extract numeric value (assuming format like "1.2GB" or "500MB")
        SIZE_NUM=$(echo "$SIZE" | sed 's/[^0-9.]//g')
        SIZE_UNIT=$(echo "$SIZE" | sed 's/[0-9.]//g')
        
        if [ "$SIZE_UNIT" = "GB" ] && (( $(echo "$SIZE_NUM > 2" | bc -l 2>/dev/null || echo 0) )); then
            echo "  ⚠️  $db_name: Large image size ($SIZE)"
        else
            echo "  ✅ $db_name: Image size OK ($SIZE)"
        fi
    fi
done

echo ""
echo "=================================================================================="
if [ $FAILED_COUNT -eq 0 ]; then
    echo "✅ ALL CONTAINERS BUILT SUCCESSFULLY"
    exit 0
else
    echo "❌ SOME CONTAINERS FAILED TO BUILD"
    exit 1
fi
