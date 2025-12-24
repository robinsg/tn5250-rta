*** Settings ***
Resource    ../resources/common.robot
Suite Teardown    Close Session

*** Test Cases ***
Sign Off From IBM i
    [Documentation]    Gracefully signs off from the active session
    [Tags]    logout    cleanup
    
    Sign Off Session
