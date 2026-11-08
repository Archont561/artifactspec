Feature: Install repository Git hooks
  Scenario: A session checks and installs missing Lefthook hooks
    Given Lefthook reports that hooks are missing
    When the hook installation script runs
    Then it installs and verifies the hooks

  Scenario: A session leaves installed hooks unchanged
    Given Lefthook reports that hooks are already installed
    When the hook installation script runs
    Then it does not reinstall the hooks
