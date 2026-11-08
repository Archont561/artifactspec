Feature: Select commits for conventional commit checks
  Scenario: Force-pushed branch has an unavailable previous commit
    Given a branch with two commits after the default branch
    When CI selects the range for a force-push with a missing previous commit
    Then all branch commits since the default merge base are selected
