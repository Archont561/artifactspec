Feature: Autodiscover installed rendering plugins
  Scenario: Inspect a plugin without importing its code
    Given an installed rendering plugin with an import marker
    When I inspect installed capabilities
    Then the plugin is listed without executing its code

  Scenario: Render with an installed plugin automatically
    Given a rendering plugin installed in the environment
    When I render with its backend without naming the plugin
    Then the plugin is loaded and the artifact is written

  Scenario: Disable automatic loading and select a plugin explicitly
    Given a rendering plugin available for explicit selection
    When I disable plugin autoload and render without selecting it
    Then rendering fails without importing the plugin
    When I explicitly select that plugin with autoload disabled
    Then the plugin is loaded and the artifact is written
