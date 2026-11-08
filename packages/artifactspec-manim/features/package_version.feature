Feature: Manim package version discovery
  Scenario: Discover the installed Manim package version
    Given the package is installed
    When its root namespace is inspected
    Then VERSION is its only public export
    And VERSION matches pyproject and installed distribution metadata
    And VERSION is read from distribution metadata
    And the package has no other source files
