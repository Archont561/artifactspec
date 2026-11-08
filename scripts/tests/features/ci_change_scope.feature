Feature: Select the appropriate CI checks for changed files
  Scenario Outline: Select a safe scope for a change
    Given a repository with a change to "<path>"
    When CI detects the changed files
    Then the selected CI scope is "<scope>"

    Examples:
      | path                                     | scope   |
      | docs/guide.md                            | docs    |
      | backlog/tasks/ART-1.md                   | docs    |
      | scripts/maintenance.py                   | scripts |
      | scripts/tests/test_detection.py          | scripts |
      | packages/artifactspec/tests/scripts/a.py | full    |
      | packages/artifactspec/src/app.py         | full    |
      | .github/workflows/ci.yml                 | full    |
