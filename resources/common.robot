*** Settings ***
Variables    variables.py
Library      libraries/TN5250Library.py    True

*** Keywords ***
Open Session To Host
    [Documentation]    Establishes a TN5250 session to the configured host
    Start TN5250 Session    ${HOST}    ssl=${SSL}    devname=${DEVNAME}    map=${MAP}

Close Session
    [Documentation]    Terminates the active TN5250 session
    Stop TN5250 Session

Verify Sign On Screen
    [Documentation]    Verifies the sign-on screen is displayed
    [Arguments]    ${timeout}=10
    Screen Should Contain    Sign On    timeout=${timeout}

Login With Credentials
    [Documentation]    Logs in with provided username and password
    [Arguments]    ${username}=${USER}    ${password}=${PASS}
    Send Text    ${username}
    Send Special Key    Tab
    Send Text    ${password}
    Send Special Key    Enter

Verify Login Success
    [Documentation]    Confirms login was successful by checking for sign-on info
    [Arguments]    ${timeout}=10
    Screen Should Contain    Sign-on Information    timeout=${timeout}

Continue Login Session
    [Documentation]    Completes the post-login flow
    Send Special Key    Enter

Execute Command And Verify
    [Documentation]    Sends a command and captures the screen
    [Arguments]    ${command}
    Send Text    ${command}
    Send Special Key    Enter
    Capture Screen    image=True

Sign Off Session
    [Documentation]    Gracefully signs off from the session
    Send Text    signoff
    Send Special Key    Enter
