*** Settings ***
Library    SeleniumLibrary
Library    ScreenCapLibrary
Library    OperatingSystem
Library    ../CommUtils/CommonKeywords.py

Library    String
Variables    ../Configs/application.py

*** Variables ***
${VIDEO_DIR}    ${OUTPUT DIR}

*** Keywords ***
Navigate To The Application
    [Arguments]    ${url}    ${browser}=CHROME    ${headless}=False

    # Normalize browser name
    ${browser}=    Set Variable    ${browser.strip().upper()}
    ${window_size}=    Set Variable      --window-size=1920,1080

    # Check if headless variable is set externally (e.g., ${CHROME_HEADLESS}=True)
    ${browser_headless_var}=    Catenate    SEPARATOR=    ${browser}    _HEADLESS
    ${result}=      Run Keyword And Ignore Error    Set Variable    ${${browser_headless_var}}
    ${headless}=    Set Variable If    '${result}[0]' == 'PASS'    ${result}[1]    ${False}

    # Handle Chrome browser options
    IF    '${browser}' == 'CHROME'
        ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver.chrome.options'].Options()    sys

        ${prefs}=    Create Dictionary
        ...    credentials_enable_service=${False}
        ...    profile.password_manager_enabled=${False}
        ...    profile.password_manager_leak_detection=${False}
        Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}

        Call Method    ${chrome_options}    add_argument    --start-maximized
        IF    ${headless}
            Log To Console    Running Chrome in Headless Mode.
            Call Method    ${chrome_options}    add_argument    --headless
            Call Method    ${chrome_options}    add_argument     ${window_size}
        END

        Open Browser    ${url}    chrome    options=${chrome_options}

    ELSE IF    '${browser}' == 'EDGE'
        ${edge_options}=    Evaluate    sys.modules['selenium.webdriver.edge.options'].Options()    sys
        Call Method    ${edge_options}    add_argument    --start-maximized

        IF    ${headless}
            Log To Console    Running Edge in Headless Mode.
            Call Method    ${edge_options}    add_argument    --headless
            Call Method    ${edge_options}    add_argument    ${window_size}
        END

        ${edge_driver_path}=    Set Variable If    os.path.exists('Drivers/edge/msedgedriver.exe')    Drivers/edge/msedgedriver.exe    ${None}
        IF    '${edge_driver_path}' != '${None}'
            Open Browser    ${url}    edge    options=${edge_options}    executable_path=${edge_driver_path}
        ELSE
            Open Browser    ${url}    edge    options=${edge_options}
        END

    ELSE IF    '${browser}' == 'FIREFOX'
        ${ff_options}=    Evaluate    sys.modules['selenium.webdriver.firefox.options'].Options()    sys
        IF    ${headless}
            Log To Console    Running Firefox in Headless Mode.
            Call Method    ${ff_options}    add_argument    --headless
        END
        Open Browser    ${url}    firefox    options=${ff_options}
        Maximize Browser Window

    ELSE
        Fail    Unsupported browser type: ${browser}. Supported: CHROME, EDGE, FIREFOX.
    END

    Log Message    Navigated to URL: ${url} using browser: ${browser}

#    # Maximize only when not headless
    IF    not ${headless}
        Maximize Browser Window
    END

Navigate to the Applications
    [Arguments]    ${url}    ${browser}=CHROME
#    Open Latest Browser    ${url}    ${browser}


Start Test Video Recording
    [Documentation]    Starts video recording and saves the target path to a test variable.
    Set Custom Screenshot Directory For Current Test
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
