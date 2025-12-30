*** Settings ***
Documentation    Common keywords for TN5250 terminal emulation testing on IBM i.
...              Provides session management, authentication, and command execution.
...              Requires environment variables: HOST, USER, PASS, SSL, DEVNAME, MAP.
...              For HMC testing: HMC_HOST, HMC_PORT, HMC_USER, HMC_PASS, HMC_SYSNAME, HMC_LPAR, HMC_SHAREKEY.

Variables    ${EXECDIR}/variables.py
Library      ${EXECDIR}/libraries/TN5250Library.py    True

*** Keywords ***
Open Session To Host
    [Documentation]    Starts TN5250 session to IBM i using environment variables.
    ...                Typically used in Suite Setup.
    Start TN5250 Session    ${HOST}    ssl=${SSL}    devname=${DEVNAME}    map=${MAP}

Open HMC Console Session
    [Documentation]    Starts TN5250 session to HMC shared console using environment variables.
    ...                Typically used in Suite Setup for HMC testing.
    Start HMC Console Session    ${HMC_HOST}    ${HMC_PORT}    ${HMC_USER}    ${HMC_PASS}    ${HMC_SYSNAME}    ${HMC_LPAR}    ${HMC_SHAREKEY}

Close Session
    [Documentation]    Terminates the TN5250 session and cleans up resources.
    ...                Typically used in Suite Teardown.
    Stop TN5250 Session

Verify Sign On Screen
    [Documentation]    Waits for "Sign On" text to appear on screen.
    ...                Args: timeout (default: 10 seconds).
    [Arguments]    ${timeout}=10
    Screen Should Contain    Sign On    timeout=${timeout}

Login With Credentials
    [Documentation]    Enters username and password on sign-on screen, then submits.
    ...                Args: username (default: ${USER}), password (default: ${PASS}).
    [Arguments]    ${username}=${USER}    ${password}=${PASS}
    Send Text    ${username}
    Send Special Key    Tab
    Send Text    ${password}
    Send Special Key    Enter

Verify Login Success
    [Documentation]    Waits for "Sign-on Information" text confirming successful login.
    ...                Args: timeout (default: 10 seconds).
    [Arguments]    ${timeout}=10
    Screen Should Contain    Sign-on Information    timeout=${timeout}

Continue Login Session
    [Documentation]    Presses Enter to proceed past sign-on information screen.
    Send Special Key    Enter

Authenticate HMC Console
    [Documentation]    Authenticates to HMC and opens shared console session.
    ...                Uses credentials stored during session setup.
    ...                Args: timeout (default: 10 seconds).
    [Arguments]    ${timeout}=10
    # Wait for HMC login prompt
    Screen Should Contain    User ID    timeout=${timeout}
    # Enter HMC username
    Send Text    ${HMC_USER}
    Send Special Key    Tab
    # Enter HMC password
    Send Text    ${HMC_PASS}
    Send Special Key    Enter
    Sleep    2s
    # Navigate to console session
    # This may vary based on HMC interface, adjust as needed
    Send Text    1    # Typically option 1 for console
    Send Special Key    Enter

Execute Command And Verify
    [Documentation]    Types command, presses Enter, and captures screen.
    ...                Args: command (IBM i command to execute).
    [Arguments]    ${command}
    Send Text    ${command}
    Send Special Key    Enter
    Capture Screen    image=True

Sign Off Session
    [Documentation]    Executes SIGNOFF command to gracefully terminate session.
    Send Text    signoff
    Send Special Key    Enter
