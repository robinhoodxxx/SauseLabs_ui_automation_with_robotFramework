*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py

*** Variables ***
${BACK_HOME_BUTTON}    id:back-to-products
${Order_Complete_Header}    xpath://div[@id='checkout_complete_container']/h2[text()='Thank you for your order!']
*** Keywords ***

Verify Order Completion
    Element Should Be Visible    ${Order_Complete_Header}
    Capture page screenshot    order_complete.png
    Log Message    Order Completion Verified Successfully
Go Back To Home Page
    Click Button    ${BACK_HOME_BUTTON}
    Capture page screenshot    back_to_home.png
    Log Message    Navigated back to Home Page Successfully