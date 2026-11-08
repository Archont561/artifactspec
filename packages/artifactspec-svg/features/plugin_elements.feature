Feature: Plugin-owned SVG elements
  Scenario: Render plugin-owned elements through their string representation
    Given an SVG composition with plugin-owned rectangle and text elements
    When the SVG composition is serialized
    Then the SVG contains the elements in order with escaped text
