Feature: Validate a specification from the command line
  Scenario: Validate using installed plugin declarations
    Given an installed typed plugin and a valid specification file
    When I validate the file as JSON
    Then validation succeeds with no diagnostics
    And the installed validation plugin is imported

  Scenario: Report multiple source-linked validation errors
    Given an installed typed plugin and a specification with missing references
    When I validate the file as JSON
    Then validation fails with two source-linked errors
    And the installed validation plugin is imported
