*** Settings ***
Resource    ../resources/common.robot

*** Test Cases ***
Verify Network Configuration
    [Documentation]    Verifies network interface configuration
    [Tags]    network    configuration
    
    Execute Command And Verify    DSPNETA
    Send Special Key    F3
    Execute Command And Verify    WRKCFGSTS *LIN *ELAN

Verify Network Connectivity
    [Documentation]    Tests network connectivity and routing
    [Tags]    network    connectivity
    
    Send Special Key    F3
    Execute Command And Verify    NETSTAT *IFC
    Send Special Key    F3
    