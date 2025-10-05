*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py

*** Variables ***
${User_name_loc}    id:user-name
${Pass_word_loc}    id:password
${Login_Button}    id:login-button
*** Keywords ***


Login With Credentials
    [Arguments]    ${username_val}    ${password_val}
    Wait until element is visible    ${User_name_loc}    timeout=10s
    Input Text    ${User_name_loc}    ${username_val}
    Input Text    ${Pass_word_loc}    ${password_val}
    Capture page screenshot    login.png
    Click Button    ${Login_Button}
    Capture page screenshot    after_login.png
    Log Message    Logged in successfully with user: ${username_val}


