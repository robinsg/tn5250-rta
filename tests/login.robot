*** Settings ***
Documentation    Test Suite: IBM i Login Verification
...
...              This test suite validates the login process to an IBM i system
...              using TN5250 emulation. It verifies that users can successfully
...              authenticate with valid credentials and reach the main menu.
...
...              Prerequisites:
...              - IBM i system must be accessible via TN5250
...              - Valid credentials must be configured in environment variables
...              - TN5250 session must be established before tests run
...
...              Test Coverage:
...              - Sign-on screen detection
...              - Credential submission
...              - Login success verification
...              - Post-login navigation

Resource    ../resources/common.robot
Suite Setup    Open Session To Host

*** Test Cases ***
Login To IBM i
    [Documentation]    Verifies successful login with valid credentials
    ...
    ...                Purpose:
    ...                Validates the complete login flow from sign-on screen to authenticated session.
    ...
    ...                Expected Behavior:
    ...                - Sign-on screen is displayed
    ...                - Credentials are accepted
    ...                - Login success message appears
    ...                - User can continue to main menu
    ...
    ...                Prerequisites:
    ...                - TN5250 session is active
    ...                - Valid USER and PASS variables are set
    ...
    ...                Notes:
    ...                Includes debug screen capture to aid troubleshooting
    [Tags]    login    smoke
    
    # Debug: Capture initial screen to see what's actually displayed
    Sleep    2s    # Give screen time to render
    Capture Screen    initial_screen    image=True
    
    Verify Sign On Screen
    Login With Credentials
    Verify Login Success
    Continue Login Session    
     
