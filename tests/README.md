# Test Suite Directory Structure

## Overview

The test suite supports running tests against multiple LPARs (Logical Partitions). Each LPAR can have its own specific test files, while common tests are shared across all LPARs. Tests run sequentially within a shared TN5250 session for efficiency.

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

## Common Test Suites

### login.robot
**Purpose**: Establishes TN5250 session and authenticates to IBM i system

**Test Cases**:
- Login To IBM i - Complete authentication flow validation

**Tags**: `login`, `smoke`

**Requirements**: Environment variables (HOST, USER, PASS, SSL, DEVNAME, MAP)

### logout.robot
**Purpose**: Gracefully terminates TN5250 session

**Test Cases**:
- Sign Off From IBM i - Session termination validation

**Tags**: `logout`, `cleanup`

### system_config.robot
**Purpose**: Validates IBM i system configuration and security settings

**Test Cases**:
- Verify System Configuration - OS/400 product license validation (5770SS1)
- Verify System Status - Security level check (QSECURITY system value)

**Tags**: `system`, `configuration`, `status`

**Commands Used**: `DSPLICKEY`, `DSPSYSVAL`

### network_config.robot
**Purpose**: Validates network configuration and connectivity

**Test Cases**:
- Verify Network Configuration - Network attributes and interface status
- Verify Network Connectivity - IP addresses and interface statistics

**Tags**: `network`, `configuration`, `connectivity`

**Commands Used**: `DSPNETA`, `WRKCFGSTS`, `NETSTAT`

### journal.robot
**Purpose**: Validates journaling functionality and audit trails

**Test Cases**:
- Verify Journal Entries - System journal accessibility

**Tags**: `journal`, `audit`

**Commands Used**: `WRKJRN`

### database.robot
**Purpose**: Validates database functionality and integrity

**Test Cases**:
- Verify Database Objects - QIWS library and sample file access
- Check Database Integrity - Placeholder for future checks

**Tags**: `database`, `objects`, `integrity`

**Commands Used**: `RUNQRY`

**Note**: Database integrity checks (CHKOBJ, VFYOBJ) not yet implemented

### application.robot
**Purpose**: Validates application installation and functionality

**Test Cases**:
- Verify Application Installation - Library accessibility verification
- Verify Application Functionality - Placeholder for future tests

**Tags**: `application`, `installation`, `functionality`

**Commands Used**: `DSPLIB`

**Note**: Application functionality tests not yet implemented

## Tag Reference

Common tags used across test suites:

- **Execution Phase**: `login`, `logout`, `cleanup`
- **Test Type**: `smoke`, `critical`
- **Functional Area**: `system`, `network`, `database`, `application`, `journal`
- **Subcategory**: `configuration`, `status`, `connectivity`, `objects`, `integrity`, `installation`, `functionality`, `audit`
- **Development**: `wip` (work in progress - typically excluded)

## Environment Variables

Each LPAR requires these environment variables (set in `.envs/.env.sh.LPAR_NAME`):

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TN5250_HOST` | Hostname or IP address | `dev400` or `192.168.1.100` | Yes |
| `TN5250_USER` | Username for authentication | `TESTUSER` | Yes |
| `TN5250_PASS` | Password (auto-converted to Secret) | `password123` | Yes |
| `TN5250_SSL` | SSL connection flag | `1` (SSL) or `0` (no SSL) | No (default: 0) |
| `TN5250_DEVNAME` | Device name | `QPADEV0001` | No |
| `TN5250_MAP` | Character map code | `285` | No (default: 285) |

## Test Execution Order

Tests execute in this sequence:

1. **login.robot** - Establishes session (runs first, required)
2. **system_config.robot** - System configuration tests
3. **network_config.robot** - Network tests
4. **journal.robot** - Journal tests
5. **database.robot** - Database tests
6. **application.robot** - Application tests
7. **logout.robot** - Session cleanup (runs last, always executes)

The order is defined in `run_suites.sh` in the `SUITE_NAMES` array.

## Test Results

Results are organized by LPAR under the `results/` directory:

```
results/LPAR_NAME/
├── suites/
│   ├── output_login.xml          # Robot Framework XML output
│   ├── log_login.html             # Detailed execution log
│   ├── report_login.html          # Summary report
│   ├── output_system_config.xml
│   ├── log_system_config.html
│   └── ...
└── screenshots/
    ├── screen_20260111_120000.png  # Screen captures from tests
    └── ...
