# Change: Documentation analysis

## Why

The feature spec contradicts itself (e.g. a minimum stake of €1.00 vs €1.01) and leaves a lot of behavior
undefined. Test scenarios need an unambiguous oracle, so every contradiction and gap needs an explicit
decision before the test plan is written.

## What Changes

- Add `documentation-analysis.md` at the repository root with:
  - 6 contradictions (DA-C1 to C6), each with a decision
  - 21 gaps (DA-G1 to G21), each with a test basis
  - 5 editorial issues (DA-E1 to E5)
  - 27 documentation issues to raise with the product owner (used in Part C)
- Add the `test-basis` capability: the decided assumptions that later test work must follow.

## Impact

- Affected specs: `test-basis` (new)
- Affected files: `documentation-analysis.md`
- Downstream: test plan (Part A.1), execution and bug reports (A.2), automation (B), recommendations (C)
