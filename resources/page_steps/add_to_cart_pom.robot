*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py

*** Variables ***
${ADD_ITEM_BUTTON}    xpath://div[@class='inventory_item_name ' and text()='{}']/ancestor::div[@class='inventory_item_description']//button[text()='Add to cart']
${CART_ICON}    id:shopping_cart_container
${ITEM_TITLE}    xpath://div[@class='inventory_item_name' and text()='{}']
${Checkout_Button}    id:checkout

*** Keywords ***

Add Items To Cart
    [Arguments]    @{items}
    Capture page screenshot
    FOR    ${item}    IN    @{items}
        ${locator}=    Format Arguments    ${ADD_ITEM_BUTTON}    ${item}
        Log Message  Adding item to cart:${item} with locator:${locator}
        Click Button  ${locator}
    END
    Capture page screenshot

Verify the Cart Count
    [Arguments]    @{items}
    ${cart_count}=    Get Text    ${CART_ICON}
    ${expected_count}=    Get Length    ${items}
    Should Be Equal As Strings    ${cart_count}    ${expected_count}
    Log Message    Items added to cart:${expected_count} verified cart count: ${cart_count}

Verify Items In Cart
    [Arguments]    @{items}
    Capture page screenshot
    FOR    ${item}    IN    @{items}
        ${locator}=    Format Arguments    ${ITEM_TITLE}    ${item}
        Element Should Be Visible    ${locator}
    END
    Capture page screenshot
    Log Message    All items verified in cart successfully

Go to Cart
    Click Element    ${CART_ICON}
    Capture page screenshot

Proceed to Checkout
    Click Button    ${Checkout_Button}
    Capture page screenshot
    Log Message    Proceeded to Checkout Successfully


