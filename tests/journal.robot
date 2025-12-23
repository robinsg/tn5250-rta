*** Settings ***
Resource    ../resources/common.robot

*** Test Cases ***
Verify Journal Entries
    [Documentation]    Verifies journal for expected entries
    [Tags]    journal    audit
    
    Execute Command And Verify    WRKJRN JRN(*LIBL/*ALL)

    Send Special Key    F3