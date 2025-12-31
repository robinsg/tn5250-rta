"""
Robot Framework variables file for TN5250 tests.
Loads environment variables for TN5250 connection and test data.
"""
import os

# TN5250 Connection Variables
HOST = os.environ.get("TN5250_HOST", "localhost")
USER = os.environ.get("TN5250_USER", "")
PASS = os.environ.get("TN5250_PASS", "")
DEVNAME = os.environ.get("TN5250_DEVNAME", "")
MAP = os.environ.get("TN5250_MAP", "285")
SSL = os.environ.get("TN5250_SSL", "0")

# Test Data Variables
DSPLIB = os.environ.get("DSPLIB", "3000")
DSPLICKEY = os.environ.get("DSPLICKEY", "6")
NETSTAT = os.environ.get("NETSTAT", "127.0.0.1")
QSECURITY = os.environ.get("QSECURITY", "40")
RUNQRY = os.environ.get("RUNQRY", "13 Myrtle Dr")
WRKCFGSTS = os.environ.get("WRKCFGSTS", "ETHLIN02,ACTIVE")
WRKJRN = os.environ.get("WRKJRN", "QAUDJRN")
