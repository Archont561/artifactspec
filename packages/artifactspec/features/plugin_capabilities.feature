Feature: Discoverable plugin capabilities
  Scenario: Register declared contributions
    Given a plugin declaring SVG and PDF output
    When the plugin is registered
    Then its declared capabilities are available for compatible outputs

  Scenario: Reject conflicting contributions
    Given a registry with a phrase contribution
    When another plugin contributes the same phrase
    Then registration fails without changing the registry

  Scenario: Discover installed capabilities from plugin objects
    Given an installed plugin object
    When capability details are requested for SVG output
    Then the matching capabilities are returned as JSON
    And the installed plugin module has been imported

  Scenario: Discover capabilities without installed plugins
    Given no installed plugins
    When capability details are requested
    Then discovery returns an empty plugin list
