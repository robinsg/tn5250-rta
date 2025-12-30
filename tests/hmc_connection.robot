*** Settings ***
Documentation       Validates HMC connection and shared 5250 console session.
...                 Requires valid HMC credentials in environment variables.
...                 (HMC_HOST, HMC_PORT, HMC_USER, HMC_PASS, HMC_SYSNAME, HMC_LPAR, HMC_SHAREKEY)

Resource            ../resources/common.robot

Suite Setup         Open HMC Console Session
Suite Teardown      Close Session


*** Test Cases ***
Connect To HMC And Open Shared Console
    [Documentation]    Validates connection to HMC and opening of shared 5250 console session.
    ...    Captures screen for troubleshooting.
    [Tags]    hmc    console    smoke

    # Debug: Capture initial screen to see what's actually displayed
    Sleep    2s    # Give screen time to render
    Capture Screen    hmc_initial_screen    image=True

    # Authenticate to HMC
    Authenticate HMC Console

    # Verify console session is active
    Sleep    2s
    Capture Screen    hmc_console_active    image=True

    # Screen should show console session indicators
    # This will need to be adjusted based on actual HMC console output
    Screen Should Contain    Console    timeout=10
