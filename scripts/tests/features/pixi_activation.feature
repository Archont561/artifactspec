Feature: Activate the local package sources
  Scenario: Run Python from anywhere in the workspace
    Given a caller with an existing Python path
    When Pixi activates the default environment from a package directory
    Then both package source directories are on the Python path
    And the caller's existing Python path is preserved
