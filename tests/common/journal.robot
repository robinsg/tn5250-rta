*** Settings ***
Documentation    Validates IBM i journaling functionality.
...              Journals provide audit trails and recovery capabilities.

Resource    ../../resources/common.robot

*** Test Cases ***
Verify Journal Entries
    [Documentation]    Confirms system journals exist and are accessible via WRKJRN.
    ...                Verifies string value at row 10 columns 7 to 13 equals ${WRKJRN}.
    [Tags]    journal    audit
    
    Execute Command And Verify    WRKJRN JRN(*LIBL/*ALL)
    Screen Should Contain At Position    10    7    13    ${WRKJRN}
    Send Special Key    F3