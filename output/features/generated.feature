Feature: Online Banking Application
  Background:
    Given the online banking application is available
  @login @positive
  Scenario: Successful user login with valid credentials
    Given the user is on the login page
    When the user enters valid username "valid_user" and password "valid_password"
    And the user clicks the "Login" button
    Then the user should be redirected to the account summary page
    And the user should see a welcome message containing "valid_user"
  @login @negative
  Scenario: Unsuccessful login with invalid username
    Given the user is on the login page
    When the user enters invalid username "invalid_username" and valid password "valid_password"
    And the user clicks the "Login" button
    Then the user should see an error message "Invalid username or password"
    And the user should remain on the login page
  @login @negative
  Scenario: Unsuccessful login with invalid password
    Given the user is on the login page
    When the user enters valid username "valid_user" and invalid password "invalid_password"
    And the user clicks the "Login" button
    Then the user should see an error message "Invalid username or password"
    And the user should remain on the login page
  @login @regression
  Scenario: Successful user login with biometric ID
    Given the user is on the login page
    When the user selects "Biometric Login"
    And the user authenticates with biometric ID
    Then the user should be redirected to the account summary page
    And the user should see a welcome message
  @balance @positive
  Scenario: User can view account balances
    Given the user is logged in
    When the user navigates to the account summary page
    Then the user should see a list of their accounts
    And the user should see the current balance for each account
  @balance @negative
  Scenario: Account balances are not displayed when API is unavailable
    Given the user is logged in
    And the account balance API is unavailable
    When the user navigates to the account summary page
    Then the user should see an error message "Unable to retrieve account balances"
  @transfer @positive
  Scenario: User can transfer funds between own accounts
    Given the user is logged in
    And the user has two accounts "Account A" and "Account B"
    When the user initiates a transfer from "Account A" to "Account B" for $100
    And the user confirms the transfer
    Then the transfer should be successful
    And the balance of "Account A" should decrease by $100
    And the balance of "Account B" should increase by $100
    And the user should receive a transaction confirmation
  @transfer @positive
  Scenario: User can transfer funds to a third-party account (internal)
    Given the user is logged in
    And the user knows the account number of the third-party account within the bank
    When the user initiates a transfer to the third-party account for $50
    And the user confirms the transfer
    Then the transfer should be successful
    And the user should receive a transaction confirmation
    And the third-party should receive the funds
  @transfer @positive
  Scenario: User can transfer funds to a third-party account (external)
    Given the user is logged in
    And the user knows the account number and routing number of the third-party account at another bank
    When the user initiates a transfer to the external third-party account for $75
    And the user confirms the transfer
    Then the transfer should be successful
    And the user should receive a transaction confirmation
    And the third-party should receive the funds
  @transfer @negative
  Scenario: Transfer fails due to insufficient funds
    Given the user is logged in
    And the user has insufficient funds in "Account A"
    When the user initiates a transfer from "Account A" to "Account B" for $1000
    And the user confirms the transfer
    Then the transfer should fail
    And the user should see an error message "Insufficient funds"
    And the balances of "Account A" and "Account B" should remain unchanged
  @transfer @regression
  Scenario: Transfer to invalid account number fails
    Given the user is logged in
    When the user initiates a transfer to an invalid account number "123456789"
    And the user confirms the transfer
    Then the transfer should fail
    And the user should see an error message "Invalid account number"
  @billpayment @positive
  Scenario: User can pay bills using a saved biller
    Given the user is logged in
    And the user has a saved biller "Electricity Company"
    When the user initiates a bill payment to "Electricity Company" for $50
    And the user confirms the payment
    Then the payment should be successful
    And the user should receive a payment confirmation
  @billpayment @positive
  Scenario: User can pay bills using a new biller
    Given the user is logged in
    When the user adds a new biller "Gas Company" with account number "987654321"
    And the user initiates a bill payment to "Gas Company" for $30
    And the user confirms the payment
    Then the payment should be successful
    And the user should receive a payment confirmation
    And the new biller should be saved
  @billpayment @negative
  Scenario: Bill payment fails due to invalid biller account number
    Given the user is logged in
    When the user initiates a bill payment to "Electricity Company" with an invalid account number
    And the user confirms the payment
    Then the payment should fail
    And the user should see an error message "Invalid biller account number"
  @history @positive
  Scenario: User can view transaction history for the last 90 days
    Given the user is logged in
    When the user navigates to the transaction history page
    Then the user should see a list of transactions for the last 90 days
    And the transactions should be sorted by date in descending order
  @history @negative
  Scenario: No transaction history is displayed when API is unavailable
    Given the user is logged in
    And the transaction history API is unavailable
    When the user navigates to the transaction history page
    Then the user should see an error message "Unable to retrieve transaction history"
  @logout @regression
  Scenario: User is automatically logged out after 5 minutes of inactivity
    Given the user is logged in
    When the user is inactive for 5 minutes
    Then the user should be automatically logged out
    And the user should be redirected to the login page
  @notifications @positive
  Scenario: User receives email notification on successful fund transfer
    Given the user is logged in
    And the user has initiated a successful fund transfer of $100
    Then the user should receive an email notification confirming the transfer
  @notifications @positive
  Scenario: User receives SMS notification on successful fund transfer
    Given the user is logged in
    And the user has initiated a successful fund transfer of $100
    Then the user should receive an SMS notification confirming the transfer
  @inapp_support @positive
  Scenario: User can access in-app support through chatbot
    Given the user is logged in
    When the user clicks the "Help" button
    Then the chatbot window should open
    And the user should be able to interact with the chatbot
  @inapp_support @positive
  Scenario: User can submit a support ticket
    Given the user is logged in
    When the user clicks the "Contact Support" button
    Then the support ticket submission form should open
    And the user should be able to submit a support ticket
  @responsive @regression
  Scenario Outline: Application is responsive on different devices
    Given the user is using a <device>
    When the user accesses the online banking application
    Then the application layout should be optimized for <device>
    Examples: