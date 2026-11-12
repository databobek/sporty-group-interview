## ADDED Requirements

### Requirement: Prioritized scenarios

The test plan SHALL contain exactly six fully specified scenarios. Each SHALL have an ID and title, a
priority (Critical / High / Medium / Low), a risk rationale, steps and expected results.

#### Scenario: Reviewer reads a scenario

- **WHEN** a reviewer opens any scenario in `test-plan.md`
- **THEN** it shows all five required fields, and every expected result cites either a SPEC section or a DA-ID

### Requirement: Feasibility status

Each scenario SHALL be marked Executable or Partially blocked. Every blocker SHALL be listed with
the unknown behind it, its effect, and what would unblock it.

#### Scenario: A step depends on undefined behavior

- **WHEN** a step's expected result relies on something the spec doesn't define and no DA decision covers it
- **THEN** the scenario is marked Partially blocked and the step is recorded in the blocker register

### Requirement: Test prerequisites

The test plan SHALL list the prerequisites needed to run any scenario: browser, test user isolation,
known starting balance, catalog snapshot, API client and evidence capture.

#### Scenario: Fresh run

- **WHEN** a tester starts a scenario
- **THEN** they use a new user-id and reset its balance to €125.50 first

### Requirement: Execution and automation selection

The three Critical scenarios SHALL be the ones executed in Part A.2. TC-01 (UI) and TC-03 (API) SHALL be the
proposed automation candidates, to be confirmed in the framework design.

#### Scenario: Part A.2 execution

- **WHEN** manual execution starts
- **THEN** TC-01, TC-02 and TC-03 are run, in that order
