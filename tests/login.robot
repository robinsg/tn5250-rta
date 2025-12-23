*** Settings ***
Resource    ../resources/common.robot
Suite Setup    Open Session To Host

*** Test Cases ***
Login To IBM i
    [Documentation]    Verifies successful login with valid credentials
    [Tags]    login    smoke
    
    # Debug: Capture initial screen to see what's actually displayed
    Sleep    2s    # Give screen time to render
    Capture Screen    initial_screen    image=True
    
    Verify Sign On Screen
    Login With Credentials
    Verify Login Success
    Continue Login Session    
     
