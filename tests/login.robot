*** Settings ***
Resource    ../resources/common.robot
Suite Setup    Open Session To Host
Suite Teardown    Close Session

*** Test Cases ***
Login To Secure IBM i
    [Documentation]    Verifies successful login with valid credentials
    [Tags]    login    smoke
    
    Verify Sign On Screen
    Login With Credentials
    Verify Login Success
    Continue Login Session
    
Execute Command After Login
    [Documentation]    Verifies command execution after successful login
    [Tags]    login    smoke
    
    Execute Command And Verify    wrkactjob
    Sign Off Session    
     
