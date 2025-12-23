#!/usr/bin/env bash
# Sequential test suite runner with centralized session management
# - login.robot runs first and establishes the session
# - Other test suites run sequentially, sharing the session
# - logout.robot runs at the end (always, even on failure)
#
# Usage:
#   ./run_suites.sh                          # Run all tests
#   ./run_suites.sh --include smoke          # Run only smoke tests
#   ./run_suites.sh --exclude wip            # Exclude work-in-progress tests
#   ./run_suites.sh --include smoke --exclude slow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f ".env.sh" ]; then
    echo "Loading environment variables from .env.sh"
    source .env.sh
else
    echo "Warning: .env.sh not found - tests may fail without required variables"
fi

# Capture any additional robot arguments (like --include, --exclude tags)
ROBOT_ARGS="$@"

# Define test suites in execution order (excluding login and logout)
MAIN_SUITES=(
    "tests/system_config.robot"
    "tests/network_config.robot"
    "tests/journal.robot"
    "tests/database.robot"
    "tests/application.robot"
)

LOGIN_SUITE="tests/login.robot"
LOGOUT_SUITE="tests/logout.robot"

RESULTS_DIR="results/suites"
TOTAL_SUITES=$((${#MAIN_SUITES[@]} + 2))  # +2 for login and logout
PASSED_SUITES=0
FAILED_SUITES=0
FAILED_SUITE_LIST=""
LOGIN_SUCCESSFUL=false

# Create results directory
mkdir -p "$RESULTS_DIR"

# Cleanup function to ensure logout always runs
cleanup() {
    local exit_code=$?
    
    if [ "$LOGIN_SUCCESSFUL" = true ]; then
        echo ""
        echo "=========================================="
        echo "Running Logout Suite"
        echo "=========================================="
        
        if robot \
            --output "$RESULTS_DIR/output_logout.xml" \
            --log "$RESULTS_DIR/log_logout.html" \
            --report "$RESULTS_DIR/report_logout.html" \
            $ROBOT_ARGS \
            "$LOGOUT_SUITE"; then
            echo "✓ PASSED: $LOGOUT_SUITE"
        else
            echo "✗ FAILED: $LOGOUT_SUITE"
        fi
    fi
    
    exit $exit_code
}

# Register cleanup function
trap cleanup EXIT

echo "=========================================="
echo "Running Test Suite Series"
echo "=========================================="
echo "Total suites: $TOTAL_SUITES"
if [ -n "$ROBOT_ARGS" ]; then
    echo "Robot args: $ROBOT_ARGS"
fi
echo ""

# STEP 1: Run login suite first
echo "[1/$TOTAL_SUITES] Running: $LOGIN_SUITE"
echo "-------------------------------------------"

if robot \
    --exitonfailure \
    --output "$RESULTS_DIR/output_login.xml" \
    --log "$RESULTS_DIR/log_login.html" \
    --report "$RESULTS_DIR/report_login.html" \
    $ROBOT_ARGS \
    "$LOGIN_SUITE"; then
    
    echo "✓ PASSED: $LOGIN_SUITE"
    PASSED_SUITES=$((PASSED_SUITES + 1))
    LOGIN_SUCCESSFUL=true
else
    EXIT_CODE=$?
    echo "✗ FAILED: $LOGIN_SUITE (exit code: $EXIT_CODE)"
    echo ""
    echo "=========================================="
    echo "Test Suite Execution Summary"
    echo "=========================================="
    echo "Login failed - aborting remaining tests"
    echo "Passed: 0/$TOTAL_SUITES"
    echo "Failed: 1/$TOTAL_SUITES"
    echo ""
    exit $EXIT_CODE
fi

echo ""

# STEP 2: Run main test suites sequentially
for i in "${!MAIN_SUITES[@]}"; do
    SUITE="${MAIN_SUITES[$i]}"
    SUITE_NUM=$((i + 2))  # +2 because login is #1
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
        $ROBOT_ARGS \
        "$SUITE"; then
        
        echo "✓ PASSED: $SUITE"
        PASSED_SUITES=$((PASSED_SUITES + 1))
    else
        EXIT_CODE=$?
        echo "✗ FAILED: $SUITE (exit code: $EXIT_CODE)"
        FAILED_SUITES=$((FAILED_SUITES + 1))
        FAILED_SUITE_LIST="${FAILED_SUITE_LIST}  - $SUITE_NAME (exit $EXIT_CODE)\n"
        
        # Stop execution on first failure, logout will run via cleanup
        echo ""
        echo "=========================================="
        echo "Test Suite Execution Summary"
        echo "=========================================="
        echo "Test suite failed - aborting remaining tests"
        echo "Passed: $PASSED_SUITES/$TOTAL_SUITES (excluding logout)"
        echo "Failed: $FAILED_SUITES/$TOTAL_SUITES (excluding logout)"
        echo ""
        echo "Failed Suites:"
        echo -e "$FAILED_SUITE_LIST"
        echo ""
        exit $EXIT_CODE
    fi
    
    echo ""
done

# STEP 3: Print summary (logout will run via cleanup trap)
echo "=========================================="
echo "Test Suite Execution Summary"
echo "=========================================="
echo "Passed: $PASSED_SUITES/$TOTAL_SUITES (excluding logout)"
echo "Failed: $FAILED_SUITES/$TOTAL_SUITES (excluding logout)"
echo ""

if [ $FAILED_SUITES -gt 0 ]; then
    echo "Failed Suites:"
    echo -e "$FAILED_SUITE_LIST"
    echo ""
    exit 1
else
    echo "All main test suites passed!"
    echo ""
    exit 0
fi
