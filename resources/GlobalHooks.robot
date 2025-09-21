*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py

*** Variables ***

*** Keywords ***
Navigate to the Application
    [Arguments]    ${url}    ${browser}=chrome
    IF    'chrome' in '${browser}'
       ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver.chrome.options'].Options()    sys
       ${prefs}=    Create Dictionary    credentials_enable_service=${False}    profile.password_manager_enabled=${False}    profile.password_manager_leak_detection=${False}
       Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}
       Open browser  ${url}   ${browser}    options=${chrome_options}
    ELSE
       Open browser  ${url}   ${browser}
    END
    Maximize Browser Window
    Capture page screenshot

