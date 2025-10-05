*** Settings ***
Library           SeleniumLibrary    screenshot_root_directory=${SCREENSHOT_DIR}
Resource          ../resources/page_steps/login_pom.robot
Resource          ../resources/page_steps/add_to_cart_pom.robot
Resource          ../resources/page_steps/checkout_pom.robot
Resource          ../resources/page_steps/shipping_pom.robot
Resource          ../resources/page_steps/checkout_complete_pom.robot
Resource      ../resources/GlobalHooks.robot
Test Teardown     Close Browser
Test Setup    Navigate to the Application    ${LOGIN_URL}    chrome
Force Tags    e2e

*** Variables ***
@{ITEMS}    Sauce Labs Backpack    Sauce Labs Bike Light    Sauce Labs Bolt T-Shirt
${LOGIN_URL}    https://www.saucedemo.com/
${User_name}    standard_user
${Pass_word}    secret_sauce
*** Test Cases ***
End To End Purchase Flow
    [Documentation]    This test case verifies the end-to-end purchase flow on the Sauce Demo website.
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


