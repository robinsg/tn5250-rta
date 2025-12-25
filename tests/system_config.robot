*** Settings ***
Documentation    Test Suite: IBM i System Configuration Verification
...
...              This test suite validates system configuration and status on the
...              IBM i platform. It ensures that critical system settings are correct
...              and the system is operating in a healthy state.
...
...              Prerequisites:
...              - Authenticated TN5250 session
...              - User must have authority to display system values and configuration
...              - System must have required licenses installed
...
...              Test Coverage:
...              - License key verification
...              - System value configuration
...              - System status and health checks
...
...              Notes:
...              Tests verify OS/400 licensing and security configuration

Resource    ../resources/common.robot

*** Test Cases ***
Verify System Configuration
    [Documentation]    Verifies basic system configuration
    ...
    ...                Purpose:
    ...                Confirms that required OS/400 features and licenses are properly
    ...                configured on the system.
    ...
    ...                Expected Behavior:
    ...                - DSPLICKEY command executes successfully
    ...                - Product 5770SS1 (OS/400) license is valid
    ...                - Feature 5051 information is displayed
    ...
    ...                Prerequisites:
    ...                - User must have authority to display license information
    ...                - OS/400 must be installed and licensed
    ...
    ...                Notes:
    ...                5770SS1 is the IBM i Operating System product ID
    ...                Feature 5051 represents a specific OS component
    [Tags]    system    configuration
    
    Execute Command And Verify    DSPLICKEY PRDID(5770SS1) FEATURE(5051)
    
Verify System Status
    [Documentation]    Checks system status and health
    ...
    ...                Purpose:
    ...                Validates critical system values and settings to ensure the
    ...                system is configured correctly and operating properly.
    ...
    ...                Expected Behavior:
    ...                - DSPSYSVAL command executes successfully
    ...                - QSECURITY system value is displayed
    ...                - System value has an appropriate setting
    ...
    ...                Prerequisites:
    ...                - User must have authority to display system values
    ...                - System must be operational
    ...
    ...                Notes:
    ...                QSECURITY controls the security level (10-50)
    ...                Level 40 or 50 is recommended for production systems
    [Tags]    system    status
    Send Special Key    F3
    Execute Command And Verify    DSPSYSVAL SYSVAL(QSECURITY)
    Send Special Key    F3

