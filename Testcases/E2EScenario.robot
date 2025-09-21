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
*** Test Cases ***
End To End Purchase Flow
    Login With Credentials    standard_user    secret_sauce
    Add Items To Cart    @{ITEMS}
    Verify the Cart Count   @{ITEMS}
    Go To Cart
    Verify Items In Cart    @{ITEMS}
    Proceed To Checkout
    Enter Address And Continue    Josh    Doe    12345
    Verify the Items in Checkout Page    @{ITEMS}
    Finish Shipping
    Verify Order Completion

