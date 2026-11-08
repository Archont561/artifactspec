Feature: Plugin-defined language syntax
  Scenario: Parse a plugin's custom output and content statements without executing code
    Given static metadata for a plugin with its own statement templates
    When I validate a document written using those templates
    Then the document is valid and its statement locations are retained

  Scenario: Reject a core-like form that no plugin declares
    Given a plugin that declares a different output and content syntax
    When I validate a document using undeclared generic forms
    Then validation reports an unknown output declaration
