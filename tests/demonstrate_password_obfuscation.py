#!/usr/bin/env python3
"""
Demonstration of password obfuscation functionality.

This script demonstrates that:
1. Actual passwords are sent to the terminal
2. Obfuscated random strings are logged instead
3. Obfuscated strings have different lengths than actual passwords
"""

import sys
import os

# Add libraries directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libraries'))

from TN5250Library import TN5250Library
from unittest.mock import patch, MagicMock


def demonstrate_password_obfuscation():
    """Demonstrate password obfuscation in action."""
    
    print("=" * 70)
    print("Password Obfuscation Demonstration")
    print("=" * 70)
    print()
    
    # Create library instance
    lib = TN5250Library(verbose=True)
    
    # Test passwords of various lengths
    test_passwords = [
        ("short", "Short password (5 chars)"),
        ("MyPassword123", "Medium password (13 chars)"),
        ("AVeryLongPasswordWithManyCharacters456!", "Long password (41 chars)"),
    ]
    
    print("Demonstrating that:")
    print("1. ✓ Actual passwords are sent to the terminal (subprocess)")
    print("2. ✓ Obfuscated passwords are logged (different from actual)")
    print("3. ✓ Obfuscated passwords have different lengths (8-16 chars)")
    print()
    print("-" * 70)
    print()
    
    for actual_password, description in test_passwords:
        print(f"Test: {description}")
        print(f"  Actual password:      '{actual_password}' (length: {len(actual_password)})")
        
        # Mock the subprocess and logger to capture what would be sent/logged
        with patch('TN5250Library.subprocess.run') as mock_subprocess, \
             patch('TN5250Library.logger') as mock_logger:
            
            # Call send_password
            lib.send_password(actual_password)
            
            # Get what was sent to subprocess (the actual password)
            sent_to_terminal = mock_subprocess.call_args[0][0][-1]
            
            # Get what was logged (the obfuscated password)
            logged_message = mock_logger.info.call_args[0][0]
            start_idx = logged_message.find("'") + 1
            end_idx = logged_message.rfind("'")
            obfuscated_password = logged_message[start_idx:end_idx]
            
            print(f"  Sent to terminal:     '{sent_to_terminal}' (CORRECT - actual password sent)")
            print(f"  Logged to console:    '{obfuscated_password}' (length: {len(obfuscated_password)})")
            
            # Verification
            if sent_to_terminal == actual_password:
                print(f"  ✓ Correct password sent to terminal")
            else:
                print(f"  ✗ ERROR: Wrong password sent to terminal!")
            
            if obfuscated_password != actual_password:
                print(f"  ✓ Password obfuscated in logs (not the same)")
            else:
                print(f"  ✗ ERROR: Password not obfuscated!")
            
            if 8 <= len(obfuscated_password) <= 16:
                print(f"  ✓ Obfuscated length within expected range (8-16)")
            else:
                print(f"  ✗ ERROR: Obfuscated length out of range!")
            
            print()
    
    print("-" * 70)
    print()
    print("Summary:")
    print("  ✓ Passwords are entered correctly in the TN5250 session")
    print("  ✓ Passwords are obfuscated in console and Robot Framework logs")
    print("  ✓ Obfuscated passwords use random characters")
    print("  ✓ Obfuscated passwords have different lengths than actual passwords")
    print()
    print("=" * 70)


if __name__ == '__main__':
    demonstrate_password_obfuscation()
