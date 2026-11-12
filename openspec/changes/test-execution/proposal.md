# Change: Test execution and bug reports (Part A.2)

## Why

The assignment asks for the three highest-priority scenarios to be run against the application, plus a few
minutes of exploratory checks around bet placement, with every defect reported in a fixed format: Bug ID and
title, severity, reproduction steps, expected vs actual, business impact, and evidence.

## What Changes

- Execute TC-01, TC-02 and TC-03 from `test-plan.md`, and record the results step by step in `execution-results.md`.
- Explore stake input edge cases in the bet slip.
- Report each defect in `bug-reports.md` (BUG-01 onwards, ordered by severity), with evidence in `evidence/`.

## Impact

- Affected specs: `test-execution` (new)
- Affected files: `execution-results.md`, `bug-reports.md`, `evidence/**`
