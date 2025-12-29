*** Settings ***
Documentation    Validates IBM i logout/sign-off process.
...              Ensures graceful session termination.

Resource    ../resources/common.robot
Suite Teardown    Close Session

*** Test Cases ***
Sign Off From IBM i
    [Documentation]    Validates sign-off command properly terminates the user session.
    ...                Typically used as cleanup after other tests.
    [Tags]    logout    cleanup
    
    Sign Off Session
