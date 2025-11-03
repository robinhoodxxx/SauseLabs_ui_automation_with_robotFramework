*** Settings ***
Library           SeleniumLibrary
Resource          ../keywords/E2EScenario.robot
Resource    ../CommUtils/GlobalHooks.robot

Test Setup       Start Test Video Recording
Test Teardown    Stop Test Video Recording
Force Tags        e2e

*** Variables ***
@{ITEMS1}          Sauce Labs Backpack    Sauce Labs Bike Light    Sauce Labs Bolt T-Shirt
@{ITEMS2}          Sauce Labs Onesie    Sauce Labs Fleece Jacket    Sauce Labs Backpack

*** Test Cases ***
End To End Purchase Flow with Validations
    [Template]    End To End Purchase Flow with Validations
    @{ITEMS1}
#    @{ITEMS2}

End To End Purchase Flow
    [Template]    End To End Purchase Flow
    @{ITEMS1}
#    @{ITEMS2}