*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py
Resource    add_to_cart_pom.robot
*** Variables ***
${FINISH_BUTTON}    id:finish
*** Keywords ***

Verify the Items in Checkout Page
    [Arguments]    @{items}
    Capture page screenshot
    FOR    ${item}    IN    @{items}
        ${locator}=    Format Arguments    ${ITEM_TITLE}    ${item}
        Element Should Be Visible    ${locator}
    END
    Capture page screenshot


Finish Shipping
    Click Button    ${FINISH_BUTTON}
    Capture page screenshot
    Log Message    Purchase Completed Successfully


