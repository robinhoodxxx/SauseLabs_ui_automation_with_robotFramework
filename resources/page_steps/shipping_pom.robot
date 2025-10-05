*** Settings ***
Library    SeleniumLibrary
Library    ../../keywords/CommonKeywords.py
Resource    add_to_cart_pom.robot
*** Variables ***
${FINISH_BUTTON}         id:finish
${ITEM_TOTAL}            xpath://div[@class='summary_subtotal_label']
${TAX}                   xpath://div[@class='summary_tax_label']
${TOTAL}                 xpath://div[@class='summary_total_label']

*** Keywords ***

Verify the Items in Checkout Page
    [Arguments]    ${item_price_map}
    Verify Item Prices   ${item_price_map}
    Capture page screenshot    items_verified_in_checkout.png
    Log Message    All items verified in checkout page successfully


Finish Shipping
    Click Button    ${FINISH_BUTTON}
    Capture page screenshot    finish_shipping.png
    Log Message    Purchase Completed Successfully

Verify Price Details in Checkout Page
    [Arguments]    ${item_price_map}
    ${calculated_item_total}=    Set Variable    0.00
    FOR    ${item}    ${price_text}    IN    &{item_price_map}
        ${price_value}=    Remove String    ${price_text}    $
        ${price_value}=    Convert To Number    ${price_value}
        ${calculated_item_total}=    Evaluate    ${calculated_item_total} + ${price_value}
    END
    ${calculated_item_total}=    Round    ${calculated_item_total}    2
    ${item_total_text}=    Get Text    ${ITEM_TOTAL}
    ${item_total_value}=    Remove String    ${item_total_text}    Item total: $
    ${item_total_value}=    Convert To Number    ${item_total_value}
    Should Be Equal As Numbers    ${calculated_item_total}    ${item_total_value}
    Log Message    Item total verified successfully: ${item_total_value}



