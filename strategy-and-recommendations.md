# Strategy and Recommendations

Part C of the assignment. It builds on [test-plan.md](test-plan.md),
[execution-results.md](execution-results.md) and [bug-reports.md](bug-reports.md).

## Why these two tests were automated

The brief asks for one E2E UI test of a critical journey and one API test of a validation or business
rule. From the six scenarios in the test plan, two gave the most value for one test each:

### TC-01: successful single bet placement (UI)

This is the journey that earns money, and it touches
every part of the feature: match list, bet slip, placement, receipt, header balance and the API
balance. One run cross-checks four places that must agree on the same amounts, so a single test
covers a lot of risk. It has a stable oracle (the spec plus the DA decisions), and it caught 8
defects on its first run.

### TC-03: server-side price integrity (API)

A client that can set its own odds or balance is a
fraud risk that the UI cannot prevent and only the server can. The test needs no browser, runs in
seconds, is deterministic, and a failure is unambiguous.

### Why not the others

| Scenario | Why it was not one of the two |
|---|---|
| TC-02 Insufficient balance | Critical as well, but it needs a sequence of bets to reach the boundary (the starting balance is above the maximum stake), and it depends on a working reset, which turned out to be broken (BUG-03). It found the two worst defects (BUG-01, BUG-02), so it is the first one to automate next. |
| TC-04 Stake boundaries | High, and cheap to automate as a parametrized API test. The risk it covers (limits) is lower than money or fraud, and exploratory testing showed the UI enforces the limits well. |
| TC-05 Outcome mapping | High. TC-01 already covers the home selection and the receipt's team order, which is where the swap defect (BUG-05) showed up. |
| TC-06 Duplicate placement | High, but its API half depends on two requests overlapping in time (blocker B-01). An automated pass would prove little, and a flaky test costs more than it gives. |

## What was left manual, and why

No scenario in the test plan has to be manual. TC-02, TC-04, TC-05 and TC-06 were left out of
automation only because the brief scopes Part B to two tests. The framework is designed so that each
of them fits without restructuring (see the framework design in
`openspec/changes/framework-design/design.md`).

What stays with a person is the work that needs judgment rather than a fixed expected result:

- Exploratory testing, like the stake-input session in Part A.2. Its value is in finding what
  nobody wrote a check for.
- Wording and clarity: whether the error modal "explains that the bet could not be processed"
  (§2.5), or whether filter feedback is "clear" (§2.6). Automation can check that text exists, not
  whether it helps.
- Undefined behavior: the observe-only gaps (DA-G15, DA-G20, DA-G21) have no expected result
  until the spec defines one.

## Recommendations if the project scales

### 1. Fix the spec and add testability hooks

Most of the cost in this project came from the spec, not the app: 6 contradictions and 21 gaps
needed a decision before a test could be written ([documentation-analysis.md](documentation-analysis.md)).
The clarifications that would unblock the most testing:

- Server-side balance rule. State explicitly that the API rejects stakes above the balance (422).
  Today only the UI tries (BUG-01, BUG-02).
- Payout rounding and money precision. Define a rounding mode and carry money as exact decimals
  or integer cents, not JSON floats (DA-G1, DA-G18).
- Status-code mapping. For each error case, name the status code (400 vs 422, DA-C5) and an
  error body schema (DA-G10).
- Bet ID and placement time from the server. Return them from `POST /api/place-bet` so the
  receipt can be verified (BUG-09, DA-C4, DA-G19).

The testability hooks would make the remaining scenarios deterministic:

- A way to force a placement failure, which makes the error modal and Rebet (§2.5) testable.
- A way to hold a bet "in progress", which removes TC-06's timing problem (B-01).
- Stable `data-testid` attributes on the elements tests use. Today the ids are good but
  undocumented.
- A reset that is verified. Reset must store what it replies (BUG-03). Every test depends on
  it.

### 2. Automate the remaining scenarios

With the hooks above, every scenario in the test plan can be automated with the existing framework:

| Scenario | How |
|---|---|
| TC-02 | API test for the server rule; UI test for "header and slip update after a bet" (BUG-02) |
| TC-04 | Parametrized API test over the case table; one UI test for the messages |
| TC-05 | API test per selection; UI check of slip and receipt per selection |
| TC-06 | API test using the "hold in progress" hook; UI double-click test |
| Error modal (#7) | UI test using the "force a failure" hook |
