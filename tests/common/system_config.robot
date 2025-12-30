*** Settings ***
Documentation    Validates IBM i system configuration and status.
...              Checks OS/400 licensing (5770SS1) and security settings (QSECURITY).

Resource    ../resources/common.robot

*** Test Cases ***
Verify System Configuration
    [Documentation]    Confirms OS/400 product license (5770SS1 feature 5051) is valid.
    [Tags]    system    configuration
    
    Execute Command And Verify    DSPLICKEY PRDID(5770SS1) FEATURE(5051)
    
Verify System Status
    [Documentation]    Checks QSECURITY system value. Level 40 or 50 recommended for production.
    [Tags]    system    status
    Send Special Key    F3
    Execute Command And Verify    DSPSYSVAL SYSVAL(QSECURITY)
    Send Special Key    F3

