# Password Obfuscation Implementation

## Overview

This document describes the password obfuscation feature implemented to prevent passwords from being displayed in clear text in console output and Robot Framework logs.

## Problem Statement

Previously, when using the `Login With Credentials` keyword, passwords were logged in clear text to both:
- Console output (when verbose mode is enabled)
- Robot Framework log files

This posed a security risk as sensitive credentials could be exposed in log files, screenshots, or during live demonstrations.

## Solution

A new `send_password` method was added to the `TN5250Library` class that:
1. **Sends the actual password to the TN5250 session** (functionality unchanged)
2. **Logs a random obfuscated string instead** of the actual password
3. **Uses random characters** (letters, digits, and special characters)
4. **Uses a different length** than the actual password (8-16 characters) to prevent length-based analysis

## Implementation Details

### New Method: `send_password`

```python
def send_password(self, password):
    """Types a password into the terminal with obfuscated logging.
    
    Sends the password to the active TN5250 session as keyboard input,
    but logs a random obfuscated string instead of the actual password.
    The obfuscated string uses random characters and has a different
    length than the actual password to prevent length-based attacks.
    
    Args:
        password (str): The password to type into the terminal.
    
    Returns:
        None
    
    Raises:
        subprocess.CalledProcessError: If sending keys to tmux fails.
    """
```

### Updated Keyword: `Login With Credentials`

The `Login With Credentials` keyword in `resources/common.robot` was updated to use `Send Password` instead of `Send Text` for the password field:

```robot
Login With Credentials
    [Documentation]    Enters username and password on sign-on screen, then submits.
    ...                Args: username (default: ${USER}), password (default: ${PASS}).
    [Arguments]    ${username}=${USER}    ${password}=${PASS}
    Send Text    ${username}
    Send Special Key    Tab
    Send Password    ${password}    # Changed from Send Text
    Send Special Key    Enter
```

## Security Features

1. **Actual Password Transmitted**: The real password is sent to the TN5250 session, ensuring login functionality is not affected.

2. **Obfuscated Logging**: Log entries show random characters instead of the actual password.

3. **Variable Length Obfuscation**: The obfuscated string length (8-16 chars) differs from the actual password length, preventing length-based attacks.

4. **Random Character Generation**: Uses a mix of:
   - Uppercase letters (A-Z)
   - Lowercase letters (a-z)
   - Digits (0-9)
   - Special characters (!@#$%^&*)

## Example Output

### Before (Insecure):
```
Typing: 'MySecretPassword123'
```

### After (Secure):
```
Typing password: 'K7v@xP2nQ$'
```

Note: The actual password `MySecretPassword123` is 19 characters, but the obfuscated log shows 10 random characters.

## Testing

Comprehensive unit tests are provided in `tests/unit_test_password_obfuscation.py` that verify:
- ✓ Actual passwords are sent to the terminal
- ✓ Passwords are obfuscated in logs
- ✓ Obfuscated passwords use random characters
- ✓ Obfuscated passwords have different lengths than actual passwords
- ✓ The `send_text` method still logs plaintext for non-passwords

Run tests with:
```bash
python3 tests/unit_test_password_obfuscation.py
```

## Demonstration

A demonstration script is available to show the obfuscation in action:
```bash
python3 tests/demonstrate_password_obfuscation.py
```

## Backward Compatibility

- The `send_text` method remains unchanged for non-password fields
- Existing tests continue to work without modification
- Only password-specific calls use the new `send_password` method

## Usage

### In Robot Framework Tests

Use the `Send Password` keyword for password fields:

```robot
Send Password    ${MY_PASSWORD_VARIABLE}
```

### In Python Library Calls

```python
from TN5250Library import TN5250Library

lib = TN5250Library()
lib.send_password("my_secret_password")
```

## Security Considerations

1. **Environment Variables**: Passwords should still be stored in `.env` files that are excluded from version control
2. **Log File Protection**: Protect access to Robot Framework HTML/XML reports even with obfuscation
3. **Screen Captures**: Be cautious when capturing screens during password entry
4. **Tmux Sessions**: The tmux session history still contains the actual password characters

## Future Enhancements

Potential future improvements:
- Add configuration option for obfuscation length range
- Support for custom obfuscation character sets
- Integration with password managers
- Clear tmux history buffer after password entry

## References

- Issue: #[issue_number] - Ensure password is not shown in clear text on console or in robot reports
- Python Library: `libraries/TN5250Library.py`
- Robot Keywords: `resources/common.robot`
- Unit Tests: `tests/unit_test_password_obfuscation.py`
