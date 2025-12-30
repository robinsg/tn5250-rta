# Test Suite Directory Structure

## Overview

The test suite supports running tests against multiple LPARs (Logical Partitions). Each LPAR can have its own specific test files, while common tests are shared across all LPARs.

## Directory Structure

```
tests/
├── common/           # Common test files shared by all LPARs
│   ├── login.robot
│   ├── logout.robot
│   ├── system_config.robot
│   ├── network_config.robot
│   ├── journal.robot
│   ├── database.robot
│   └── application.robot
├── DEV400/          # LPAR-specific tests for DEV400
│   └── (optional LPAR-specific robot files)
└── PROD500/         # LPAR-specific tests for PROD500
    └── (optional LPAR-specific robot files)

results/
├── DEV400/          # Results for DEV400 LPAR
│   ├── suites/      # Test suite results (output.xml, log.html, report.html)
│   └── screenshots/ # Screen captures from tests
└── PROD500/         # Results for PROD500 LPAR
    ├── suites/      # Test suite results
    └── screenshots/ # Screen captures from tests
```

## Usage

To run tests for a specific LPAR:

```bash
./run_suites.sh <LPAR_NAME> [robot_args...]
```

### Examples

```bash
# Run all tests for DEV400
./run_suites.sh DEV400

# Run only smoke tests for DEV400
./run_suites.sh DEV400 --include smoke

# Run all tests except WIP for PROD500
./run_suites.sh PROD500 --exclude wip
```

## Test File Resolution

When running tests, the script looks for test files in the following order:

1. **LPAR-specific directory** (`tests/<LPAR_NAME>/`)
2. **Common directory** (`tests/common/`)

This allows you to:
- Use common tests for all LPARs by default
- Override specific tests for a particular LPAR
- Add LPAR-specific tests when needed

### Example

If you have:
- `tests/common/login.robot` (generic login)
- `tests/DEV400/login.robot` (DEV400-specific login)

When running `./run_suites.sh DEV400`, the script will use `tests/DEV400/login.robot` instead of the common version.

## Creating a New LPAR Configuration

To add a new LPAR:

1. Create the LPAR directory under `tests/`:
   ```bash
   mkdir tests/NEW_LPAR
   ```

2. Create the results directory:
   ```bash
   mkdir -p results/NEW_LPAR/suites results/NEW_LPAR/screenshots
   ```

3. (Optional) Add LPAR-specific test files to `tests/NEW_LPAR/`

4. Run tests:
   ```bash
   ./run_suites.sh NEW_LPAR
   ```

## Required Files

The following files are required and must exist in either the LPAR-specific or common directory:
- `login.robot` - Required to establish the initial session
- `logout.robot` - Required to cleanly close the session

All other test files are optional.
