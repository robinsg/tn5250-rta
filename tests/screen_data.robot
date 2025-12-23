*** Settings ***
Variables      ../variables.py
Library           ../libraries/TN5250Library.py    True
Suite Setup       Connect To TN5250
Suite Teardown    Stop TN5250 Session

*** Test Cases ***
Test Search Line For Text
    [Documentation]    Verify searching for text on a specific line works correctly
    ${found}=    Search Line    1    Sign On
    Should Be True    ${found}    Text should be found on line 1

Test Get Line Text
    [Documentation]    Verify retrieving text from a specific line
    ${text}=    Get Line Text    1    1    10
    Should Not Be Empty    ${text}    Retrieved text should not be empty

Test Search Display For Text
    [Documentation]    Verify searching anywhere on the display
    ${found}=    Search Display    Sign On
    Should Be True    ${found}    Text should be found on display

Test Get Text At Position
    [Documentation]    Verify retrieving text from specific row and column
    ${text}=    Get Text At Position    1    1    5
    Should Not Be Empty    ${text}    Retrieved text should not be empty

Test Search Two Strings Both Found
    [Documentation]    Verify searching for two strings when both exist
    ${result}=    Search Two Strings    Sign    On
    Should Be Equal    ${result}    both    Both strings should be found

Test Search Two Strings First Only
    [Documentation]    Verify searching for two strings when only first exists
    ${result}=    Search Two Strings    Sign    XYZNotFound
    Should Be Equal    ${result}    first    Only first string should be found

Test Search Two Strings Neither Found
    [Documentation]    Verify searching for two strings when neither exists
    ${result}=    Search Two Strings    XYZNotFound    ABCNotFound
    Should Be Equal    ${result}    neither    Neither string should be found

Test Get Block Text
    [Documentation]    Verify retrieving a block of text
    ${text}=    Get Block Text    1    1    3    20
    Should Not Be Empty    ${text}    Block text should not be empty

Test Search Block
    [Documentation]    Verify searching within a specific block
    ${found}=    Search Block    1    1    5    80    Sign
    Should Be True    ${found}    Text should be found in block

Test Get Message Line
    [Documentation]    Verify reading the message line (line 24)
    ${message}=    Get Message Line
    Log    Message line: ${message}

Test Block Text Validation Rules
    [Documentation]    Verify block text enforces row/column rules
    Run Keyword And Expect Error    *end_row*must be >= start_row + 1*
    ...    Get Block Text    5    1    5    80
    Run Keyword And Expect Error    *end_col*must be >= start_col*
    ...    Get Block Text    1    10    3    5

*** Keywords ***
Connect To TN5250
    Start TN5250 Session    ${HOST}    ssl=${SSL}    devname=${DEVNAME}    map=${MAP}
    Screen Should Contain    Sign On    timeout=10
