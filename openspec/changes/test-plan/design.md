# Design: Test plan (Part A.1)

## Context

A pool of 12 candidate scenarios was ranked by risk to money and to bet integrity, and each was checked
for how well it can be automated. None is strictly impossible to automate, but #6 (duplicate placement)
depends on timing and #7 (error modal) needs a way to inject a failure.

## Decision log

Decided on 2026-11-12.

| # | Decision | Options considered | Chosen |
|---|---|---|---|
| 1 | Order of work | the test plan includes the framework design / tests first, then the framework | Tests first: define the problem, then solve it. The framework design is a later change. |
| 2 | Source of truth | explore the live app first / spec only | The feature spec serves as the documentation. Where the app differs, that is a defect, and the test stays as written. |
| 3 | Reporting | (set for the project) | pytest with Allure. How the Allure CLI is installed (Java or Node) is decided in the framework change. |
| 4 | Scope beyond the brief's 5 or 6 | 6 in full plus an appendix / all 12 in full / 6 in full only | 6 in full, no appendix. The cut candidates are covered in Part C only. |
| 5 | Which six | #1 to #6 / swap #6 for #8 / swap #6 for #7 | #1 to #6: happy path, insufficient balance, price integrity, stake boundaries, outcome mapping, duplicate placement. |
| 6 | Feasibility | (set for the plan) | Each test is marked Executable or Partially blocked, with a blocker register. |
| 7 | Style | (set for the plan) | Plain, direct prose. |
| 8 | Blocker register (B-01 to B-03) | keep all / keep B-01 only / move to the doc analysis / remove | Keep all three. B-03 is also recorded in `documentation-analysis.md` under DA-G18. |

## Scenarios considered and not selected (for Part C)

| # | Candidate | Priority | Why it was cut |
|---|---|---|---|
| 7 | Error modal: Rebet and Close | High | There is no way to force a server failure from outside the app (it needs request interception), and Rebet behavior isn't fully defined (DA-G6). |
| 8 | API protocol errors (400/401/405/422) | Medium | No money at stake. |
| 9 | Catalog data (upcoming only, odds range, kickoff time) | Medium | Data quality, with no money at stake. |
| 10 | Bet on a past match is rejected | Medium | No documented past match to use as test data. |
| 11 | Filters | Medium | Usability only. |
| 12 | Reset-balance consistency | Low | Test-support endpoint. |

## Smaller calls

- Scenario IDs are `TC-01` to `TC-06`, prerequisites `P1` to `P6` and blockers `B-01` to `B-03`.
- TC-02 spends €100.00 first. The starting balance (€125.50) is above the maximum stake (€100.00), so the
  balance boundary can't be reached any other way.
