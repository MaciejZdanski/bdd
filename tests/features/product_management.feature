Feature: Product Management

  Scenario: Adding a new product with correct data
    Given I have new product data
    When I add the product
    Then the response status code should be 201
    And the response should contain the product

  Scenario: Attempting to add a product with a negative price
    Given I have new product data with negative price
    When I add the product with negative price
    Then the response status code should be 400
    And the response should indicate a validation error

  Scenario: Automatic change of the product status do "Unavailable" when the stock level reaches 0
    Given I have a product
    When I update the product stock to 0
    Then the product status should be "Unavailable"

  Scenario: Updating an existing product
    Given I have a product
    When I update the product details
    Then the response status code should be 200
    And the product details should be updated

  Scenario: Deleting an existing product
    Given I have a product
    When I delete the product
    Then I response status code should be 200
    And the product should no longer exist