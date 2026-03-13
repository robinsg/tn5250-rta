*** Settings ***
Documentation       Validates IBM i network configuration and connectivity.
...                 Tests network interfaces, status, and routing.

Resource            ../../resources/common.resource


*** Test Cases ***
Verify Network Configuration
    [Documentation]    Confirms network attributes (DSPNETA) and line/Ethernet status (WRKCFGSTS).
    ...    DSPNETA: Verifies host name appears 3 times in lines 3 to 7 (case-insensitive).
    ...    WRKCFGSTS: Verifies all values in ${WRKCFGSTS} appear on the same line.
    [Tags]    network    configuration

    Execute Command And Verify    DSPNETA
    Verify Occurrence Count    ${HOST}    3    7    3    case_sensitive=False
    Send Special Key    F3
    Execute Command And Verify    WRKCFGSTS *LIN *ELAN
    Verify All Values On Same Line    ${WRKCFGSTS}

Verify Network Connectivity
    [Documentation]    Displays interface statistics (NETSTAT *IFC) showing IP addresses and status.
    ...    Verifies IP address in lines 10 to 20 equals ${NETSTAT} and appears only 1 time.
    [Tags]    network    connectivity

    Send Special Key    F3
    Execute Command And Verify    NETSTAT *IFC
    Verify Occurrence Count    ${NETSTAT}    10    20    1
    Send Special Key    F3
