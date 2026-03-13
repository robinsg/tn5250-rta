*** Settings ***
Documentation       Validates IBM i system configuration and status.
...                 Checks OS/400 licensing (5770SS1) and security settings (QSECURITY).

Resource            ../../resources/common.resource


*** Test Cases ***
Verify System Configuration
    [Documentation]    Confirms OS/400 product license (5770SS1 feature 5051) is valid.
    ...    Verifies numeric processor count at row 14 columns 34 to 35 equals ${DSPLICKEY}.
    [Tags]    system    configuration

    Execute Command And Verify    DSPLICKEY PRDID(5770SS1) FEATURE(5051)
    Screen Should Contain At Position    14    34    34    ${DSPLICKEY}

Verify System Status
    [Documentation]    Checks QSECURITY system value. Level 40 or 50 recommended for production.
    ...    Verifies numeric value at row 7 columns 35 to 36 equals ${QSECURITY}.
    [Tags]    system    status
    Send Special Key    F3
    Execute Command And Verify    DSPSYSVAL SYSVAL(QSECURITY)
    Screen Should Contain At Position    7    35    36    ${QSECURITY}
    Send Special Key    F3
