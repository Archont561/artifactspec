Feature: Run capability discovery through the Typer app
  Scenario: Use the app directly to inspect installed capabilities
    Given an installed plugin with a static manifest
    When the Typer app is invoked with SVG capability details
    Then the matching capabilities are returned as JSON
    And the installed plugin module has not been executed
