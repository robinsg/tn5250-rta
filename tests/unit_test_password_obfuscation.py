#!/usr/bin/env python3
"""
Unit test for password obfuscation in TN5250Library.

This test validates that the send_password method properly obfuscates
passwords in logs while still sending the actual password to the terminal.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
import random

# Add libraries directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libraries'))

from TN5250Library import TN5250Library


class TestPasswordObfuscation(unittest.TestCase):
    """Test cases for password obfuscation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.lib = TN5250Library(verbose=True)

    @patch('TN5250Library.subprocess.run')
    @patch('TN5250Library.logger')
    def test_send_password_obfuscates_in_logs(self, mock_logger, mock_subprocess):
        """Test that send_password logs obfuscated password, not actual password."""
        actual_password = "MySecretPassword123!"
        
        # Call send_password
        self.lib.send_password(actual_password)
        
        # Verify subprocess.run was called with actual password
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        self.assertEqual(args[0][-1], actual_password, "Actual password should be sent to tmux")
        
        # Verify logger was called with obfuscated password
        mock_logger.info.assert_called_once()
        logged_message = mock_logger.info.call_args[0][0]
        
        # Verify the actual password is NOT in the log
        self.assertNotIn(actual_password, logged_message, 
                        "Actual password should not appear in logs")
        
        # Verify the log contains "password" indicator
        self.assertIn("password", logged_message.lower(), 
                     "Log should indicate this is a password")

    @patch('TN5250Library.subprocess.run')
    @patch('TN5250Library.logger')
    def test_obfuscated_password_has_different_length(self, mock_logger, mock_subprocess):
        """Test that obfuscated password has different length than actual password."""
        # Test with various password lengths
        test_passwords = [
            "short",           # 5 chars
            "medium_pass",     # 11 chars
            "very_long_password_with_many_characters",  # 40 chars
        ]
        
        for actual_password in test_passwords:
            mock_logger.reset_mock()
            mock_subprocess.reset_mock()
            
            self.lib.send_password(actual_password)
            
            # Get the logged message
            logged_message = mock_logger.info.call_args[0][0]
            
            # Extract the obfuscated password from the log message
            # Format is: "Typing password: 'OBFUSCATED'"
            start_idx = logged_message.find("'") + 1
            end_idx = logged_message.rfind("'")
            obfuscated = logged_message[start_idx:end_idx]
            
            # Verify obfuscated password length is between 8-16 (as per implementation)
            self.assertGreaterEqual(len(obfuscated), 8, 
                                  f"Obfuscated password should be at least 8 chars")
            self.assertLessEqual(len(obfuscated), 16, 
                               f"Obfuscated password should be at most 16 chars")
            
            # For most passwords, verify different length
            if len(actual_password) < 8 or len(actual_password) > 16:
                self.assertNotEqual(len(obfuscated), len(actual_password),
                                  f"Obfuscated length should differ from actual password length")

    @patch('TN5250Library.subprocess.run')
    @patch('TN5250Library.logger')
    def test_obfuscated_password_uses_random_characters(self, mock_logger, mock_subprocess):
        """Test that obfuscated passwords use random characters."""
        actual_password = "TestPassword123"
        
        # Call send_password multiple times and collect obfuscated values
        obfuscated_values = []
        for _ in range(10):
            mock_logger.reset_mock()
            self.lib.send_password(actual_password)
            
            logged_message = mock_logger.info.call_args[0][0]
            start_idx = logged_message.find("'") + 1
            end_idx = logged_message.rfind("'")
            obfuscated = logged_message[start_idx:end_idx]
            obfuscated_values.append(obfuscated)
        
        # Verify that we got different obfuscated values (randomness check)
        unique_values = set(obfuscated_values)
        self.assertGreater(len(unique_values), 1, 
                          "Obfuscated passwords should be random, not always the same")

    @patch('TN5250Library.subprocess.run')
    def test_send_text_still_logs_plaintext(self, mock_subprocess):
        """Test that send_text still logs text in plain (for non-passwords)."""
        # This ensures we didn't break the normal send_text functionality
        test_text = "username123"
        
        with patch.object(self.lib, '_log') as mock_log:
            self.lib.send_text(test_text)
            
            # Verify _log was called with the actual text
            mock_log.assert_called_once()
            logged_message = mock_log.call_args[0][0]
            self.assertIn(test_text, logged_message, 
                         "send_text should log actual text for non-passwords")

    @patch('TN5250Library.subprocess.run')
    @patch('TN5250Library.logger')
    def test_send_password_calls_subprocess_correctly(self, mock_logger, mock_subprocess):
        """Test that send_password calls subprocess with correct parameters."""
        actual_password = "CorrectPassword456"
        
        self.lib.send_password(actual_password)
        
        # Verify subprocess.run was called with correct tmux command structure
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        
        # Check command structure: ["tmux", "send-keys", "-t", session_name, password]
        self.assertEqual(args[0][0], "tmux")
        self.assertEqual(args[0][1], "send-keys")
        self.assertEqual(args[0][2], "-t")
        self.assertEqual(args[0][3], self.lib.session_name)
        self.assertEqual(args[0][4], actual_password)
        self.assertEqual(kwargs.get('check'), True)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
