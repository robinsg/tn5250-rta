*** Settings ***
Documentation    Test Suite: IBM i Network Configuration Verification
...
...              This test suite validates network configuration and connectivity on
...              the IBM i system. It verifies that network interfaces are properly
...              configured and operational.
...
...              Prerequisites:
...              - Authenticated TN5250 session
...              - User must have authority to display network configuration
...              - Network interfaces must be configured
...
...              Test Coverage:
...              - Network interface configuration
...              - Line and interface status
...              - Network connectivity and routing
...
...              Notes:
...              Network validation ensures system accessibility and communication capabilities

Resource    ../resources/common.robot

*** Test Cases ***
Verify Network Configuration
    [Documentation]    Verifies network interface configuration
    ...
    ...                Purpose:
    ...                Confirms that network interfaces are properly configured and
    ...                that network attributes are set correctly.
    ...
    ...                Expected Behavior:
    ...                - DSPNETA displays network attributes
    ...                - WRKCFGSTS shows line and Ethernet configuration status
    ...                - All configured interfaces are shown
    ...                - F3 key returns to command line after each command
    ...
    ...                Prerequisites:
    ...                - Network interfaces must be configured
    ...                - User must have authority to display network information
    ...
    ...                Notes:
    ...                *LIN *ELAN displays all line and Ethernet configuration status
    [Tags]    network    configuration
    
    Execute Command And Verify    DSPNETA
    Send Special Key    F3
    Execute Command And Verify    WRKCFGSTS *LIN *ELAN

Verify Network Connectivity
    [Documentation]    Tests network connectivity and routing
    ...
    ...                Purpose:
    ...                Validates that network interfaces are active and operational,
    ...                and that routing is configured correctly.
    ...
    ...                Expected Behavior:
    ...                - NETSTAT *IFC displays interface statistics
    ...                - Active interfaces are shown with their status
    ...                - IP addresses and subnet masks are displayed
    ...                - F3 key returns to command line
    ...
    ...                Prerequisites:
    ...                - Network interfaces must be active
    ...                - TCP/IP must be started
    ...                - User must have authority to display network status
    ...
    ...                Notes:
    ...                *IFC parameter shows interface-specific statistics
    ...                Helps verify network layer connectivity
    [Tags]    network    connectivity
    
    Send Special Key    F3
    Execute Command And Verify    NETSTAT *IFC
    Send Special Key    F3
    