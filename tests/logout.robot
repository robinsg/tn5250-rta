*** Settings ***
Documentation    Test Suite: IBM i Logout/Sign-Off Verification
...
...              This test suite validates the logout/sign-off process from an IBM i
...              system. It ensures that users can properly terminate their session
...              and that the system handles sign-off gracefully.
...
...              Prerequisites:
...              - Active authenticated TN5250 session
...              - User must be logged in before sign-off
...
...              Test Coverage:
...              - Graceful session termination
...              - Sign-off command execution
...              - Proper cleanup of TN5250 session

Resource    ../resources/common.robot
Suite Teardown    Close Session

*** Test Cases ***
Sign Off From IBM i
    [Documentation]    Gracefully signs off from the active session
    ...
    ...                Purpose:
    ...                Validates that the sign-off command properly terminates the user session.
    ...
    ...                Expected Behavior:
    ...                - Sign-off command is accepted
    ...                - Session terminates cleanly
    ...                - No errors or warnings are displayed
    ...
    ...                Prerequisites:
    ...                - User must be authenticated
    ...                - Active session must exist
    ...
    ...                Notes:
    ...                This is typically run as a cleanup step after other tests
    [Tags]    logout    cleanup
    
    Sign Off Session
