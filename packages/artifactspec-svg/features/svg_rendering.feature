Feature: Render reusable composition with the SVG plugin
  Scenario: Produce editable SVG from semantic layout
    Given a composition containing a text element
    When the SVG plugin renders the composition
    Then the artifact contains escaped editable SVG text
