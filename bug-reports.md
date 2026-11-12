# Bug Reports: Single Bet Placement

Found during the execution of TC-01, TC-02 and TC-03 and the exploratory checks
([execution-results.md](execution-results.md)). All evidence is in [evidence/](evidence/). The
user-id is masked as `***` in every file.

## Severity scale

| Severity | Meaning |
|---|---|
| Critical | Wrong money moved or recorded, or a security hole |
| High | A wrong bet, or a wrong record of a bet; a spec rule not enforced |
| Medium | A spec deviation with a workaround, or no direct money impact |
| Low | Cosmetic or copy |

## Summary

| ID | Title | Severity | Found in |
|---|---|---|---|
| [BUG-01](#bug-01-api-accepts-stakes-above-the-balance-and-the-balance-goes-negative) | API accepts stakes above the balance, and the balance goes negative | Critical | TC-02 |
| [BUG-02](#bug-02-ui-never-refreshes-the-balance-after-a-bet-and-validates-against-the-old-value) | UI never refreshes the balance after a bet, and validates against the old value | Critical | TC-01, TC-02 |
| [BUG-03](#bug-03-reset-balance-replies-12550-but-stores-12000) | Reset-balance replies €125.50 but stores €120.00 | Critical | TC-02, TC-03 |
| [BUG-04](#bug-04-receipt-shows-a-payout-of-2--stake-instead-of-stake--odds) | Receipt shows a payout of 2 × stake instead of stake × odds | High | TC-01, TC-02 |
| [BUG-05](#bug-05-receipt-swaps-the-home-and-away-teams) | Receipt swaps the home and away teams | High | TC-01, TC-02 |
| [BUG-06](#bug-06-receipt-does-not-show-the-selection) | Receipt does not show the selection | High | TC-01 |
| [BUG-07](#bug-07-past-matches-are-listed-as-upcoming-and-accept-bets) | Past matches are listed as upcoming and accept bets | High | TC-01, TC-03 |
| [BUG-08](#bug-08-place-bet-response-reports-the-currency-as-usd) | Place-bet response reports the currency as USD | Medium | TC-03 |
| [BUG-09](#bug-09-place-bet-response-has-no-bet-id-timestamp-or-match-details) | Place-bet response has no bet ID, timestamp or match details | Medium | TC-03 |
| [BUG-10](#bug-10-bet-slip-hides-the-available-balance-once-a-selection-is-made) | Bet slip hides the available balance once a selection is made | Medium | TC-01 |
| [BUG-11](#bug-11-match-list-shows-no-kickoff-time) | Match list shows no kickoff time | Medium | TC-01 |

## BUG-01: API accepts stakes above the balance, and the balance goes negative

- Severity: Critical
- Spec: §4.1 "Stake must not exceed available balance (UI + API): show/reject as insufficient balance"

Reproduction steps:

1. `POST /api/reset-balance` with `x-user-id: <id>`. Then `GET /api/balance` returns `120`.
2. `POST /api/place-bet` `{"matchId": "bundesliga-bayern-leverkusen-2026-11-13", "selection": "HOME", "stake": 100}`. The balance becomes `20`.
3. `POST /api/place-bet` with the same body and `"stake": 20.01`.

Expected: 422, bet rejected as insufficient balance. Balance stays €20.00.

Actual: 200 `"Bet placed successfully"`, `"balance": -0.01`. Repeating with larger stakes takes the balance to −€31.02.

Business impact: customers can bet money they don't have. The operator extends unlimited credit,
cannot collect losses, and may breach gambling regulations on affordability.

Evidence: `TC-02-intent-api-01-reset.txt` to `TC-02-intent-api-05-balance.txt` (exact boundary);
`TC-02-04-place-bet.txt` (balance −31.02).

## BUG-02: UI never refreshes the balance after a bet, and validates against the old value

- Severity: Critical
- Spec: §2.3 "On success: stake is deducted"; §4.1 balance rule; glossary "The balance is shared across the header and the bet slip"

Reproduction steps:

1. Reset the balance (stored €120.00). Open or reload the app. The header shows €120.00.
2. Place a €100.00 bet and close the receipt.
3. Note the header. It still shows €120.00, but the real balance is €20.00.
4. Select any odds and enter €25.51.
5. Click Place Bet.

Expected: after step 2 the header and bet slip show €20.00. At step 4, `Insufficient balance`
appears and Place Bet is blocked.
Actual: the header stays at €120.00. €25.51 is accepted without a message and the bet is placed.
The real balance is now −€5.51. Only a page reload shows the correct balance, and after a reload the
UI does block the stake (so the rule exists, but it checks a value that is out of date).

Business impact: the customer sees more money than they have and can overspend through the normal
UI. Together with BUG-01, nothing stops the balance going negative.

Evidence: `TC-01-07-bet-scucessful.png` (header €110 after a €10 bet); `TC-02-02.png` (header
€120 after a €100 bet); `TC-02-03-nobalanceblock.png` (€25.51 placed); `TC-02-03-balance.txt`
(−€5.51); `TC-02-fresh-page-header.png` (fresh page shows the real balance); `tc-02-intent-step3.png`
and `tc-02-intent-step4.png` (after a reload the rule works).

## BUG-03: Reset-balance replies €125.50 but stores €120.00

- Severity: Critical
- Spec: §5.3 "Resets user balance to initial configured value… Response body and persisted state must be consistent after reset"; glossary "Balance starts at €125.50"

Reproduction steps:

1. `POST /api/reset-balance` with `x-user-id: <id>`.
2. `GET /api/balance` with the same header.

Expected: both return `125.5`.

Actual: the reset replies `{"balance": 125.5}`, but `GET /api/balance` returns `120`. The app header
also shows €120.00 after a reload. Reproduced on every reset in the session (6 in the evidence).

Business impact: every reset leaves the customer €5.50 short of what the system reports. Any
process that trusts the reset response (support tools, reconciliation) records a balance that doesn't
exist.

Evidence: `TC-03-01-reset.txt` + `TC-03-02-balance.txt`; `TC-02-01-reset.txt` +
`TC-02-02-balance.txt`; `TC-02-01-start.png`.

## BUG-04: Receipt shows a payout of 2 × stake instead of stake × odds

- Severity: High
- Spec: §2.4 receipt "Potential payout"; glossary "Payout = stake × odds"; "All values should be consistent with what was shown before placement"

Reproduction steps:

1. Select odds 1.75 (Bayern Munich vs Leverkusen, `1`) and enter €10.00. The slip shows a potential payout of €17.50.
2. Place the bet.

Expected: the receipt shows a potential payout of €17.50, the same as the slip.

Actual: the receipt shows €20.00. The receipt payout is always exactly 2 × stake, whatever the odds:

| Stake | Odds | Correct | Receipt |
|---|---|---|---|
| €10.00 | 1.75 | €17.50 | €20.00 |
| €100.00 | 7.20 | €720.00 | €200.00 |
| €25.51 | 3.05 | €77.81 | €51.02 |
| €20.00 | 2.95 | €59.00 | €40.00 |

The bet slip and the API response (`"payout": 17.5`) are correct. Only the receipt is wrong.

Business impact: the receipt is the customer's only record of the bet. Customers are told they
will win more or less than the real payout, which leads to disputes and complaints when the bet is
settled.

Evidence: `TC-01-04-pre-place-bet.png` (slip €17.50) vs `TC-01-06-bet-successful.png`
(receipt €20.00); `TC-02-02.png`; `TC-02-03-nobalanceblock.png`; `TC-02-intent-step5.png`;
`TC-03-04-place-bet.txt` (API payout correct).

## BUG-05: Receipt swaps the home and away teams

- Severity: High
- Spec: §2.4 "Match details"; glossary *Match Ordering*: "This convention carries through to the bet receipt"

Reproduction steps:

1. Select odds on Bayern Munich (home) vs Leverkusen (away). The slip reads "Bayern Munich vs Leverkusen".
2. Enter €10.00 and place the bet.

Expected: the receipt reads "Bayern Munich vs Leverkusen".

Actual: the receipt reads "Leverkusen vs Bayern Munich". The same thing happened on every
receipt: "Stuttgart vs Bayern Munich" and "Porto vs Benfica" (home is Bayern and Benfica).

Business impact: because the receipt shows no selection either (BUG-06), a customer who backed the
home side reads a receipt that suggests the other team. That means wrong-bet disputes and a loss of
trust.

Evidence: `TC-01-03-bet-slip.png` (slip order) vs `TC-01-06-bet-successful.png` (receipt
order); `TC-02-02.png`; `TC-02-intent-step5.png`.

## BUG-06: Receipt does not show the selection

- Severity: High
- Spec: §2.4 "Receipt must show: … Selection …"

Reproduction steps:

1. Select `1` on any upcoming match, enter €10.00 and place the bet.
2. Read the receipt.

Expected: the receipt shows the selection (e.g. "Match Winner: Home"), as the slip did.

Actual: the receipt shows Bet ID, match, stake, odds, payout and time, but no selection.

Business impact: the customer can't confirm which outcome they backed. Combined with BUG-05 the
receipt can actively point at the wrong team.

Evidence: `TC-01-06-bet-successful.png`; `TC-01-08-second-bet.png`.

## BUG-07: Past matches are listed as upcoming and accept bets

- Severity: High
- Spec: §1 and §3 "Upcoming/Pre-match events only"; §2.1 "Display upcoming football matches"; DA-C6

Reproduction steps:

1. Open the app (2026-11-12). Under "Upcoming Football Matches", cards marked PAST are listed with active odds buttons, e.g. Real Madrid vs Sevilla (05 Nov).
2. `POST /api/place-bet` `{"matchId": "premier-league-manutd-chelsea", "selection": "HOME", "stake": 1}`. `GET /api/matches` gives this match a `kickoffDate` of `2026-02-27`.

Expected: only upcoming matches are listed, and a bet on a past match is rejected (422).

Actual: the list shows past matches as bettable, and the API returns 200 "Bet placed successfully" for a match dated 2026-02-27.

Business impact: customers can bet on games whose result is already known, which is a guaranteed
loss for the operator and an obvious route for abuse.

Evidence: `TC-01-03-bet-slip.png` (PAST cards with odds); `TC-03-03-matches.txt` (catalog
dates); `BUG-past-match-01-place-bet.txt` (bet accepted).

## BUG-08: Place-bet response reports the currency as USD

- Severity: Medium
- Spec: §3 "Currency: EUR (€)"; §5.3 `POST /api/place-bet` 200 response `currency: "EUR"`

Reproduction steps:

1. `POST /api/place-bet` with any valid bet.

Expected: `"currency": "EUR"`.

Actual: `"currency": "USD"`. `GET /api/balance` and `POST /api/reset-balance` correctly return `"EUR"`.

Business impact: any client that displays or reconciles amounts from this response would label
euros as dollars, which means wrong statements and wrong accounting.

Evidence: `TC-03-04-place-bet.txt` (`USD`) vs `TC-03-05-balance.txt` (`EUR`).

## BUG-09: Place-bet response has no bet ID, timestamp or match details

- Severity: Medium
- Spec: §2.4 receipt requires Bet ID, match details and placement timestamp; §5.3 response has none of them (DA-C4)

Reproduction steps:

1. `POST /api/place-bet` with any valid bet.
2. Compare the response fields with the receipt fields in §2.4.

Expected: the response carries the server-side Bet ID, placement timestamp and match details shown on the receipt.

Actual: the response has `message, matchId, selection, stake, odds, payout, balance, currency` only. The receipt's Bet ID (e.g. `#B-94384`) and time therefore come from the client and can't be traced to the server.

Business impact: support and customers can't use the receipt's Bet ID to find the bet on the
server, and the placement time has no authoritative source.

Evidence: `TC-03-04-place-bet.txt`; `TC-01-06-bet-successful.png`.

## BUG-10: Bet slip hides the available balance once a selection is made

- Severity: Medium
- Spec: §2.2 "Shows entered stake, available balance, and computed potential payout"

Reproduction steps:

1. Open the app. The empty slip shows "Balance: €120.00".
2. Select any odds.

Expected: the slip keeps showing the available balance next to the stake and payout.

Actual: the balance disappears from the slip as soon as a selection is made. It only shows while
the slip is empty.

Business impact: the customer has to look away to the header to see what they can stake, and the
header is out of date anyway (BUG-02).

Evidence: `x14.png` (empty slip with balance) vs `TC-01-04-pre-place-bet.png` (slip with
selection, no balance).

## BUG-11: Match list shows no kickoff time

- Severity: Medium
- Spec: §2.1 "Each match shows… kickoff date/time label"; DA-C2

Reproduction steps:

1. Open the app and look at any match card.

Expected: a kickoff date and time, e.g. "Fri, 13 Nov, 20:30".

Actual: only a day, e.g. "Tomorrow" or "czw., 05 lis". No time anywhere. The API's
`kickoffDate` is date-only too (`YYYY-MM-DD`), so the time isn't available to the UI at all.

Business impact: customers can't tell when a match starts, and so whether they can still bet on
it pre-match.

Evidence: `TC-01-03-bet-slip.png`; `TC-03-03-matches.txt` (date-only `kickoffDate`).
