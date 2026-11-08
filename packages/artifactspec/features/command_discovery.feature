Feature: Automatically register built-in Typer applications
  Scenario: Add commands and a nested command group without modifying the CLI entry point
    Given a built-in command module exposes a Typer application with multiple commands and a nested group
    When the CLI discovers command modules
    Then both commands and the nested command are available from the Typer application
