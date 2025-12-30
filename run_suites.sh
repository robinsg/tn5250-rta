#!/usr/bin/env bash
# Sequential test suite runner with centralized session management
# - login.robot runs first and establishes the session
# - Other test suites run sequentially, sharing the session
# - logout.robot runs at the end (always, even on failure)
#
# Usage:
#   ./run_suites.sh <LPAR_NAME>                          # Run all tests for LPAR
#   ./run_suites.sh <LPAR_NAME> --include smoke          # Run only smoke tests
#   ./run_suites.sh <LPAR_NAME> --exclude wip            # Exclude work-in-progress tests
#   ./run_suites.sh <LPAR_NAME> --include smoke --exclude slow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for LPAR name parameter
if [ -z "$1" ]; then
    echo "Error: LPAR name is required"
    echo "Usage: $0 <LPAR_NAME> [robot_args...]"
    echo "Example: $0 DEV400 --include smoke"
    exit 1
fi

LPAR_NAME="$1"
shift  # Remove LPAR_NAME from arguments

# Export LPAR_NAME so it's available to the test library
export LPAR_NAME

# Validate LPAR directories exist
if [ ! -d "tests/${LPAR_NAME}" ]; then
    echo "Error: LPAR directory 'tests/${LPAR_NAME}' does not exist"
    echo "Please create the directory before running tests"
    exit 1
fi

if [ ! -d "results/${LPAR_NAME}" ]; then
    echo "Error: LPAR directory 'results/${LPAR_NAME}' does not exist"
    echo "Please create the directory before running tests"
    exit 1
fi

echo "Running tests for LPAR: ${LPAR_NAME}"
echo ""

# Load environment variables
if [ -f ".env.sh" ]; then
    echo "Loading environment variables from .env.sh"
    source .env.sh
else
    echo "Warning: .env.sh not found - tests may fail without required variables"
fi

# Capture any additional robot arguments (like --include, --exclude tags)
ROBOT_ARGS="$@"

# Helper function to find test suite (LPAR-specific or common)
find_suite() {
    local suite_name="$1"
    local lpar_suite="tests/${LPAR_NAME}/${suite_name}"
    local common_suite="tests/common/${suite_name}"
    
    if [ -f "$lpar_suite" ]; then
        echo "$lpar_suite"
    elif [ -f "$common_suite" ]; then
        echo "$common_suite"
    else
        echo ""
    fi
}

# Define test suite names in execution order (excluding login and logout)
SUITE_NAMES=(
    "system_config.robot"
    "network_config.robot"
    "journal.robot"
    "database.robot"
    "application.robot"
)

# Build actual suite paths using LPAR-specific or common files
MAIN_SUITES=()
for suite_name in "${SUITE_NAMES[@]}"; do
    suite_path=$(find_suite "$suite_name")
    if [ -n "$suite_path" ]; then
        MAIN_SUITES+=("$suite_path")
    fi
done

# Find login and logout suites
LOGIN_SUITE=$(find_suite "login.robot")
LOGOUT_SUITE=$(find_suite "logout.robot")

if [ -z "$LOGIN_SUITE" ]; then
    echo "Error: login.robot not found in tests/${LPAR_NAME}/ or tests/common/"
    exit 1
fi

if [ -z "$LOGOUT_SUITE" ]; then
    echo "Error: logout.robot not found in tests/${LPAR_NAME}/ or tests/common/"
    exit 1
fi

RESULTS_DIR="results/${LPAR_NAME}/suites"
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
    echo "Note: Suites without matching tests will be skipped"
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
    # Suppress stderr for cleaner output when no tests match (exit 252)
    ROBOT_STDERR=$(mktemp)
    if robot \
        --exitonfailure \
        --output "$RESULTS_DIR/output_${SUITE_NAME}.xml" \
        --log "$RESULTS_DIR/log_${SUITE_NAME}.html" \
        --report "$RESULTS_DIR/report_${SUITE_NAME}.html" \
        $ROBOT_ARGS \
        "$SUITE" 2>"$ROBOT_STDERR"; then
        
        echo "✓ PASSED: $SUITE"
        PASSED_SUITES=$((PASSED_SUITES + 1))
        rm -f "$ROBOT_STDERR"
    else
        EXIT_CODE=$?
        
        # Exit code 252 means no tests matched the tag filter - this is OK
        if [ $EXIT_CODE -eq 252 ]; then
            echo "⊘ SKIPPED: $SUITE (no tests match tag filter)"
            rm -f "$ROBOT_STDERR"
        else
            # Real error - show stderr and fail
            cat "$ROBOT_STDERR" >&2
            rm -f "$ROBOT_STDERR"
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
    fi
    
    echo ""
done

# STEP 3: Clean up .txt screenshot files
echo "Cleaning up .txt screenshot files..."
find results/${LPAR_NAME}/screenshots -name "*.txt" -type f -delete 2>/dev/null || true
echo ""

# STEP 4: Print summary (logout will run via cleanup trap)
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
