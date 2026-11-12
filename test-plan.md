# Test Plan: Single Bet Placement

| | |
|---|---|
| Feature | Single Bet Placement (desktop web, pre-match football, single bets) |
| Test basis | Feature Specification (*SPEC*), plus the decisions in [documentation-analysis.md](documentation-analysis.md) (*DA-xx*) |
| Application under test | `https://qae-assignment-tau.vercel.app/?user-id=<user-id>` |
| Status | Draft for review |

## 1. Introduction

### 1.1 Purpose

This plan defines six prioritized scenarios for the Single Bet Placement feature. They were chosen by
risk: the risk of losing money, of placing a bet the customer did not intend, and of breaking a limit
the business has committed to. For each scenario the plan says whether it can be executed now or is
blocked by an open question.

### 1.2 Scope

In scope: match selection, the bet slip, stake validation, bet placement through the UI and API,
the success receipt, and balance handling.

Out of scope: everything the spec excludes (live betting, accumulators, other sports, mobile UX),
plus filters, catalog data quality, protocol-level API errors and the error modal. These were considered
and ranked below the six selected scenarios. Part C explains why.

### 1.3 Source of truth

The feature spec is the reference. Where the application differs from it, the difference is reported as
a defect in the application and the test stays as written. Where the spec is silent or contradicts
itself, the decision recorded in `documentation-analysis.md` is the expected result, and each step cites
the DA-ID it relies on.

## 2. Approach

### 2.1 Priority definitions

| Priority | Meaning |
|---|---|
| Critical | A failure loses money directly (wrong balance, wrong price) or blocks the core journey. |
| High | A failure places a bet the customer didn't intend, or breaks a stated product limit. |
| Medium | A failure degrades the experience or data quality, with no money at stake. |
| Low | Cosmetic or test-support behavior. |

### 2.2 Test layers

| Layer | Used for |
|---|---|
| UI (desktop Chrome) | What the customer sees and does: selection, bet slip, messages, receipt. |
| API (`/api/*`) | Rules the server must enforce on its own, because a client can skip the UI. |

Several scenarios check the same rule at both layers on purpose. The spec marks most stake rules as
"UI + API", and a rule that only the UI enforces can be bypassed.

### 2.3 Execution order

The three Critical scenarios (TC-01, TC-02 and TC-03) are executed manually first, as Part A.2 of the
assignment requires. TC-01 (UI) and TC-03 (API) are the proposed automation candidates for Part B. That
choice is confirmed when the framework is designed.

## 3. Prerequisites

These are what a tester needs before running any scenario. How the automation framework provides them
is defined later, in the framework design.

| # | Prerequisite | Detail |
|---|---|---|
| P1 | Browser | Latest desktop Chrome, desktop window size. |
| P2 | Fresh user | A new `user-id` per scenario run (e.g. `qa-<scenario>-<timestamp>`), so balances and in-progress bets from other runs can't interfere. |
| P3 | Known balance | `POST /api/reset-balance` with header `x-user-id: <user-id>` before the scenario. Expected balance afterwards: €125.50 (DA-G17). |
| P4 | Catalog snapshot | `GET /api/matches` with the same header, used to pick a match and read its odds. Odds stay the same for the whole run (DA-G16). |
| P5 | API client | Any HTTP client that can send JSON and custom headers: Swagger UI at `/api/docs`, curl, or Postman. |
| P6 | Evidence | Screenshots of the main UI states, and the request and response of every API step. |

Money is compared to 2 decimal places with a €0.01 tolerance (DA-G1, DA-G18).

## 4. Scenario summary

