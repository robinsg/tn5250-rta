*** Settings ***
Documentation    Validates IBM i login process via TN5250 emulation.
...              Requires valid credentials in environment variables (USER, PASS).

Resource    ../resources/common.robot
Suite Setup    Open Session To Host

*** Test Cases ***
Login To IBM i
    [Documentation]    Validates complete login flow from sign-on screen to authenticated session.
    ...                Captures screen for troubleshooting.
    [Tags]    login    smoke
    
    # Debug: Capture initial screen to see what's actually displayed
    Sleep    2s    # Give screen time to render
    Capture Screen    initial_screen    image=True
    
    Verify Sign On Screen
    Login With Credentials
    Verify Login Success
    Continue Login Session    
     
