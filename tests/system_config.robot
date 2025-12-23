*** Settings ***
Resource    ../resources/common.robot
Suite Setup    Open Session To Host
Suite Teardown    Close Session

*** Test Cases ***
Login To IBM i
    [Documentation]    Verifies successful login with valid credentials
    [Tags]    system   configuration    status
    
    Verify Sign On Screen
    Login With Credentials
    Verify Login Success
    Continue Login Session

Verify System Configuration
    [Documentation]    Verifies basic system configuration
    [Tags]    system    configuration
    
    Execute Command And Verify    DSPLICKEY PRDID(5770SS1) FEATURE(5051)
    
Verify System Status
    [Documentation]    Checks system status and health
    [Tags]    system    status
    Send Special Key    F3
    Execute Command And Verify    DSPSYSVAL SYSVAL(QSECURITY)

