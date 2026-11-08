Feature: Parse controlled artifact specifications
  Scenario: Parse registered output-aware statements into typed source-linked nodes
    Given image phrases and properties are registered
    When I parse an image specification with a named object and properties
    Then the document has typed statements and source locations
    And parsing has not executed plugin handlers

  Scenario: Preserve unresolved references for semantic validation
    Given an image color property is registered
    When I parse a property referring to it before any object is created
    Then the reference is preserved without being resolved

  Scenario: Reject an unknown phrase with its source location
    Given an image circle phrase is registered
    When I parse a specification with an unregistered phrase
    Then parsing fails with an unknown statement diagnostic at line 2

  Scenario: Reject a malformed property value
    Given an image color property can be parsed
    When I parse a specification with a non-string property value
    Then parsing fails with an unknown statement diagnostic at line 2

  Scenario: Reject ambiguous output declarations
    Given image and animation outputs are registered
    When I parse a specification with two output headers
    Then parsing fails with an ambiguous output diagnostic at line 2

  Scenario: Reject a phrase unavailable for the selected output
    Given a circle phrase is registered only for image output
    When I parse an animation specification using an image-only phrase
    Then parsing fails with an unknown statement diagnostic at line 2
