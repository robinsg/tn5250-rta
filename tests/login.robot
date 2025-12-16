*** Settings ***
Library           ../libraries/TN5250Library.py
Suite Teardown    Stop TN5250 Session

*** Variables ***
${HOST}        172.16.8.41
${USER}        grobinson   # <--- Change this
${PASS}        R3t1re17!   # <--- Change this
${DEVNAME}     QSECDEV10
${MAP}         285

*** Test Cases ***
Login To Secure IBM i
    [Documentation]    Connects to ${HOST} via SSL and logs in.
    
    # 1. Start SSL Connection
    Start TN5250 Session    ${HOST}    ssl=${True}    devname=${DEVNAME}    map=${MAP}
    
    # 2. Verify we hit the Sign On Screen
    Screen Should Contain    Sign On
    
    # 3. Enter Username
    Send Text    ${USER}
    # Note: If your username is 10 chars, you might not need this Tab.
    # But for safety in this first test, we send it.
    Send Special Key    Tab
    
    # 4. Enter Password
    Send Text    ${PASS}
    Send Special Key    Enter
    
    # 5. Verify Login Success
    # Look for text that only appears AFTER login (e.g., "Main Menu")
    Screen Should Contain    Sign-on Information    timeout=10
    
    # 6. Logout (Good practice)
    Send Special Key    F3