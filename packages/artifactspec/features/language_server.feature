Feature: Publish validation diagnostics while editing
  Scenario: Repair an invalid document in an editor
    Given an editor connected to the language server with typed static capabilities
    When the editor opens a specification with an unresolved reference
    Then the language server publishes the shared validation diagnostic
    When the editor fixes the specification
    Then the language server clears the diagnostic
