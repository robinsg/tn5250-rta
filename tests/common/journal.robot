*** Settings ***
Documentation    Validates IBM i journaling functionality.
...              Journals provide audit trails and recovery capabilities.

Resource    ../../resources/common.robot

*** Test Cases ***
Verify Journal Entries
    [Documentation]    Confirms system journals exist and are accessible via WRKJRN.
    [Tags]    journal    audit
    
    Execute Command And Verify    WRKJRN JRN(*LIBL/*ALL)

    Send Special Key    F3