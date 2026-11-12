# Design: Documentation analysis

## Context

Both source documents were reviewed section by section: the feature spec and the assignment's domain
glossary. Each finding was classified as a contradiction (two conflicting statements), a gap (undefined
behavior) or an editorial issue. Each contradiction and each gap that affects a test oracle got an
explicit decision.

## Decision log

Decided on 2026-11-12. The full wording is in `documentation-analysis.md`.

### Contradictions

| ID | Topic | Options considered | Chosen |
|---|---|---|---|
| DA-C1 | Min stake | €1.00 / €1.01 / test both with no oracle | €1.00, inclusive |
| DA-C2 | Kickoff time | date must match the API / time is required | Time is required; a missing time is a defect |
| DA-C3 | Remove All vs `x` | clear the selection / clear selection and stake / out of scope | Clear the selection and the stake |
| DA-C4 | Receipt vs API | presence and consistency / also flag the API | Flag the API as a defect (no bet ID, timestamp or match details) |
| DA-C5 | 400 vs 422 | 422 for field errors / 400 for type, 422 for value / accept either | 422 for every field error |
| DA-C6 | Upcoming only | `kickoffDate` on or after today / the API also rejects past matches | The API must also reject past matches (422) |

### Gaps

| ID | Topic | Chosen | Doc issue |
|---|---|---|---|
| DA-G1 | Payout rounding | Consistency only, within €0.01 of the exact product | Yes |
| DA-G2 | Inclusive boundaries | All inclusive | |
| DA-G3 | Message precedence | No precedence chosen; only "blocked" is asserted | Yes |
| DA-G4 | Missing copy | Blocked, with some visible feedback | Yes |
| DA-G5 | Decimal separator | Both `.` and `,` must work | Yes |
| DA-G6 | Rebet | Same data, single deduction | Yes |
| DA-G7 | Idempotency | Observe only | Yes |
| DA-G8 | Double submit | UI blocks, and the API returns 409 | Yes |
| DA-G9 | Invalid user id | Missing, empty or blank gives 401 | Yes |
| DA-G10 | Error body schema | Observe only | Yes |
| DA-G11 | Extra fields | Must be ignored | Yes |
| DA-G12 | Odds range data | Check the catalog | Yes |
| DA-G13 | Odds filter | Any of the three odds in range | Yes |
| DA-G14 | Date filter | Reversed range rejected | Yes |
| DA-G15 | Filter and selection | Observe only | Yes |
| DA-G16/G17 | Session, balance | Odds stable per run; €125.50 per user | Yes |
| DA-G18 | Float precision | 2 dp with a €0.01 tolerance | Yes |
| DA-G19 | Receipt formats | Unique ID, timestamp close to placement | Yes |
| DA-G20 | Slip behavior | Observe only | Yes |
| DA-G21 | UI without user-id | Observe only | Yes |

### Process

- Each gap was decided on its own, not accepted as a batch of defaults.
- Git: the analysis is the second commit, `documentation analysis`, on top of the setup commit.

## Approach

Where the spec is silent, the gap is flagged as a documentation issue instead of being quietly assumed.
Assertions stay as weak as the spec allows: consistency or a tolerance rather than an invented rule. Later
steps follow the same approach.
