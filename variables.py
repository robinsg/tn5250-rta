"""
Variable file for Robot Framework TN5250 tests.

Loads environment variables and converts sensitive values to Secret type
to prevent them from being logged in clear text.
"""

import os
from robot.utils import Secret


def get_variables():
    """
    Load environment variables for TN5250 testing.
    
    Returns a dictionary of variables with the password converted to Secret type
    to prevent logging in clear text.
    
    Environment variables loaded (with TN5250_ prefix):
    - TN5250_HOST: Hostname or IP address
    - TN5250_USER: Username for sign-on
    - TN5250_PASS: Password for sign-on (converted to Secret)
    - TN5250_SSL: SSL flag (0 or 1)
    - TN5250_DEVNAME: Optional device name
    - TN5250_MAP: Optional keyboard map number
    """
    variables = {
        'HOST': os.environ.get('TN5250_HOST', ''),
        'USER': os.environ.get('TN5250_USER', ''),
        'PASS': Secret(os.environ.get('TN5250_PASS', '')),
        'SSL': os.environ.get('TN5250_SSL', '0'),
        'DEVNAME': os.environ.get('TN5250_DEVNAME', ''),
        'MAP': os.environ.get('TN5250_MAP', '285'),
    }
    
    return variables
