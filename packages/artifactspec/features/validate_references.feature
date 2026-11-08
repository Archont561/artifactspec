Feature: Validate controlled artifact references
  Scenario: Resolve forward names and the latest object without running plugins
    Given typed circle and color capabilities
    When I validate a specification with forward and latest references
    Then both references resolve to their intended objects
    And validation has not run a plugin handler

  Scenario: Explain a property applied to the wrong object type
    Given typed circle and color capabilities
    When I validate a color property on a text object
    Then validation reports a wrong type at the reference

  Scenario: Reject legacy metadata without templates
    Given a legacy plugin without type metadata
    When I inspect its manifest
    Then the plugin must be migrated to the current schema
