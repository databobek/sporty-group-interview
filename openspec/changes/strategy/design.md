# Design: Strategy and recommendations (Part C)

## Decision log

Decided on 2026-11-12.

| # | Decision | Options considered | Chosen |
|---|---|---|---|
| S1 | Recommendations | test data strategy / push rules down to the API / CI gating and known defects / spec and testability fixes | Spec and testability fixes, and automating the remaining scenarios, since none of them needs to be manual |
| S2 | Manual-only section | (follows from S1) | No test-plan scenario is inherently manual. The four that were not automated were left out only because the brief scopes Part B to two tests. Only work that needs judgment (exploratory testing, wording and clarity, undefined behavior) stays manual. |
| S3 | Branch | this branch / a new branch / main | `test-execution-12.11.2026` |

## Smaller calls

- The file name `strategy-and-recommendations.md`.
- The "why not the others" table draws on the execution results: TC-02 found the two worst defects, so it is
  named as the first to automate next.