| ID | Title | Priority | Layer | Feasibility |
|---|---|---|---|---|
| TC-01 | Successful single bet placement | Critical | UI (+API check) | Executable |
| TC-02 | Insufficient balance boundary | Critical | UI + API | Executable |
| TC-03 | Server-side price integrity | Critical | API | Executable |
| TC-04 | Stake minimum, maximum and precision boundaries | High | UI + API | Executable |
| TC-05 | Outcome selection maps to the correct odds and side | High | UI + API | Executable |
| TC-06 | Duplicate placement protection | High | UI + API | Partially blocked (B-01, see [§6](#6-unknowns-and-blockers)) |

*Executable* means every step has a defined expected result. *Partially blocked* means some steps can
run, but at least one result depends on something the spec doesn't define.

## 5. Scenarios

### TC-01: Successful single bet placement

| | |
|---|---|
| Priority | Critical |
| Layer | UI, with an API cross-check |
| Feasibility | Executable |
| References | SPEC §2.1 to §2.4; DA-C2, DA-C4, DA-G1, DA-G17, DA-G19 |

Risk rationale: this is the journey that earns money. If it fails, no bets are taken. If it
"succeeds" with the wrong numbers, the business charges or pays out the wrong amount. The receipt is the
customer's only record of the bet, so every value on it has to match what they agreed to.

Preconditions: P1 to P4. Pick any match *M* from the catalog, and let *O* be its home odds.

Steps:

1. Open the application with `?user-id=<user-id>`.
2. Note the balance shown in the header.
3. On match *M*, click odds button `1`.
4. Enter a stake of €10.00 in the bet slip.
5. Note the potential payout shown in the bet slip.
6. Click `Place Bet`.
7. Note the receipt values.
8. Close the receipt.
9. Call `GET /api/balance`.

Expected results:

| Step | Expected |
|---|---|
| 2 | Header balance is €125.50. |
| 3 | Bet slip shows *M* (home team first), selection home/`1`, odds *O*. The match list shows a kickoff date and time (DA-C2). |
| 4 | Bet slip shows stake €10.00 and available balance €125.50. |
| 5 | Potential payout is 10.00 × *O* (±€0.01). |
| 6 | Button shows `Placing...`, then a success receipt appears. |
| 7 | Receipt shows a non-empty Bet ID, *M* (home vs away), selection `1`/home, stake €10.00, odds *O*, the payout from step 5, and a timestamp within a few minutes of now (DA-G19). |
| 8 | Receipt closes. Bet slip has no selection and no stake. Header balance is €115.50. |
| 9 | API balance is 115.50, the same as the header. |

Then place a second bet the same way. Its Bet ID must differ from the first one (DA-G19).

### TC-02: Insufficient balance boundary

| | |
|---|---|
| Priority | Critical |
| Layer | UI + API |
| Feasibility | Executable |
| References | SPEC §4.1, §4.4; DA-G2, DA-G3 |

Risk rationale: if a stake larger than the balance is accepted, the balance can go negative. That is
credit the business never agreed to give, and possibly a regulatory breach. If a stake equal to the
balance is rejected, the customer is wrongly blocked from using all their funds.

The starting balance (€125.50) is above the maximum stake (€100.00), so the balance rule can't be
reached until the balance drops below €100. The scenario spends money first to get there.

Preconditions: P1 to P5.

Steps:

1. Through the UI, place a €100.00 bet on any match.
2. Select odds on any match and enter a stake of €25.51.
3. Try to place the bet.
4. Through the API, send `POST /api/place-bet` with a valid match and selection and `stake: 25.51`.
5. Call `GET /api/balance`.
6. Through the UI, change the stake to €25.50 and place the bet.
7. Check the header balance, then call `GET /api/balance`.

Expected results:

| Step | Expected |
|---|---|
| 1 | Bet accepted. Balance is €25.50. |
| 2 and 3 | Message `Insufficient balance`. The bet is not placed. |
| 4 | 422. The bet is not placed. |
| 5 | Balance is still 25.50. |
| 6 | Bet accepted, since a stake equal to the balance is allowed (DA-G2). |
| 7 | Header and API balance are both €0.00. |

### TC-03: Server-side price integrity

| | |
|---|---|
| Priority | Critical |
| Layer | API |
| Feasibility | Executable |
| References | SPEC §5.3 (place-bet: "Extra fields may be ignored"); DA-G1, DA-G11 |

Risk rationale: the API accepts JSON from the client, and anyone can send JSON. If the server uses
odds, payout or balance values sent by the client, a customer can set their own price or top up their
own balance. That is direct fraud, and only the server can prevent it.

Preconditions: P2 to P5. Pick match *M* from the catalog, and let *O* be its home odds.

Steps:

1. Send `POST /api/place-bet` with:
   ```json
   {
     "matchId": "<M.id>",
     "selection": "HOME",
     "stake": 10.00,
     "odds": 1000.00,
     "payout": 99999.00,
     "balance": 99999.00
   }
   ```
2. Call `GET /api/balance`.

Expected results:

| Step | Expected |
|---|---|
| 1 | 200. `odds` is *O*, not 1000. `payout` is 10.00 × *O* (±€0.01), not 99999. `balance` is 115.50, not 99999. |
| 2 | Balance is 115.50, matching the response in step 1. |

### TC-04: Stake minimum, maximum and precision boundaries

| | |
|---|---|
| Priority | High |
| Layer | UI + API |
| Feasibility | Executable |
| References | SPEC §3, §4.1, §4.4; DA-C1, DA-C5, DA-G2, DA-G4, DA-G5 |

Risk rationale: stake limits are product and regulatory commitments. Off-by-one bugs live at
boundaries, and this spec already disagrees with itself about the minimum (€1.00 vs €1.01, DA-C1).
Accepting a stake outside the limits breaks a commitment, and rejecting one inside them turns away a
valid bet.

Preconditions: P1 to P5. Reset the balance (P3) before each accepted case, so earlier bets don't
change the result.

Run each case in the UI (enter the stake, try to place the bet) and through the API
(`POST /api/place-bet`):

| # | Stake | UI expected | API expected | Ref |
|---|---|---|---|---|
| a | 0.99 | Blocked, `Minimum stake is €1.00` | 422 | DA-C1 |
| b | 1.00 | Accepted | 200 | DA-C1, DA-G2 |
| c | 100.00 | Accepted | 200 | DA-G2 |
| d | 100.01 | Blocked, `Maximum stake is €100.00` | 422 | §4.4 |
| e | 10.555 | Blocked, with some visible feedback | 422 | §4.1, DA-G4 |
| f | `1,00` (comma) | Accepted as €1.00 | n/a (UI input only) | DA-G5 |

In every rejected case the balance must stay unchanged.

### TC-05: Outcome selection maps to the correct odds and side

| | |
|---|---|
| Priority | High |
| Layer | UI + API |
| Feasibility | Executable |
| References | SPEC §2.1, §2.2, §4.2, §5.3; Glossary *Odds*, *Match Ordering* |

Risk rationale: `1`, `X` and `2` have to reach the server as `HOME`, `DRAW` and `AWAY`, with the
matching odds. If home and away are swapped, the customer backs the wrong team at the wrong price. They
may not notice until the match is settled, and by then the dispute is the operator's problem.

Preconditions: P1 to P5. Pick match *M*, with catalog odds *Oh*, *Od* and *Oa*.

Steps:

1. In the UI, click `1` on *M*.
2. Click `X` on *M*.
3. Click `2` on *M*.
4. Enter €5.00 and place the bet.
5. Through the API, place three €1.00 bets on *M*: one each with `HOME`, `DRAW` and `AWAY`.

Expected results:

| Step | Expected |
|---|---|
| 1 | Bet slip shows one selection: home team, odds *Oh*. |
| 2 | The selection is replaced by draw, odds *Od*. Still one selection. |
| 3 | Replaced again by away team, odds *Oa*. Still one selection. |
| 4 | Receipt shows *M* as "home vs away" (home first), selection `2`/away, odds *Oa*, payout 5.00 × *Oa* (±€0.01). |
| 5 | Each 200 response echoes its `selection`, with `odds` equal to *Oh*, *Od* and *Oa* respectively. |

### TC-06: Duplicate placement protection

| | |
|---|---|
| Priority | High |
| Layer | UI + API |
| Feasibility | Partially blocked (B-01) |
| References | SPEC §2.3, §5.3 (`409`); DA-G8 |

Risk rationale: customers double-click and networks retry. If one intent produces two bets, the
customer is charged twice and the operator has a complaint or a refund to deal with. The spec defines
`409` for exactly this case.

Preconditions: P1 to P5.

Steps:

1. In the UI, select odds, enter €10.00, and double-click `Place Bet`.
2. Check how many receipts appear and the header balance.
3. Through the API, send two `POST /api/place-bet` requests for the same user at the same time.
4. Call `GET /api/balance`.
5. As a control, repeat step 3 with two different user-ids.

Expected results:

| Step | Expected |
|---|---|
| 1 | `Place Bet` can't fire again while `Placing...` is shown (DA-G8). |
| 2 | One receipt. Balance is €115.50 (one deduction). |
| 3 | One 200 and one 409. |
| 4 | Balance is 115.50 (one deduction). |
| 5 | Both requests return 200, because the 409 applies to the same user only. |

Steps 3 to 5 only prove something if the two requests overlap in time. A pass is weak evidence, since
the second request may have arrived after the first one finished. A fail (two 200s, a double deduction)
is conclusive. See B-01.

## 6. Unknowns and blockers

| ID | Affects | Unknown | Effect | Unblocked by |
|---|---|---|---|---|
| B-01 | TC-06 steps 3 to 5 | The spec defines `409` "bet already in progress" but not how long a bet stays in progress. | The two requests can't be guaranteed to overlap, so a pass doesn't prove the protection exists. Steps 1 and 2 (UI) are executable. | A documented processing window, or a test hook that holds a bet in progress. |
| B-02 | TC-01 step 7 | The place-bet response has no Bet ID or timestamp (DA-C4). | The receipt's Bet ID and timestamp can only be checked for presence, uniqueness and plausibility, not against the server. This is already reported as an API contract defect. | The API returning a server-side Bet ID and timestamp. |
| B-03 | TC-04 case e (API) | JSON numbers are binary floats, so `10.555` may arrive as `10.55499…`. | The API precision check could pass or fail for reasons unrelated to validation. | The spec defining stake precision on the wire (e.g. a decimal string or integer cents). |

B-02 and B-03 don't stop execution, but they limit how strong the conclusion can be. B-01 is the only one
that blocks part of a scenario.

## 7. Entry and exit criteria

Entry:

- The application and `/api/*` are reachable.
- `POST /api/reset-balance` works (P3).
- The catalog returns at least one match.

Exit, for this round:

- TC-01, TC-02 and TC-03 have been executed.
- Every defect found has been reported in the bug report document.
- Every blocked step has been recorded as blocked, not as passed.
