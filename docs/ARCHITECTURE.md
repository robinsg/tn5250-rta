# TN5250-RT Architecture

## System Overview

TN5250-RT is a Robot Framework-based test automation suite designed for headless testing of IBM i systems via TN5250 terminal emulation. The architecture emphasizes automation, security, and multi-environment support.

## Component Architecture

### Layer 1: Test Orchestration
**Robot Framework Test Suites** (`tests/`)
- Declarative test definitions using Robot Framework DSL
- Gherkin-style (Given/When/Then) test organization
- Tag-based filtering for test execution control
- Multi-LPAR support with override capabilities

### Layer 2: Test Library
**TN5250Library** (`libraries/TN5250Library.py`)
- Python-based Robot Framework library
- Provides keywords for TN5250 interaction
- Manages tmux session lifecycle
- Handles screen verification and capture
- Implements password security via Secret type

### Layer 3: Terminal Multiplexing
**tmux**
- Provides headless terminal sessions
- Standard 80x24 screen dimensions
- Session persistence across test cases
- Background execution for CI/CD compatibility

### Layer 4: Terminal Emulation
**tn5250 Emulator**
- Compiled from source (v0.18)
- SSL/TLS connection support
- TN5250 protocol implementation
- Character map support (default: 285)

### Layer 5: Target System
**IBM i (AS/400)**
- Target system under test
- TN5250 server endpoint

## Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│ Test Suite Execution                                          │
│                                                                │
│  1. run_suites.sh LPAR_NAME [args]                           │
│     ├─ Loads .envs/.env.sh.LPAR_NAME                         │
│     ├─ Exports LPAR_NAME environment variable                │
│     └─ Executes Robot Framework with tag filters            │
│                                                                │
│  2. Login Suite (login.robot)                                │
│     ├─ Open Session To Host                                  │
│     │  └─ Start TN5250 Session (hostname, ssl, devname, map) │
│     │     └─ tmux new-session -d tn5250 [ssl:]hostname       │
│     ├─ Verify Sign On Screen                                 │
│     ├─ Login With Credentials (USER, PASS)                   │
│     │  └─ Send Text/Special Key via tmux                     │
│     └─ Verify Login Success                                  │
│        └─ Screen Should Contain "Sign-on Information"        │
│                                                                │
│  3. Test Suites (system, network, journal, database, app)    │
│     ├─ Execute Command And Verify                            │
│     │  ├─ Send Text <command>                                │
│     │  ├─ Send Special Key Enter                             │
│     │  └─ Capture Screen (text + optional PNG)               │
│     └─ Share existing tmux session                           │
│                                                                │
│  4. Logout Suite (logout.robot)                              │
│     ├─ Sign Off Session                                      │
│     │  └─ Send Text "signoff"                                │
│     └─ Close Session (Suite Teardown)                        │
│        └─ Stop TN5250 Session                                │
│           └─ tmux kill-session                               │
└──────────────────────────────────────────────────────────────┘
```

## Multi-LPAR Support

### Directory Structure

```
tests/
├── common/              # Shared tests (default)
│   ├── login.robot
│   ├── logout.robot
│   ├── system_config.robot
│   ├── network_config.robot
│   ├── journal.robot
│   ├── database.robot
│   └── application.robot
├── DEV400/              # LPAR-specific overrides
│   └── (optional custom tests)
└── PROD500/             # Different LPAR
    └── (optional custom tests)

results/
├── DEV400/
│   ├── suites/          # Test results (XML, HTML)
│   └── screenshots/     # Screen captures (PNG)
└── PROD500/
    ├── suites/
    └── screenshots/
