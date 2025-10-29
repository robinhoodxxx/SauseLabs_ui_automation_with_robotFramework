*** Settings ***
Library           SeleniumLibrary
Library       ../../CommUtils/CommonKeywords.py

*** Variables ***
${FIRST_NAME_Loc}        id:first-name
${LAST_NAME_Loc}         id:last-name
${POSTAL_CODE_Loc}       id:postal-code
${CONTINUE_BUTTON}       id:continue


*** Keywords ***
Enter Address And Continue
    [Arguments]   ${first_name}  ${last_name}    ${postal_code}
    Wait until element is visible    ${FIRST_NAME_Loc}    timeout=10s
    Input Text    ${FIRST_NAME_Loc}    ${first_name}
    Input Text    ${LAST_NAME_Loc}     ${last_name}
    Input Text    ${POSTAL_CODE_Loc}   ${postal_code}
    Capture Unique screenshot    address_entered.png
    Click Button  ${CONTINUE_BUTTON}
    Capture Unique screenshot    after_address_continue.png
    Log Message    Address entered and continued to next step