```

**Note**: `.txt` screenshot files are automatically cleaned up after test execution; only `.png` files are preserved.

## Adding Custom Tests

### Creating a New Common Test

1. Create `tests/common/new_test.robot`:
   ```robot
   *** Settings ***
   Documentation    Description of what this test validates
   Resource    ../../resources/common.robot

   *** Test Cases ***
   Test Name
       [Documentation]    Specific test case description
       [Tags]    category    subcategory
       
       Execute Command And Verify    YOUR_COMMAND
       Send Special Key    F3
   ```

2. Add to execution order in `run_suites.sh`:
   ```bash
   SUITE_NAMES=(
       "system_config.robot"
       # ... existing tests ...
       "new_test.robot"  # Add here
   )
   ```

3. Test execution:
   ```bash
   ./run_suites.sh YOUR_LPAR
   ```

### Creating an LPAR-Specific Override

1. Create `tests/LPAR_NAME/existing_test.robot` with same structure as common version

2. Customize test cases or add LPAR-specific tests

3. The script will automatically use the LPAR-specific version instead of common

## Shared Resources

Common keywords are defined in `resources/common.robot`:

### Session Management
- `Open Session To Host` - Starts TN5250 session
- `Close Session` - Terminates TN5250 session

### Authentication
- `Verify Sign On Screen` - Waits for sign-on screen
- `Login With Credentials` - Enters username and password
- `Verify Login Success` - Confirms authentication
- `Continue Login Session` - Proceeds past sign-on info screen

### Command Execution
- `Execute Command And Verify` - Types command, presses Enter, captures screen
- `Sign Off Session` - Executes SIGNOFF command

These keywords utilize the TN5250Library for low-level terminal interaction.

## Writing Effective Tests

### Best Practices

1. **Use descriptive names**: Test case names should clearly state what is being validated
2. **Add documentation**: Always include `[Documentation]` for test cases
3. **Tag appropriately**: Use relevant tags for filtering
4. **Capture screens**: Use `Capture Screen    image=True` for visual verification
5. **Clean up navigation**: Use `Send Special Key    F3` to return to command entry
6. **Follow Gherkin style**: Use Given/When/Then pattern for clarity

### Example Test Case

```robot
*** Test Cases ***
Verify System Configuration
    [Documentation]    Confirms OS/400 product license (5770SS1 feature 5051) is valid.
    [Tags]    system    configuration
    
    # Given: User is authenticated
    # When: License info is requested
    Execute Command And Verify    DSPLICKEY PRDID(5770SS1) FEATURE(5051)
    # Then: Screen is captured for verification
```

## Troubleshooting

### Tests Failing to Start

**Issue**: "Error: LPAR directory does not exist"

**Solution**: Create required directories:
```bash
mkdir tests/LPAR_NAME
mkdir -p results/LPAR_NAME/{suites,screenshots}
```

### Authentication Failures

**Issue**: "Timeout: Text 'Sign On' not found on screen"

**Solutions**:
- Verify `TN5250_HOST` is correct and reachable
- Check `TN5250_SSL` setting matches host requirements
- Verify network connectivity to IBM i system
- Check `.devcontainer/hosts.conf` for correct IP mapping

### Login Credential Errors

**Issue**: "Timeout: Text 'Sign-on Information' not found"

**Solutions**:
- Verify `TN5250_USER` and `TN5250_PASS` are correct
- Check user profile is not disabled on IBM i
- Verify user has appropriate authorities
- Check if password has expired

### Screen Capture Issues

**Issue**: Screenshots not being generated

**Solutions**:
- Verify ImageMagick is installed (for PNG images)
- Check `results/LPAR_NAME/screenshots/` directory exists
- Ensure sufficient disk space
- Check log files for specific error messages

## Continuous Integration

For CI/CD integration:

1. **Build Docker image**:
   ```bash
   docker build -t tn5250-rt .
   ```

2. **Run tests**:
   ```bash
   docker run --rm \
     -v $(pwd)/results:/app/results \
     -e TN5250_HOST=your_host \
     -e TN5250_USER=your_user \
     -e TN5250_PASS=your_password \
     -e TN5250_SSL=1 \
     tn5250-rt \
     ./run_suites.sh LPAR_NAME
   ```

3. **Collect results**:
   - Results available in `results/LPAR_NAME/suites/`
   - Exit code indicates pass/fail

## Further Reading

- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [TN5250Library Documentation](../docs/TN5250Library.html)
- [Architecture Documentation](../docs/ARCHITECTURE.md)
- [Password Security](../docs/PASSWORD_SECURITY.md)
