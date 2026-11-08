Feature: Publish validation diagnostics while editing
  Scenario: Repair an invalid document in an editor
    Given an editor connected to the language server with typed plugin capabilities
    When the editor opens a specification with an unresolved reference
    Then the language server publishes the shared validation diagnostic
    When the editor fixes the specification
    Then the language server clears the diagnostic

  Scenario: Edit after a Unicode separator inside a string
    Given an editor using incremental changes with typed plugin capabilities
    When the editor opens a specification with a Unicode separator before an unresolved reference
    Then the diagnostic identifies the reference on the correct line
    When the editor replaces that reference with an incremental edit
    Then the language server clears the diagnostic
