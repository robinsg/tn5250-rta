*** Settings ***
Documentation    Common Keywords and Resources for TN5250 Testing
...
...              This resource file provides reusable keywords for TN5250 terminal
...              emulation testing on IBM i systems. Keywords handle session management,
...              authentication, and common terminal operations.
...
...              Usage:
...              Import this resource in test suites with:
...              Resource    ../resources/common.robot
...
...              Available Keywords:
...              - Session management (Open/Close)
...              - Authentication (Login/Verify)
...              - Command execution
...              - Screen verification
...
...              Dependencies:
...              - TN5250Library.py for terminal emulation
...              - Environment variables (HOST, USER, PASS, etc.)

Variables    ${EXECDIR}/variables.py
Library      ${EXECDIR}/libraries/TN5250Library.py    True

*** Keywords ***
Open Session To Host
    [Documentation]    Establishes a TN5250 session to the configured host
    ...
    ...                Purpose:
    ...                Initiates a TN5250 terminal session to the IBM i system using
    ...                configuration from environment variables.
    ...
    ...                Arguments:
    ...                None (uses environment variables)
    ...
    ...                Environment Variables Used:
    ...                - HOST: Target IBM i hostname or IP address
    ...                - SSL: Boolean flag for SSL/TLS connection
    ...                - DEVNAME: Optional device name for the session
    ...                - MAP: Character mapping (default: 285)
    ...
    ...                Expected Behavior:
    ...                - TN5250 session starts successfully
    ...                - Connection to host is established
    ...                - Terminal screen becomes available
    ...
    ...                Raises:
    ...                Fails if connection cannot be established
    ...
    ...                Notes:
    ...                This is typically used in Suite Setup
    Start TN5250 Session    ${HOST}    ssl=${SSL}    devname=${DEVNAME}    map=${MAP}

Close Session
    [Documentation]    Terminates the active TN5250 session
    ...
    ...                Purpose:
    ...                Cleanly closes the TN5250 terminal session and releases resources.
    ...
    ...                Arguments:
    ...                None
    ...
    ...                Expected Behavior:
    ...                - TN5250 session is terminated
    ...                - tmux session is killed
    ...                - Resources are cleaned up
    ...
    ...                Notes:
    ...                This is typically used in Suite Teardown
    ...                Safe to call even if session doesn't exist
    Stop TN5250 Session

Verify Sign On Screen
    [Documentation]    Verifies the sign-on screen is displayed
    ...
    ...                Purpose:
    ...                Confirms that the IBM i sign-on screen has loaded and is ready
    ...                for credential input.
    ...
    ...                Arguments:
    ...                - timeout: Maximum seconds to wait for sign-on screen (default: 10)
    ...
    ...                Expected Behavior:
    ...                - Screen contains "Sign On" text
    ...                - Screen is ready for user input
    ...
    ...                Raises:
    ...                AssertionError if sign-on screen not found within timeout
    ...
    ...                Example:
    ...                Verify Sign On Screen
    ...                Verify Sign On Screen    timeout=30
    [Arguments]    ${timeout}=10
    Screen Should Contain    Sign On    timeout=${timeout}

Login With Credentials
    [Documentation]    Logs in with provided username and password
    ...
    ...                Purpose:
    ...                Enters credentials on the sign-on screen and submits them
    ...                for authentication.
    ...
    ...                Arguments:
    ...                - username: User ID to login with (default: ${USER} from environment)
    ...                - password: Password for authentication (default: ${PASS} from environment)
    ...
    ...                Expected Behavior:
    ...                - Username is entered in the user field
    ...                - Password is entered in the password field (masked)
    ...                - Enter key submits the credentials
    ...
    ...                Prerequisites:
    ...                - Sign-on screen must be displayed
    ...                - Cursor must be in the user field
    ...
    ...                Example:
    ...                Login With Credentials
    ...                Login With Credentials    username=TESTUSER    password=testpass
    [Arguments]    ${username}=${USER}    ${password}=${PASS}
    Send Text    ${username}
    Send Special Key    Tab
    Send Text    ${password}
    Send Special Key    Enter

Verify Login Success
    [Documentation]    Confirms login was successful by checking for sign-on info
    ...
    ...                Purpose:
    ...                Validates that authentication completed successfully by verifying
    ...                the post-login screen displays the expected message.
    ...
    ...                Arguments:
    ...                - timeout: Maximum seconds to wait for success message (default: 10)
    ...
    ...                Expected Behavior:
    ...                - Screen contains "Sign-on Information" text
    ...                - Login was accepted by the system
    ...
    ...                Raises:
    ...                AssertionError if success message not found within timeout
    ...
    ...                Notes:
    ...                The "Sign-on Information" screen shows last login details
    ...
    ...                Example:
    ...                Verify Login Success
    ...                Verify Login Success    timeout=20
    [Arguments]    ${timeout}=10
    Screen Should Contain    Sign-on Information    timeout=${timeout}

Continue Login Session
    [Documentation]    Completes the post-login flow
    ...
    ...                Purpose:
    ...                Advances past the sign-on information screen to reach the
    ...                main command line or menu.
    ...
    ...                Arguments:
    ...                None
    ...
    ...                Expected Behavior:
    ...                - Enter key is pressed
    ...                - User proceeds to main menu or command line
    ...
    ...                Prerequisites:
    ...                - Must be on sign-on information screen
    ...
    ...                Notes:
    ...                This typically bypasses informational screens shown after login
    Send Special Key    Enter

Execute Command And Verify
    [Documentation]    Sends a command and captures the screen
    ...
    ...                Purpose:
    ...                Executes an IBM i command and captures a screenshot of the result
    ...                for verification and documentation purposes.
    ...
    ...                Arguments:
    ...                - command: The IBM i command to execute (e.g., "DSPLIB QIWS")
    ...
    ...                Expected Behavior:
    ...                - Command is typed on the command line
    ...                - Enter key submits the command
    ...                - Screen is captured after command execution
    ...
    ...                Prerequisites:
    ...                - Must be at command line or menu
    ...                - User must have authority to execute the command
    ...
    ...                Notes:
    ...                Screenshots are saved to results/screenshots directory
    ...                Useful for both verification and debugging
    ...
    ...                Example:
    ...                Execute Command And Verify    DSPLIB QIWS
    ...                Execute Command And Verify    WRKSYSSTS
    [Arguments]    ${command}
    Send Text    ${command}
    Send Special Key    Enter
    Capture Screen    image=True

Sign Off Session
    [Documentation]    Gracefully signs off from the session
    ...
    ...                Purpose:
    ...                Executes the IBM i SIGNOFF command to properly terminate the
    ...                user session.
    ...
    ...                Arguments:
    ...                None
    ...
    ...                Expected Behavior:
    ...                - SIGNOFF command is typed
    ...                - Enter key submits the command
    ...                - Session is terminated gracefully
    ...
    ...                Prerequisites:
    ...                - Must be authenticated and at command line
    ...
    ...                Notes:
    ...                This performs a clean logout, different from forcibly closing
    ...                the TN5250 connection. Recommended for test cleanup.
    Send Text    signoff
    Send Special Key    Enter
