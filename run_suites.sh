#!/usr/bin/env bash
# Sequential test suite runner with per-suite failure handling
# Each suite stops on first failure, then continues to next suite

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Define test suites in execution order
SUITES=(
    "tests/login.robot"
    "tests/system_config.robot"
    "tests/network_config.robot"
    "tests/journal.robot"
    "tests/database.robot"
    "tests/application.robot"
)

RESULTS_DIR="results/suites"
TOTAL_SUITES=${#SUITES[@]}
PASSED_SUITES=0
FAILED_SUITES=0
FAILED_SUITE_LIST=""

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "=========================================="
echo "Running Test Suite Series"
echo "=========================================="
echo "Total suites: $TOTAL_SUITES"
echo ""

# Run each suite sequentially
for i in "${!SUITES[@]}"; do
    SUITE="${SUITES[$i]}"
    SUITE_NUM=$((i + 1))
    SUITE_NAME=$(basename "$SUITE" .robot)
    
    echo "[$SUITE_NUM/$TOTAL_SUITES] Running: $SUITE"
    echo "-------------------------------------------"
    
    # Run robot with exitonfailure for this suite
    # Output goes to suite-specific results directory
    if robot \
        --exitonfailure \
        --output "$RESULTS_DIR/output_${SUITE_NAME}.xml" \
        --log "$RESULTS_DIR/log_${SUITE_NAME}.html" \
        --report "$RESULTS_DIR/report_${SUITE_NAME}.html" \
        "$SUITE"; then
        
        echo "✓ PASSED: $SUITE"
        ((PASSED_SUITES++))
    else
        EXIT_CODE=$?
        echo "✗ FAILED: $SUITE (exit code: $EXIT_CODE)"
        ((FAILED_SUITES++))
        FAILED_SUITE_LIST="${FAILED_SUITE_LIST}  - $SUITE_NAME (exit $EXIT_CODE)\n"
    fi
    
    echo ""
done

# Print summary
echo "=========================================="
echo "Test Suite Execution Summary"
echo "=========================================="
echo "Passed: $PASSED_SUITES/$TOTAL_SUITES"
echo "Failed: $FAILED_SUITES/$TOTAL_SUITES"
echo ""

if [ $FAILED_SUITES -gt 0 ]; then
    echo "Failed Suites:"
    echo -e "$FAILED_SUITE_LIST"
    echo ""
    exit 1
else
    echo "All suites passed!"
    echo ""
    exit 0
fi
