Feature: Set up the ArtifactSpec development container
  Scenario: Create a development environment from the checked-in locks
    Given a supported development container with Pixi available
    When its setup script runs
    Then the developer tools and locked project environments are installed
    And optional agent tooling is not installed by default