```

### Resolution Order

When `run_suites.sh` is executed for an LPAR:
1. Check `tests/LPAR_NAME/<test>.robot` (LPAR-specific)
2. Fall back to `tests/common/<test>.robot` (shared)

This allows:
- Shared tests for common functionality
- LPAR-specific overrides for unique environments
- Custom tests per LPAR

### Environment Configuration

Each LPAR has its own environment file:
```
.envs/
├── .env.sh.dev400       # DEV400 credentials
├── .env.sh.prod500      # PROD500 credentials
└── .env.sh.template     # Template for new LPARs
```

Environment variables:
- `TN5250_HOST` - Hostname or IP address
- `TN5250_USER` - Username for authentication
- `TN5250_PASS` - Password (converted to Secret)
- `TN5250_SSL` - SSL flag (0 or 1)
- `TN5250_DEVNAME` - Optional device name
- `TN5250_MAP` - Character map number (default: 285)
- `LPAR_NAME` - Set by run_suites.sh for result organization

## Security Architecture

### Password Protection

**Problem**: Passwords logged in clear text in Robot Framework reports

**Solution**: Multi-layered security approach

1. **Secret Type** (`variables.py`)
   ```python
   from robot.utils import Secret
   'PASS': Secret(os.environ.get('TN5250_PASS', ''))
   ```
   - Robot Framework displays as `<secret>` in logs
   - Actual value accessible via `.value` property

2. **Library Support** (`TN5250Library.send_text()`)
   ```python
   actual_text = text.value if isinstance(text, Secret) else text
   self._log(f"Typing: '{text}'")  # Logs <secret>
   subprocess.run(["tmux", "send-keys", "-t", self.session_name, actual_text])
   ```
   - Extracts actual password for tmux
   - Logs obfuscated version

3. **Keyword Removal** (`run_suites.sh`)
   ```bash
   robot --removekeywords NAME:Login* ...
   ```
   - Removes entire login keyword tree from HTML reports

4. **File Exclusion** (`.gitignore`)
   - Environment files with credentials
   - DevContainer customer configs
   - Test results with potential sensitive data

### Network Security

- SSL/TLS support via `ssl:hostname` prefix
- Configurable per LPAR via `TN5250_SSL` environment variable
- Character map validation

## Session Management

### Session Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ Session States                                          │
│                                                          │
│  [No Session]                                           │
│       │                                                  │
│       │ Start TN5250 Session                            │
│       ▼                                                  │
│  [tmux Session Created]                                 │
│       │                                                  │
│       │ tn5250 connects                                 │
│       │ SSL handshake (if enabled)                      │
│       ▼                                                  │
│  [Connected - Sign On Screen]                           │
│       │                                                  │
│       │ Login With Credentials                          │
│       ▼                                                  │
│  [Authenticated - Ready]                                │
│       │                                                  │
│       │ Test suites execute                             │
│       │ (session shared)                                │
│       ▼                                                  │
│  [Tests Complete]                                       │
│       │                                                  │
│       │ Sign Off Session                                │
│       ▼                                                  │
│  [Signed Off]                                           │
│       │                                                  │
│       │ Stop TN5250 Session                             │
│       ▼                                                  │
│  [Session Terminated]                                   │
└─────────────────────────────────────────────────────────┘
```

### Session Cleanup

The `run_suites.sh` script uses a bash trap to ensure logout always runs:

```bash
cleanup() {
    local exit_code=$?
    if [ "$LOGIN_SUCCESSFUL" = true ]; then
        robot ... "$LOGOUT_SUITE"
    fi
    exit $exit_code
}
trap cleanup EXIT
```

This guarantees session termination even on test failures.

## Screen Verification

### Text Matching

`Screen Should Contain` keyword polls the screen:

```python
def screen_should_contain(self, expected_text, timeout=10):
    start_time = time.time()
    while time.time() - start_time < int(timeout):
        result = subprocess.run([
            "tmux", "capture-pane", "-p", "-t", self.session_name
        ], capture_output=True, text=True)
        if expected_text in result.stdout:
            return True
        time.sleep(0.5)
    raise AssertionError(f"Timeout: Text '{expected_text}' not found")
```

- Polls every 0.5 seconds
- Configurable timeout
- Dumps screen on failure for debugging

### Screenshot Capture

Two formats supported:

1. **Text** (`.txt`) - Always generated
   - Raw tmux pane capture
   - Used for debugging
   - Cleaned up after test completion

2. **Image** (`.png`) - Optional via `image=True`
   - Generated using ImageMagick
   - Monospace font rendering
   - Preserved for test reports

Screenshots organized by LPAR:
```
results/${LPAR_NAME}/screenshots/
├── screen_20260111_120000.txt
├── screen_20260111_120000.png
└── ...
```

## Error Handling

### Subprocess Error Handling

All tmux/tn5250 operations use `subprocess.run()` with `check=True`:

```python
subprocess.run([...], check=True)
```

Raises `CalledProcessError` on failure, which Robot Framework catches and reports.

### Test Execution Flow

```
Login Suite
  │
  ├─ PASS → Continue to main tests
  │
  └─ FAIL → Abort all tests, skip to cleanup
             (LOGIN_SUCCESSFUL=false, no logout)

Main Test Suite
  │
  ├─ PASS → Continue to next suite
  │
  └─ FAIL → Abort remaining tests, run logout
             (EXIT via trap, cleanup runs logout)

Logout Suite
  │
  └─ Always runs if login was successful
     (via cleanup trap)
```

