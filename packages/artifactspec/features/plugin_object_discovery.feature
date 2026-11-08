Feature: Discover plugin objects
  Scenario: Import an installed plugin object and expose its typed declarations
    Given an installed plugin declared as a Python object
    When I discover its capabilities
    Then its Python module is imported and its distribution version is reported
