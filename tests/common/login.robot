*** Settings ***
Documentation       Validates IBM i login process via TN5250 emulation.
...                 Requires valid credentials in environment variables (USER, PASS).

Resource            ../../resources/common.resource

Suite Setup         Open Session To Host


*** Test Cases ***
Login To IBM i
    [Documentation]    Validates complete login flow from sign-on screen to authenticated session.
    ...    Captures screen for troubleshooting.
    [Tags]    login    smoke

    Wait Until Keyword Succeeds    10s    2s    Verify Sign On Screen
    Capture Screen    initial_screen    image=True

    Login With Credentials
    Verify Login Success
    Continue Login Session
