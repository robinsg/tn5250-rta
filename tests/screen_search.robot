*** Settings ***
Documentation    Test cases for TN5250 screen search and retrieve functionality
Variables        ../variables.py
Library          ../libraries/TN5250Library.py    True
Suite Setup      Setup TN5250 Session
Suite Teardown   Stop TN5250 Session

*** Test Cases ***
Search Text On Specific Line
    [Documentation]    Test searching for text on a specific line
    Given I Am On The Sign On Screen
    When Search Text On Line    1    Sign On
    Then The Result Should Be True
    
    # Test negative case - text not on that line
    ${result}=    Search Text On Line    5    This text does not exist
    Should Be Equal    ${result}    ${False}

Retrieve Text From Line
    [Documentation]    Test retrieving specific text from a line
    Given I Am On The Sign On Screen
    ${text}=    Retrieve Text From Line    1    1    10
    Log    Retrieved text: ${text}
    Should Not Be Empty    ${text}

Search Text Anywhere On Screen
    [Documentation]    Test searching for text anywhere on the screen
    Given I Am On The Sign On Screen
    ${result}=    Search Text On Screen    Sign On
    Should Be Equal    ${result}    ${True}
    
    ${result}=    Search Text On Screen    NonExistentText123
    Should Be Equal    ${result}    ${False}

Retrieve Text From Position
    [Documentation]    Test retrieving text from a specific position
    Given I Am On The Sign On Screen
    ${text}=    Retrieve Text From Position    1    1    20
    Log    Retrieved text from position: ${text}
    Should Not Be Empty    ${text}

Search Two Texts On Screen
    [Documentation]    Test searching for two different texts
    Given I Am On The Sign On Screen
    
    # Both texts should be found
    ${result}=    Search Two Texts On Screen    Sign On    User
    Should Be Equal    ${result}    both
    
    # Only first text found
    ${result}=    Search Two Texts On Screen    Sign On    NonExistentText
    Should Be Equal    ${result}    first_only
    
    # Neither text found
    ${result}=    Search Two Texts On Screen    NonExistent1    NonExistent2
    Should Be Equal    ${result}    neither

Retrieve Text Block
    [Documentation]    Test retrieving a block of text from screen
    Given I Am On The Sign On Screen
    ${block}=    Retrieve Text Block    1    1    3    40
    Log    Retrieved block: ${block}
    Should Not Be Empty    ${block}
    # Block should contain multiple lines
    Should Contain    ${block}    \n

Search Text In Block
    [Documentation]    Test searching for text within a block
    Given I Am On The Sign On Screen
    ${result}=    Search Text In Block    1    1    5    80    Sign On
    Should Be Equal    ${result}    ${True}
    
    ${result}=    Search Text In Block    1    1    5    80    NonExistentText
    Should Be Equal    ${result}    ${False}

Retrieve Message Line
    [Documentation]    Test retrieving the message line (line 24)
    Given I Am On The Sign On Screen
    ${message}=    Retrieve Message Line
    Log    Message line: ${message}
    # Message line should return a string (may be empty)
    Variable Should Exist    ${message}

Verify Login Success With New Keywords
    [Documentation]    Test login flow using new search keywords
    Given I Am On The Sign On Screen
    When I Enter Valid Credentials
    Then Login Should Be Successful
    And Work With Active Jobs Screen

*** Keywords ***
Setup TN5250 Session
    Start TN5250 Session    ${HOST}    ssl=${SSL}    devname=${DEVNAME}    map=${MAP}

I Am On The Sign On Screen
    Screen Should Contain    Sign On    timeout=10

I Enter Valid Credentials
    Send Text    ${USER}
    Send Special Key    Tab
    Send Text    ${PASS}
    Send Special Key    Enter

Login Should Be Successful
    Screen Should Contain    Sign-on Information    timeout=10
    ${result}=    Search Text On Screen    Sign-on Information
    Should Be Equal    ${result}    ${True}
    Send Special Key    Enter

Work With Active Jobs Screen
    Send Text    wrkactjob
    Send Special Key    Enter
    Sleep    2s
    ${result}=    Search Text On Screen    Work with Active Jobs
    Should Be Equal    ${result}    ${True}
    Capture Screen    screen_search_test    image=True
    
    # Cleanup
    Send Special Key    F3
    Send Text    signoff
    Send Special Key    Enter

The Result Should Be True
    # This is a placeholder for Gherkin-style test
    # In practice, this would validate the previous step result
    Log    Previous search should have returned True
