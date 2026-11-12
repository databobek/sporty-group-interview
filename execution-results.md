# Execution Results: Single Bet Placement

| | |
|---|---|
| Date | 2026-11-12 |
| Application | `https://qae-assignment-tau.vercel.app/?user-id=<user-id>` (user-id masked in all evidence) |
| Browser | Latest desktop Chrome |
| Scope | The three Critical scenarios from [test-plan.md](test-plan.md) (TC-01, TC-02, TC-03) and exploratory checks on stake input |
| Defects | 11, reported in [bug-reports.md](bug-reports.md) |
| Evidence | [evidence/](evidence/): screenshots (`.png`) and API request/response pairs (`.txt`) |

## How it was executed

UI steps were done by hand in Chrome. API steps (resets, balance reads, direct `POST /api/place-bet`
calls) were sent as plain HTTP requests, and each request and response was saved to `evidence/`.
The UI and the API share one user's balance, so every hand-over between them was coordinated.

Execution order was TC-03, TC-01, TC-02, then the exploratory checks.

## Summary

| Scenario | Result | Defects found |
|---|---|---|
| TC-01 Successful single bet placement | Fail | BUG-02, BUG-04, BUG-05, BUG-06, BUG-10, BUG-11 |
| TC-02 Insufficient balance boundary | Fail | BUG-01, BUG-02, BUG-03 |
| TC-03 Server-side price integrity | Fail as written; the price-integrity rule itself holds | BUG-03, BUG-08, BUG-09 |
| Exploratory: stake input | Pass, with two observations | none |

BUG-07 (past matches listed and bettable) came from the match list data seen during all three
scenarios.

A reset of the balance (test plan P3) never gives the expected €125.50. The reset replies €125.50 but
stores €120.00 (BUG-03), so any expected value that assumes €125.50 is off by €5.50. The tables below
show the expected value as written, and where that differs, the value relative to the real starting
balance.

## TC-03: Server-side price integrity (API)

Match: Bayern Munich vs Leverkusen (2026-11-13), home odds 1.75.

| Step | Expected | Actual | Result | Evidence |
|---|---|---|---|---|
| P3 | Reset gives balance €125.50 | Reply `125.5`; `GET /api/balance` right after: `120` | Fail (BUG-03) | `TC-03-01-reset.txt`, `TC-03-02-balance.txt` |
| 1 | 200; `odds` 1.75 (not 1000); `payout` 17.50 (not 99999); `balance` 115.50 | 200; `odds` 1.75 (correct); `payout` 17.5 (correct); `balance` 110 (correct for 120 − 10, but not the 115.50 written); `currency` `USD` | Fail as written; price integrity passes | `TC-03-04-place-bet.txt` |
| 2 | Balance matches the step 1 response | `110` = `110` | Pass | `TC-03-05-balance.txt` |

The server ignored the client's `odds`, `payout` and `balance`, which is the risk this scenario
targets. The scenario fails only because of the reset defect. The response also exposed BUG-08
(currency `USD`) and BUG-09 (no bet ID or timestamp).

## TC-01: Successful single bet placement (UI)

Match: Bayern Munich vs Leverkusen, odds `1` = 1.75, stake €10.00. P3 (reset) was not run before
this scenario, so the starting balance was recorded as €110.00 at step 2, and the later expectations
are relative to it.

| Step | Expected | Actual | Result | Evidence |
|---|---|---|---|---|
| 2 | Note the header balance | €110.00 (recorded as the start) | Pass | `TC-01-02-balance.png` |
| 3 | Slip: Bayern Munich vs Leverkusen, home, 1.75. Kickoff shows date and time. | Slip correct. Card shows only "Tomorrow". | Fail (BUG-11) | `TC-01-03-bet-slip.png` |
| 4 | Slip shows stake €10.00 and the available balance | Stake €10.00 is correct. No available balance in the slip. | Fail (BUG-10) | `TC-01-04-pre-place-bet.png` |
| 5 | Potential payout 10 × 1.75 = €17.50 | €17.50 | Pass | `TC-01-04-pre-place-bet.png` |
| 6 | `Placing...`, then a success receipt | `PLACING...`, then the receipt | Pass | `TC-01-05-placing.png` |
| 7 | Bet ID, Bayern Munich vs Leverkusen, selection home, €10.00, 1.75, €17.50, timestamp | #B-94384 (correct); "Leverkusen vs Bayern Munich" (swapped); no selection; €10.00 and 1.75 (correct); €20.00 (wrong); "TODAY, 18:05" (correct) | Fail (BUG-05, BUG-06, BUG-04) | `TC-01-06-bet-successful.png` |
| 8 | Slip empty; header €110 − €10 = €100.00 | Slip empty (correct); header still €110.00 | Fail (BUG-02) | `TC-01-07-bet-scucessful.png` |
| 9 | API balance = header | After this and the extra bet: API €90, header €110 | Fail (BUG-02) | `TC-01-step9-api-balance.txt` |
| Extra | A second identical bet gets a different Bet ID | #B-95018 ≠ #B-94384 | Pass | `TC-01-08-second-bet.png` |

