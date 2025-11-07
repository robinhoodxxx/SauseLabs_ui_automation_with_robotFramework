*** Settings ***
Library    SeleniumLibrary
Library    ../../CommUtils/CommonKeywords.py
Library    Collections

*** Variables ***
${ADD_ITEM_BUTTON}     xpath://div[starts-with(@class,'inventory_item_name ') and text()='{}']/ancestor::div[@class='inventory_item_description']//button[text()='Add to cart']
${CART_ICON}    id:shopping_cart_container
${ITEM_TITLE}    xpath://div[@class='inventory_item_name' and text()='{}']
${Checkout_Button}    id:checkout
${Item_Price}    //div[normalize-space()='{}']/ancestor::div[@data-test = 'inventory-item']//div[@class='inventory_item_price']

*** Keywords ***

Add Items To Cart
    [Arguments]    @{items}
    ${item_price_map}=    Create Dictionary
    FOR    ${item}    IN    @{items}
        Log to console    ${item}
        ${locator}=    Format Arguments    ${ADD_ITEM_BUTTON}    ${item}
        ${price_locator}=    Format Arguments    ${Item_Price}    ${item}
        ${price_text}=    Get Text    ${price_locator}
        Log Message    Adding item to cart: ${item} | Price: ${price_text}
        Click Button    ${locator}
        Set To Dictionary   ${item_price_map}    ${item}=${price_text}
    END
    Log Message    Items added to cart successfully: @{items}
    RETURN      ${item_price_map}

Verify the Cart Count
    [Arguments]    @{items}
    ${cart_count}=    Get Text    ${CART_ICON}
    ${expected_count}=    Get Length    ${items}
    Should Be Equal As Strings    ${cart_count}    ${expected_count}
    Log Message    Items added to cart:${expected_count} verified cart count: ${cart_count}
    Capture Unique Screenshot    items_added_to_cart.png



Go to Cart
    Click Element    ${CART_ICON}

Proceed to Checkout
    Click Button    ${Checkout_Button}
    Capture Unique Screenshot    proceed_to_checkout.png
    Log Message    Proceeded to Checkout Successfully

Verify Item Prices
    [Arguments]    ${item_price_map}
    FOR    ${item}    ${expected_price}    IN    &{item_price_map}
        ${item_locator}=    Format Arguments    ${ITEM_TITLE}    ${item}
        Element should be visible    ${item_locator}
        ${price_locator}=    Format Arguments    ${Item_Price}    ${item}
        ${actual_price}=    Get Text    ${price_locator}
        Should Be Equal As Strings    ${actual_price}    ${expected_price}
        Log Message    Price for item: ${item} verified successfully. Expected: ${expected_price}, Actual: ${actual_price}
    END

Verify Item Prices in Cart
    [Arguments]    ${item_price_map}
    Verify Item Prices    ${item_price_map}
    Capture Unique screenshot    item_prices_verified_in_cart.png
    Log Message    All item prices verified in cart successfully
