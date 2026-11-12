Feature: Python clean code gate
  Python clean code findings should fail the same check locally and in CI.

  Scenario: A global statement is rejected
    Given a Python file that mutates global state
    When the Python clean code gate checks the file
    Then the gate reports the global statement and fails

  Scenario: Clean Python passes
    Given a Python file with no clean code findings
    When the Python clean code gate checks the file
    Then the gate succeeds without findings
