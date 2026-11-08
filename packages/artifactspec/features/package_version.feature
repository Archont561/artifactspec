Feature: ArtifactSpec package version discovery
  Scenario: Discover the installed ArtifactSpec version
    Given the package is installed
    When its root namespace is inspected
    Then VERSION is its only public export
    And VERSION matches pyproject and installed distribution metadata
    And VERSION is read from distribution metadata
