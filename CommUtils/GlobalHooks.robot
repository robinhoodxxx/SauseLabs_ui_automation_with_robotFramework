*** Settings ***
Library    SeleniumLibrary
Library    ../CommUtils/CommonKeywords.py
Library    ScreenCapLibrary
Library    OperatingSystem
Library    String
Variables    ../Configs/application.py


*** Variables ***
${VIDEO_DIR}    ${OUTPUT DIR}

*** Keywords ***
Navigate to the Application
    [Arguments]    ${url}    ${browser}=CHROME

    ${browser}=    Evaluate    '${browser}'.strip().upper()
    ${options_required}=    Set Variable    ${False}
    ${is_headless} =    Set Variable     ${False}
    IF    'CHROME' == '${browser}'
        ${options_required}=    Set Variable    ${True}
        ${browser_headless}=    Catenate    SEPARATOR=    ${browser}    _HEADLESS
        ${result}=      Run Keyword And Ignore Error    Set Variable    ${${browser_headless}}
        ${is_headless}=    Set Variable If    '${result}[0]' == 'PASS'    ${result}[1]    ${False}

    END
    IF    ${options_required}
        ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver.chrome.options'].Options()    sys
        IF    ${is_headless}
            Log To Console    Running Chrome in Headless Mode.
            Call Method    ${chrome_options}     add_argument     --headless
        END
        ${prefs}=    Create Dictionary    credentials_enable_service=${False}    profile.password_manager_enabled=${False}    profile.password_manager_leak_detection=${False}
        Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}
        Open browser  ${url}   ${browser}    options=${chrome_options}
    ELSE
        Open browser  ${url}   ${browser}
    END

    Log Message    Navigated to URL: ${url} using browser: ${browser}
    Maximize Browser Window

Start Test Video Recording
    [Documentation]    Starts video recording and saves the target path to a test variable.
    ${sanitized_name}=       Replace String    ${TEST NAME}    ${SPACE}    _
    Create directory     ${OUTPUT DIR}/${TEST NAME}
    Start Video Recording     name=${OUTPUT DIR}/${TEST NAME}/${sanitized_name}     embed=True     embed_width=100px   alias=${sanitized_name}
    ${desired_filename}=     Set Variable    ${sanitized_name}.webm
    ${final_video_path}=     Set Variable    ${VIDEO_DIR}${/}${desired_filename}
    Set Test Variable        ${final_video_path}
    Set Test Variable        ${sanitized_name}
    Log to console           Desired final video path: ${final_video_path}



Stop Test Video Recording
#    ${link_path}=    Video Record Path
#    Log to console    linkpath ${link_path}
#    Log    <a href="${link_path}">🎥 Watch ${TEST NAME} Video</a>    html=True
     Stop Video Recording     alias=${sanitized_name}


Video Record Path
#    ${generic_path}=         Stop Video Recording
#    Create Directory         ${VIDEO_DIR}
#    Move File   ${generic_path}    ${final_video_path}
#    RETURN    videos${/}${sanitized_name}.webm
