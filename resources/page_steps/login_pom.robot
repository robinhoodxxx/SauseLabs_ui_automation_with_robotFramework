*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py

*** Variables ***
${password_store}    --password-store=basic
${User_name}    id:user-name
${Pass_word}    id:password
${Login_Button}    id:login-button
*** Keywords ***


Login With Credentials
    [Arguments]    ${username_val}    ${password_val}
    Wait until element is visible    ${User_name}    timeout=10s
    Input Text    ${User_name}    ${username_val}
    Input Text    ${Pass_word}    ${password_val}
    Capture page screenshot
    Click Button    ${Login_Button}
    Capture page screenshot
    Log Message    Logged in successfully with user: ${username}


