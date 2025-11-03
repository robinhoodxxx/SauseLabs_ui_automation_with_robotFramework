*** Settings ***
Library    SeleniumLibrary
Library    ../CommUtils/CdpRecorder.py    # Import your custom Python file
Resource          ../keywords/E2EScenario.robot

Test Setup     Start Test Recording
Test Teardown    Stop Test Recording And Clean Up
Force Tags    video_test

*** Variables ***
@{ITEMS1}          Sauce Labs Backpack    Sauce Labs Bike Light    Sauce Labs Bolt T-Shirt
@{ITEMS2}          Sauce Labs Onesie    Sauce Labs Fleece Jacket    Sauce Labs Backpack


*** Keywords ***
Start Test Recording
    # ${OUTPUT DIR} is passed from your Pabot run
    Navigate to the Application    ${LOGIN_URL}    ${BROWSER}
    ${OUTPUT_DIR}=    Get Variable Value    ${OUTPUT DIR}
    Start CDP Screencast    ${OUTPUT_DIR}    ${TEST NAME}

Stop Test Recording And Clean Up
    ${OUTPUT_DIR}=    Get Variable Value    ${OUTPUT DIR}
    ${FINAL_VIDEO_PATH}=    Set Variable    ${OUTPUT_DIR}/${TEST NAME}.mp4
    Stop CDP Screencast And Stitch Video    ${FINAL_VIDEO_PATH}

#*** Test Cases ***
#End To End Purchase Flow with Validations
#    [Template]    End To End Purchase Flow with Validations
#    @{ITEMS1}
#    @{ITEMS2}
