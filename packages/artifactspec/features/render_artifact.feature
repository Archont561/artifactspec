Feature: Render validated semantic content
  Scenario: Render a specification as an SVG image
    Given an explicitly trusted basic SVG plugin and an image specification
    When I render it using the selected representation and renderer
    Then the SVG artifact contains the described text and rectangle
    And the result identifies its renderer and source provenance

  Scenario: Reuse semantic content for a report representation
    Given an explicitly trusted basic SVG plugin and a report specification
    When I select the report representation
    Then the semantic text is represented without animation playback

  Scenario: Render an image through the CLI with the built-in plugin
    Given a specification file and explicitly selected built-in image plugin
    When I invoke the render command with explicit capabilities
    Then the command writes an SVG artifact and reports its provenance

  Scenario: Reuse historical events without creating playback timing
    Given a timeline of two dated events in declaration order
    When I compose the same semantic timeline for image and report
    Then both forms preserve the event dates and labels in declaration order
    And the event dates are not animation playback timing
