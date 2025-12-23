*** Settings ***
Resource    ../resources/common.robot

*** Test Cases ***
Verify System Configuration
    [Documentation]    Verifies basic system configuration
    [Tags]    system    configuration
    
    Execute Command And Verify    DSPLICKEY PRDID(5770SS1) FEATURE(5051)
    
Verify System Status
    [Documentation]    Checks system status and health
    [Tags]    system    status
    Send Special Key    F3
    Execute Command And Verify    DSPSYSVAL SYSVAL(QSECURITY)

