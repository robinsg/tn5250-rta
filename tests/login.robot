*** Settings ***
Library           ../libraries/TN5250Library.py    True
Suite Teardown    Stop TN5250 Session

*** Variables ***
${HOST}        172.16.8.41
${USER}        grobinson   # <--- Change this
${PASS}        R3t1re17!   # <--- Change this
${DEVNAME}     QSECDEV06
${MAP}         285

*** Test Cases ***
Login To Secure IBM i
    [Documentation]    Connects to ${HOST} via SSL and logs in.
    
    # Start SSL Connection
    Start TN5250 Session    ${HOST}    ssl=${True}    devname=${DEVNAME}    map=${MAP}

    # Verify we hit the Sign On Screen
    Screen Should Contain    Sign On
    
    # Enter Username
    Send Text    ${USER}
    # Note: If your username is 10 chars, you might not need this Tab.
    # But for safety in this first test, we send it.
    Send Special Key    Tab
    
    # Enter Password
    Send Text    ${PASS}
    Send Special Key    Enter
    
    # Verify Login Success
    # Look for text that only appears AFTER login (e.g., "Main Menu")
    Screen Should Contain    Sign-on Information    timeout=10

    # Continue log in
    Send Special Key    Enter
    # Send text    wrkactjob
    # Send Special Key    Enter

    # Logout (Good practice)
    # Send Special Key    F3
    Send Text    wrkactjob
    Send Special Key    Enter
    Capture Screen    image=True

    Send Text    signoff
    Send Special Key    Enter    
     
