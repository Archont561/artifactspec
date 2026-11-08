Feature: Test plugins through public phase contexts
  Scenario: Build typed content using registered phrase and property handlers
    Given a typed text plugin using public phase contexts
    When a valid specification is converted into semantic content
    Then the content contains the declared text and source provenance
    And the same plugin handlers can be exercised with fake contexts
