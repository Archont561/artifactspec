Feature: Documentation quality checks
  Documentation should use consistent terminology without linting code examples.

  Scenario: Incorrect project terminology is reported
    Given a documentation passage with inconsistent terminology
    When the passage is checked with Vale
    Then Vale reports the preferred terminology

  Scenario: Code examples are not treated as prose
    Given a documentation passage with terminology inside a code block
    When the passage is checked with Vale
    Then Vale reports no findings
