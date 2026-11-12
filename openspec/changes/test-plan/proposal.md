# Change: Test plan (Part A.1)

## Why

The assignment asks for 5 or 6 prioritized test scenarios. The automation framework (Part B) is designed
from these scenarios, so they come first: define the problem before solving it.

## What Changes

- Add `test-plan.md` at the repository root, with:
  - Six fully specified scenarios, TC-01 to TC-06, each with priority, risk rationale, steps and expected results
  - Prerequisites P1 to P6 (browser, fresh user-id, balance reset, catalog snapshot, API client, evidence)
  - A feasibility status per scenario, and a register of unknowns and blockers (B-01 to B-03)
  - Entry and exit criteria
- The framework design follows in its own change.

## Impact

- Affected specs: `test-plan` (new)
- Affected files: `test-plan.md`
- Downstream: Part A.2 executes TC-01 to TC-03; Part B automates the candidates TC-01 (UI) and TC-03 (API)
