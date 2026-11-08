Feature: Compose SVG and event plugin contributions
  Scenario: Render shapes and events from separate plugins in one image
    Given the SVG and event plugins are installed
    When I render a document containing a shape and a dated event
    Then the SVG contains both plugin contributions in declaration order

  Scenario: Reject manifests without plugin-defined syntax
    Given a legacy plugin manifest without statement templates
    When I try to read its capabilities
    Then the plugin must be migrated before it can be used
