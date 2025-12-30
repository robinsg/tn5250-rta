*** Settings ***
Documentation    Validates IBM i network configuration and connectivity.
...              Tests network interfaces, status, and routing.

Resource    ../../resources/common.robot

*** Test Cases ***
Verify Network Configuration
    [Documentation]    Confirms network attributes (DSPNETA) and line/Ethernet status (WRKCFGSTS).
    [Tags]    network    configuration
    
    Execute Command And Verify    DSPNETA
    Send Special Key    F3
    Execute Command And Verify    WRKCFGSTS *LIN *ELAN

Verify Network Connectivity
    [Documentation]    Displays interface statistics (NETSTAT *IFC) showing IP addresses and status.
    [Tags]    network    connectivity
    
    Send Special Key    F3
    Execute Command And Verify    NETSTAT *IFC
    Send Special Key    F3
    