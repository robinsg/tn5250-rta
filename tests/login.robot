*** Settings ***
Variables      ../variables.py
Library           ../libraries/TN5250Library.py    True
Suite Teardown    Stop TN5250 Session

*** Test Cases ***
Login To Secure IBM i
    [Documentation]    Connects to ${HOST} via SSL and logs in.
    
    # Start SSL Connection
    Start TN5250 Session    ${HOST}    ssl=${SSL}    devname=${DEVNAME}    map=${MAP}

    # Verify we hit the Sign On Screen using new search keywords
    Screen Should Contain    Sign On
    ${found}=    Search Text On Screen    Sign On
    Should Be Equal    ${found}    ${True}
    
    # Enter Username
    Send Text    ${USER}
    # Note: If your username is 10 chars, you might not need this Tab.
    # But for safety in this first test, we send it.
    Send Special Key    Tab
    
    # Enter Password
    Send Text    ${PASS}
    Send Special Key    Enter
    
    # Verify Login Success using new search keywords
    # Look for text that only appears AFTER login (e.g., "Main Menu")
    Screen Should Contain    Sign-on Information    timeout=10
    ${found}=    Search Text On Screen    Sign-on Information
    Should Be Equal    ${found}    ${True}
    
    # Check message line for any errors
    ${message}=    Retrieve Message Line
    Log    Message line content: ${message}

    # Continue log in
    Send Special Key    Enter
    # Send text    wrkactjob
    # Send Special Key    Enter

    # Work with Active Jobs and verify using new keywords
    Send Text    wrkactjob
    Send Special Key    Enter
    
    # Verify the screen shows "Work with Active Jobs"
    ${jobs_found}=    Search Text On Screen    Work with Active Jobs
    Should Be Equal    ${jobs_found}    ${True}
    
    # Capture the screen
    Capture Screen    image=True
    
    # Exit back to command line
    Send Special Key    F3

    # Logout
    Send Text    signoff
    Send Special Key    Enter    
     
