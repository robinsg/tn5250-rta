*** Settings ***
Documentation    Test Suite: IBM i Journal Verification
...
...              This test suite validates journaling functionality on the IBM i system.
...              Journals are critical for audit trails, recovery, and tracking changes
...              to database objects.
...
...              Prerequisites:
...              - Authenticated TN5250 session
...              - User must have authority to work with journals
...              - Journals must exist on the system
...
...              Test Coverage:
...              - Journal existence verification
...              - Journal entry accessibility
...              - Audit trail validation
...
...              Notes:
...              Journals are IBM i's mechanism for logging database changes and system events

Resource    ../resources/common.robot

*** Test Cases ***
Verify Journal Entries
    [Documentation]    Verifies journal for expected entries
    ...
    ...                Purpose:
    ...                Confirms that system journals exist and are accessible, ensuring
    ...                that audit and recovery capabilities are operational.
    ...
    ...                Expected Behavior:
    ...                - WRKJRN command executes successfully
    ...                - Journal list is displayed
    ...                - All journals in all libraries (*LIBL/*ALL) are shown
    ...                - F3 key returns to command line
    ...
    ...                Prerequisites:
    ...                - User must have authority to display journal information
    ...                - At least one journal must exist on the system
    ...
    ...                Notes:
    ...                *LIBL/*ALL displays all journals in the library list
    ...                Journals are essential for database integrity and recovery
    [Tags]    journal    audit
    
    Execute Command And Verify    WRKJRN JRN(*LIBL/*ALL)

    Send Special Key    F3