### Exit Codes

- `0` - All tests passed
- `1-251` - Test failures
- `252` - No tests matched tag filter (treated as skip, not error)

## Development Environment

### DevContainer Configuration

The project uses VS Code DevContainers for consistent development environments:

**Features**:
- Python 3.12 runtime
- Robot Framework 7.4
- tn5250 compiled with SSL support
- tmux, git, ImageMagick
- Dynamic host configuration via `hosts.conf`

**Setup**:
1. Copy `devcontainer.template.json` → `devcontainer.json`
2. Configure git user in `devcontainer.json`
3. Add hosts to `.devcontainer/hosts.conf`
4. Rebuild container (runs `setup-hosts.sh`)

### Build Process (Dockerfile)

**Stage 1: Builder**
- Compiles tn5250 v0.18 from source
- Enables SSL support via `--with-ssl`
- Generates binaries and shared libraries

**Stage 2: Runtime**
- Slim Python 3.12 base
- Copies tn5250 binaries and libraries
- Installs Robot Framework dependencies
- Configures library paths via `ldconfig`

## Test Execution Engine

### Sequential Execution

Tests run sequentially to share the session:

```bash
robot --exitonfailure \
      --removekeywords NAME:Login* \
      --output output.xml \
      --log log.html \
      --report report.html \
      $ROBOT_ARGS \
      "$SUITE"
```

Key flags:
- `--exitonfailure` - Stop on first failure
- `--removekeywords NAME:Login*` - Security (remove login details)
- `$ROBOT_ARGS` - User-provided tag filters

### Tag-Based Filtering

Common tags used:
- `login`, `logout` - Session management
- `smoke` - Critical path tests
- `system`, `network`, `database`, `application` - Functional areas
- `wip` - Work in progress (exclude from CI)

Example usage:
```bash
./run_suites.sh DEV400 --include smoke --exclude wip
```

## Logging and Reporting

### Output Artifacts

Per suite:
- `output_<suite>.xml` - Machine-readable results
- `log_<suite>.html` - Detailed execution log
- `report_<suite>.html` - Summary report

Organized by LPAR:
```
results/${LPAR_NAME}/suites/
├── output_login.xml
├── log_login.html
├── report_login.html
├── output_system_config.xml
├── ...
└── report_logout.html
```

### Verbose Mode

TN5250Library supports verbose console output:

```robot
Set TN5250 Verbose    True
```

When enabled:
- All library operations logged to console
- Screen content displayed on matches
- Useful for debugging test development

## Extensibility

### Adding New Keywords

Add methods to `TN5250Library.py`:

```python
def new_keyword(self, arg1, arg2="default"):
    """Keyword documentation.
    
    Args:
        arg1 (str): Description of arg1
        arg2 (str, optional): Description of arg2. Defaults to "default".
    
    Returns:
        type: Description of return value
    
    Raises:
        Exception: Description of when raised
    """
    # Implementation
    pass
```

Robot Framework automatically discovers methods as keywords.

### Adding New Test Suites

1. Create `tests/common/new_suite.robot`
2. Add to `SUITE_NAMES` array in `run_suites.sh`
3. Follow existing patterns (Resource, Documentation, Tags)

### LPAR-Specific Customization

Create `tests/LPAR_NAME/test.robot` to override common test:

```robot
*** Settings ***
Documentation    LPAR-specific version of test
Resource    ../../resources/common.robot

*** Test Cases ***
Custom Test For This LPAR
    [Tags]    custom
    Execute Command And Verify    CUSTOM_COMMAND
```

## Performance Considerations

### Session Reuse

- Login once, share session across all tests
- Reduces authentication overhead
- Faster test execution

### Screen Polling

- 0.5 second poll interval balances responsiveness and CPU
- Configurable timeouts prevent indefinite waits
- Early return on match

### Screenshot Cleanup

Text screenshots (`.txt`) deleted after test run:
```bash
find results/${LPAR_NAME}/screenshots -name "*.txt" -type f -delete
```

PNG images preserved for reporting.

## Future Enhancements

Potential areas for expansion:
- Parallel test execution across LPARs
- Test data management (external files, databases)
- Enhanced error recovery (retry logic)
- Performance metrics collection
- Integration with CI/CD pipelines (Jenkins, GitHub Actions)
- API for programmatic test execution

## References

- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [tn5250 Project](https://github.com/tn5250/tn5250)
- [tmux Manual](https://man7.org/linux/man-pages/man1/tmux.1.html)
- [IBM i Information Center](https://www.ibm.com/docs/en/i)
