Feature: Compose contributions from independent plugins
  Scenario: Render a document containing objects from two plugins
    Given independently registered shape and event plugins
    When I compose their objects using the shared representation
    Then their visual elements appear together in declaration order
