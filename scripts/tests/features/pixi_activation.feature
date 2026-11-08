Feature: Activate the local package sources
  Scenario: Run Python from anywhere in the workspace
    Given a caller with an existing Python path
    When Pixi activates the default environment from a package directory
    Then every project source directory is on the Python path
    And the caller's existing Python path is preserved

  Scenario: A newly added project is discovered without changing Pixi tasks
    Given an inherited Python path
    And a new Python project with a source directory
    When Pixi activates the default environment from a package directory
    Then the new project source directory is on the Python path
