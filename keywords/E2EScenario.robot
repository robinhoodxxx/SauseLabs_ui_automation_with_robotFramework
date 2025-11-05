*** Settings ***
Resource          ../resources/page_steps/login_pom.robot
Resource          ../resources/page_steps/add_to_cart_pom.robot
Resource          ../resources/page_steps/checkout_pom.robot
Resource          ../resources/page_steps/shipping_pom.robot
Resource          ../resources/page_steps/checkout_complete_pom.robot
Resource      ../CommUtils/GlobalHooks.robot
Variables     ../Configs/application.py

*** Variables ***

*** Keywords ***
End To End Purchase Flow with Validations
    [Arguments]    @{ITEMS}
    [Documentation]    This test case verifies the end-to-end purchase flow on the Sauce Demo website with Verify of prices.
    [Setup]        Navigate to the Application    ${LOGIN_URL}    ${BROWSER}
    Login With Credentials    ${User_name}    ${Pass_word}
    ${Items_map}=    Add Items To Cart    @{ITEMS}
    Verify the Cart Count   @{ITEMS}
    Go To Cart
    Verify Item Prices in Cart   ${Items_map}
    Proceed To Checkout
    Enter Address And Continue    Josh    Doe    12345
    Verify the Items in Checkout Page    ${Items_map}
    Verify Price Details in Checkout Page    ${Items_map}
    Finish Shipping
    Verify Order Completion
    [Teardown]    Close Browser

End To End Purchase Flow
    [Arguments]    @{ITEMS}
    [Documentation]    This test case verifies the end-to-end purchase flow on the Sauce Demo website.
    [Setup]        Navigate to the Application    ${LOGIN_URL}    ${BROWSER}
    Login With Credentials    ${User_name_1}    ${Pass_word}
    ${Items_map}=    Add Items To Cart    @{ITEMS}
    Go To Cart
    Proceed To Checkout
    Enter Address And Continue    Josh    Doe    12345
    Finish Shipping
    Verify Order Completion
    [Teardown]    Close Browser