The server deducted both €10 bets correctly, taking the balance from €110 to €90. The UI never showed it.

## TC-02: Insufficient balance boundary (UI + API)

### As written

P3 reset: reply €125.50, stored €120.00 (`TC-02-01-reset.txt`, `TC-02-02-balance.txt`).

| Step | Expected | Actual | Result | Evidence |
|---|---|---|---|---|
| 0 | Header after reload = stored balance | €120.00 | Pass | `TC-02-01-start.png` |
| 1 | €100.00 bet accepted; balance €25.50 | Accepted; receipt shows payout €200.00 (100 × 7.20 = €720.00) and swapped teams; header still €120.00; real balance €20.00 | Fail (BUG-02, BUG-04, BUG-05) | `TC-02-02.png` |
| 2 and 3 | €25.51: `Insufficient balance`, bet not placed | No message, bet placed. Receipt: payout €51.02 (should be €77.81). | Fail (BUG-02) | `TC-02-03-nobalanceblock.png` |
| 3a | Balance check | API balance −€5.51 | Fail (BUG-01) | `TC-02-03-balance.txt` |
| 4 | API `stake: 25.51` returns 422 | 200, balance −€31.02 | Fail (BUG-01) | `TC-02-04-place-bet.txt` |
| 5 | Balance unchanged | −€31.02 (the bet in step 4 went through) | Fail (BUG-01) | `TC-02-05-balance.txt` |
| 6 | €25.50 accepted, balance €0.00 | Refused with `Insufficient balance`. That is correct for the real balance, which a freshly loaded page shows as −€31.02. | n/a (expectation no longer applies) | `TC-02-fresh-page-header.png` |
| 7 | Header and API €0.00 | n/a | n/a | |

### Repeated with the real balance (the rule itself)

| Step | Expected | Actual | Result | Evidence |
|---|---|---|---|---|
| Setup | Reset; €100 bet; reload; header €20.00 | €20.00 | Pass | `TC-02-intent-*-reset.txt`, `tc-02-intent-step3.png` |
| UI €20.01 (after reload) | `Insufficient balance`, blocked | `Insufficient balance`, blocked | Pass | `tc-02-intent-step4.png` |
| UI €20.00 | Accepted (stake == balance) | Accepted. Receipt payout €40.00 (20 × 2.95 = €59.00), teams swapped. | Pass (BUG-04, BUG-05 again) | `TC-02-intent-step5.png` |
| API €20.01 at balance €20.00 | 422 | 200, balance −€0.01 | Fail (BUG-01) | `TC-02-intent-api-01…05` |

The UI enforces the rule correctly when its balance is up to date. It is never updated after a bet,
though (BUG-02), and the API doesn't enforce the rule at all (BUG-01). Together they let a customer
bet money they don't have through the normal UI.

## Exploratory: stake input

Balance reset before the session (`X-setup-*`, `X-setup2-*`). Match: PSG vs Monaco, odds 1.65.

| # | Input | Observed | Result | Evidence |
|---|---|---|---|---|
| X1 | `1` | Accepted, payout €1.65 | Pass | `X-01.png` |
| X2 | `0.99` | `Minimum stake is €1.00`, Place Bet disabled | Pass | `X-02.png` |
| X3 | `100` | Accepted, payout €165.00 | Pass | `X-03.png` |
| X4 | `100.01` | `Maximum stake is €100.00`, Place Bet disabled | Pass | `X-04.png` |
| X5 | `0`, `-5` | `0` gives the minimum message. `-` cannot be typed. | Pass | `x-05.png` |
| X6 | `10.555` | A third decimal cannot be typed | Pass | (no screenshot) |
| X7 | `1,50` / `1.50` | Both accepted | Pass (DA-G5) | (no screenshot) |
| X8 | `00010` | Read as €10.00 (the field keeps showing `00010`) | Pass | `x-08a.png`, `x-08b.png` |
| X9 | letters, spaces | Not accepted | Pass | (no screenshot) |
| X10 | paste `12.345` | Becomes `12.34` | Pass | `x-10.png` |
| X11 | clear the field | Place Bet disabled, no message | Pass | `x-11.png` |
| X12 | switch to another match's odds | Stake reset to 0.00 | Observation (DA-G20) | `x-12.png` |
| X13 | click the selected odds again | Stays selected, no toggle-off | Observation (DA-G20) | `x-13.png` |
| X14 | Remove the selection | Slip empty: no selection, no stake | Pass (DA-C3) | `x14.png` |

The stake input enforces the spec's limits well: minimum, maximum, 2 decimal places, numbers only,
and both decimal separators. The spec doesn't define X12 and X13 (DA-G20), so they are recorded as
observations only.

## Observations that are not defects

- Receipt timestamp: local time, cut down to the minute, with a relative day ("TODAY, 18:05").
  Logged as a documentation issue in DA-G19.
- Dates follow the browser locale: a Polish browser shows "czw., 05 lis", and an en-US browser
  shows relative words such as "Tomorrow".
- Invalid stakes still show a payout: the slip shows a potential payout for out-of-range stakes,
  e.g. €1.63 for €0.99. Cosmetic.
