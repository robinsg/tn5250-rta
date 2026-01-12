# Password Security Implementation

## Overview

This implementation uses Robot Framework's built-in `Secret` type to prevent passwords from being displayed in clear text in console output and Robot Framework HTML/XML reports.

## How It Works

### 1. Secret Type

The `variables.py` file loads environment variables and converts the password to a `Secret` type:

```python
from robot.utils import Secret

def get_variables():
    variables = {
        'HOST': os.environ.get('TN5250_HOST', ''),
        'USER': os.environ.get('TN5250_USER', ''),
        'PASS': Secret(os.environ.get('TN5250_PASS', '')),  # ← Converted to Secret
        'SSL': os.environ.get('TN5250_SSL', '0'),
        'DEVNAME': os.environ.get('TN5250_DEVNAME', ''),
        'MAP': os.environ.get('TN5250_MAP', '285'),
    }
    return variables
```

When a `Secret` object is logged, Robot Framework automatically displays it as `<secret>` instead of the actual value.

### 2. Library Support

The `TN5250Library.send_text()` method has been updated to handle `Secret` types:

```python
from robot.utils import Secret

def send_text(self, text):
    # Extract actual value from Secret if needed
    actual_text = text.value if isinstance(text, Secret) else text
    
    # Log shows '<secret>' for Secret objects
    self._log(f"Typing: '{text}'")
    
    # Send actual password value to terminal
    subprocess.run(["tmux", "send-keys", "-t", self.session_name, actual_text], check=True)
```

### 3. Remove Login Keywords from Logs

The `run_suites.sh` script includes the `--removekeywords NAME:Login*` option to remove all login-related keywords from the final HTML log:

```bash
robot \
    --removekeywords NAME:Login* \
    --output output.xml \
    --log log.html \
    "$LOGIN_SUITE"
```

This removes the entire `Login With Credentials` keyword and its details from the log file.

## Log Output Examples

### Console Output
```
[INFO] Typing: 'username123'
[INFO] Typing: '<secret>'         ← Password shown as <secret>
[INFO] Sending Key: Enter
```

### Robot Framework HTML Log

With `--removekeywords NAME:Login*`, the login keyword details are completely removed from the log:

```
✓ Login To IBM i
  Suite Setup: Open Session To Host
  [Login With Credentials keyword removed from log]
  ✓ Verify Login Success
```

## Configuration

### Environment Variables

Set these in `.envs/.env.sh.LPAR_NAME`:

```bash
export TN5250_HOST=your_host
export TN5250_USER=your_user
export TN5250_PASS=your_password  # Will be converted to Secret
export TN5250_SSL=1
```

### Running Tests

The `run_suites.sh` script automatically includes the necessary options:

```bash
./run_suites.sh dev400
```

For manual test runs, always include:

```bash
robot --removekeywords NAME:Login* tests/common/login.robot
```

## Security Benefits

1. **Secret Type**: Passwords are automatically obfuscated as `<secret>` in all logs
2. **Keyword Removal**: Login details are removed from HTML reports with `--removekeywords`
3. **Actual Value Sent**: The real password is still sent to the TN5250 session for authentication
4. **Built-in Support**: Uses Robot Framework's native security features

## Testing

Test that Secret type works correctly:

```python
from robot.utils import Secret
from variables import get_variables

vars = get_variables()
print(vars['PASS'])  # Output: <secret>
print(vars['PASS'].value)  # Output: actual_password
```

## References

- [Robot Framework Secret Type](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#hiding-sensitive-data)
- [--removekeywords documentation](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#removing-keywords)
