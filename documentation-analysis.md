# Documentation Analysis: Single Bet Placement

## Purpose

This review of the *Single Bet Placement* feature specification and the assignment's domain glossary
comes before the test plan. It records four things:

1. Contradictions: two statements that cannot both be true. Each one has an explicit decision, so it
   can serve as a test oracle.
2. Gaps and ambiguities: behavior the spec does not define. Each one has a decided test basis.
3. Editorial issues: wording problems that don't change behavior.
4. Documentation issues raised: everything above that needs clarifying with the product owner.

These decisions are the test basis for the test plan, the execution and the automation. A defect is
reported against the spec where the spec is clear, and against these decisions where it is not.

| | Count |
|---|---|
| Contradictions | 6 |
| Gaps and ambiguities | 21 |
| Editorial issues | 5 |
| Documentation issues raised | 27 |

### Sources

| Ref | Document |
|---|---|
| `SPEC §x` | Single Bet Placement Feature Specification (no version or date given) |
| `GLOSSARY` | Assignment brief, *Domain Context*, *Betting Concepts* |

## 1. Contradictions

### DA-C1: Minimum stake is €1.00 in two places and €1.01 in a third

| Source | Statement |
|---|---|
| SPEC §3 Business Rules | Stake min (per bet): €1.00 |
| SPEC §4.1 Stake Validation | Minimum €1.01 (positive values) |
| SPEC §4.4 UI copy | `Minimum stake is €1.00` |

Why it matters: this decides the most important boundary test, whether a €1.00 stake is accepted or
rejected. If the real minimum were €1.01, the UI message would show the wrong value.

Decision: the minimum is €1.00, inclusive. Two of the three sources say so, including the message users
see. €1.00 must be accepted, and €0.99 must be rejected with `Minimum stake is €1.00`. The €1.01 in §4.1
is treated as a documentation error.

### DA-C2: Kickoff "date/time" vs a date-only API field

| Source | Statement |
|---|---|
| SPEC §2.1 | Each match shows a "kickoff date/time label" |
| GLOSSARY | Each match has a "kickoff date/time" |
| SPEC §5.3 `GET /api/matches` | `kickoffDate: string (YYYY-MM-DD)`, with no time part |

Why it matters: the UI can't show a kickoff time that the API never returns. Unless the time comes from
somewhere undocumented, a test that expects one will always fail.

Decision: the kickoff time is required. The UI must show a kickoff date and time, and the date must match
the API's `kickoffDate`. A match shown without a kickoff time is a defect.

### DA-C3: "One selection at a time" vs controls for removing several

| Source | Statement |
|---|---|
| SPEC §2.2 | Bet slip "shows one active selection at a time" |
| SPEC §2.1 | Selecting new odds replaces the previous selection |
| GLOSSARY | "Only one bet can be active at a time" |
| SPEC §2.2 | Bet slip includes `Remove All` and a per-selection remove (`x`) |

Why it matters: with only one selection, `Remove All` and `x` either do the same thing or differ in a way
the spec never defines. The spec also doesn't say whether removing a selection clears the stake.

Decision: `Remove All` and `x` behave the same. Each clears both the selection and the stake, like `Close`
in the error modal (§2.5).

### DA-C4: The receipt needs data that the place-bet API doesn't return

| Source | Statement |
|---|---|
| SPEC §2.4 | Receipt shows Bet ID, match details, selection, stake, odds at placement, payout, placement timestamp |
| SPEC §5.3 `POST /api/place-bet` 200 | `message, matchId, selection, stake, odds, payout, balance, currency`: no bet ID, no timestamp, no team names |

Why it matters: the Bet ID and timestamp must come from the client or from an undocumented field. They
can't be compared with a server value, and nothing says whether a Bet ID can be traced on the server.

Decision: on the receipt, check that the Bet ID and timestamp are present, and that match, selection,
stake, odds and payout match the bet slip and the API response (format rules in DA-G19). The missing bet
ID, timestamp and match details in the place-bet response are reported as an API contract defect.

### DA-C5: 400 or 422 for a mistyped field

| Source | Statement |
|---|---|
| SPEC §4.1 | Stake "Must be numeric" is listed as a stake validation rule |
| SPEC §4.3 | "Request body must be valid JSON object": reject malformed or non-object payloads |
| SPEC §5.3 | `400` malformed payload; `422` semantic validation failures (selection/stake/match) |

Why it matters: `{"stake": "abc"}` is valid JSON, so it fits "semantic stake failure" (422). A field with
the wrong type is also commonly treated as malformed (400). API negative tests need one expected status
per case.

Decision: `400` only when the body isn't valid JSON or isn't a JSON object. Every field-level problem
returns `422`: missing field, wrong type, `null`, out of range, unknown match.

### DA-C6: "Upcoming matches only" can't be checked by date alone, and nothing enforces it

| Source | Statement |
|---|---|
| SPEC §1, §3 | Upcoming / pre-match events only; no live betting |
| SPEC §5.3 | Kickoff is a date only (`YYYY-MM-DD`) |
| SPEC §4.2 | Match validation only checks "non-empty" and "exists in catalog". No rule rejects started or past matches. |

Why it matters: the data can't tell whether a match dated today has already kicked off, and the API is not
required to reject a bet on a past match even though the business rule bans it.

Decision: every match in `GET /api/matches` has a `kickoffDate` of today or later, and today counts as
upcoming. A past-dated match in the catalog is a defect. The API must also reject a bet on a past match
with `422`; accepting it is a defect.

## 2. Gaps and ambiguities

"Yes" in the Doc issue column means the gap is also listed in [§4](#4-documentation-issues-raised).

| ID | Area | Gap | Test basis (decision) | Doc issue |
|---|---|---|---|---|
| DA-G1 | Payout | No rounding rule for `stake × odds` (e.g. €33.33 × 2.45 = 81.6585) | No rounding mode is assumed. Bet slip preview, receipt and API `payout` must agree, and each must be within €0.01 of the exact product. | Yes |
| DA-G2 | Boundaries | Not stated whether the min, max and balance limits are inclusive | All inclusive. €1.00 accepted, €0.99 rejected. €100.00 accepted, €100.01 rejected. A stake equal to the balance accepted, balance + €0.01 rejected. | |
| DA-G3 | Messages | No precedence when several rules fail (e.g. €130 with a €125.50 balance breaks both max and balance) | No precedence assumed and no specific message asserted. Placement must be blocked. | Yes |
| DA-G4 | Messages | No message text for required, non-numeric or precision errors (§4.4 covers min, max and balance only) | Placement is blocked and some visible feedback appears. The text is not asserted. | Yes |
| DA-G5 | Input format | "Single decimal separator" doesn't name the character | Both `.` and `,` must work: `10.50` and `10,50` both mean €10.50. Rejecting `,` is a defect. | Yes |
| DA-G6 | Rebet | §2.5 says Rebet "retries placement" but not with which data | The retry uses the same match, selection and stake. On success the balance is deducted exactly once. | Yes |
| DA-G7 | Idempotency | The API has no idempotency key. If a request times out after the server has committed it, a retry can place a duplicate bet. | Observe only. Recorded as a risk and a recommendation. | Yes |
| DA-G8 | Double submit | §2.3 defines a loading state but doesn't say whether `Place Bet` is disabled. §5.3 defines `409` for a concurrent bet. | `Place Bet` can't fire again while `Placing...` is shown, so exactly one bet and one deduction result. Concurrent API calls for the same user return `409`. | Yes |
| DA-G9 | Auth | "Missing/invalid `x-user-id`" doesn't define invalid | Missing, empty or whitespace-only gives `401`. Any other non-empty string is a valid user. | Yes |
| DA-G10 | Errors | No error response body schema | Observe only. API tests assert status codes, not bodies. | Yes |
| DA-G11 | Extra fields | "Extra fields may be ignored" | Client-sent `odds`, `payout` or `balance` must have no effect, and the server price is used. Any effect is a security defect. | Yes |
| DA-G12 | Odds data | §3 limits odds to 1.01 to 1000.00, but no rule enforces it and the client never sends odds | Every odds value in `GET /api/matches` is between 1.01 and 1000.00. A value outside that range is a data defect. | Yes |
| DA-G13 | Odds filter | Doesn't say which of the three odds the min/max applies to. "Invalid range" is undefined, and there is no feedback text. | A match is shown if any of its odds is in `[min, max]`. min > max, non-numeric or negative input is rejected with visible feedback. | Yes |
| DA-G14 | Date filter | No behavior for a start date after the end date, and no time zone | A reversed range is rejected with visible feedback. Dates are compared as calendar dates. | Yes |
| DA-G15 | Filters and slip | Not defined what happens to the active selection when its match is filtered out | Observe only. | Yes |
| DA-G16 | Odds session | "Static for session" doesn't define session | Odds stay the same across `GET /api/matches` calls within one test run. | Yes |
| DA-G17 | Balance | Reset-balance resets to an "initial configured value", and the value appears only in the glossary (€125.50) | The initial and reset balance is €125.50 per `x-user-id`. The header and bet slip balance always agree. | Yes |
| DA-G18 | Float maths | API amounts are JSON `number`s, so floating-point drift is possible (e.g. 125.50 − 10.10 giving `115.39999…`). Input has the same problem: a stake of `10.555` may reach the server as `10.55499…`, so an API precision check can pass or fail for reasons unrelated to validation (test plan B-03). | Amounts are compared at 2 dp with a €0.01 tolerance. Linked to DA-G1. Results of API precision checks are reported with this caveat. | Yes |
| DA-G19 | Receipt fields | No format for Bet ID or timestamp, and no time zone. Observed on 2026-11-12: the receipt shows local time cut to the minute with a relative day ("TODAY, 05:41 PM"), and nothing else carries the time. Measured against the click time, the actual delay is 0 minutes (0 s, within display precision). Proposal: the spec should require a precise, time-zoned placement timestamp, ideally returned by the API. | Bet ID is non-empty and unique per bet. The timestamp is recorded in the report with its measured delay, not asserted. | Yes |
| DA-G20 | Slip behavior | Not defined: whether the stake survives a selection change, or what clicking the already-selected odds does | Observe only. | Yes |
| DA-G21 | UI auth | Behavior when `?user-id=` is missing from the UI URL is unspecified | Observe only. | Yes |

## 3. Editorial issues

| ID | Location | Issue |
|---|---|---|
| DA-E1 | SPEC §2.1 | The "new selection replaces previous" requirement appears three times in slightly different words. |
| DA-E2 | SPEC §4.1 | "Minimum €1.01 (positive values)": the part in brackets is unclear. Positive values above what? |
| DA-E3 | GLOSSARY vs SPEC §2.4 | The glossary's Bet Receipt list leaves out Selection, which §2.4 requires. |
| DA-E4 | SPEC §2.3 vs §2.5 | "Retry option" in §2.3 and the `Rebet` button in §2.5 are the same thing under two names. |
| DA-E5 | SPEC (whole) | No version, date or owner, so findings can't be traced to a document revision. |

## 4. Documentation issues raised

Questions for the product owner. They feed the spec clarifications in the Part C recommendations.

### From contradictions

| # | Ref | Question |
|---|---|---|
| 1 | DA-C1 | Is the minimum stake €1.00 or €1.01? Please fix §4.1, or §3 and §4.4. |
| 2 | DA-C2 | Where does the kickoff time come from? The API exposes a date only. |
| 3 | DA-C3 | Why does a single-selection slip have both `Remove All` and `x`? Does removing a selection clear the stake? |
| 4 | DA-C4 | Should `POST /api/place-bet` return a server-side bet ID, timestamp and match details? |
| 5 | DA-C5 | Please map each error case to a status code. Is a wrong type or missing field a 400 or a 422? |
| 6 | DA-C6 | Add a validation rule that rejects bets on started or past matches, and give kickoff a time. |

### From gaps

| # | Ref | Question |
|---|---|---|
| 7 | DA-G1, G18 | What are the payout rounding mode and the monetary precision? Should the API carry money as exact decimals (e.g. decimal strings or integer cents) instead of JSON floats? |
| 8 | DA-G3 | Which message wins when several stake rules fail at once? |
| 9 | DA-G4 | What is the message text for required, non-numeric and precision errors? |
| 10 | DA-G5 | Which decimal separators does the stake input accept? |
| 11 | DA-G6, G7 | What exactly does Rebet resend? Is placement idempotent, so a retry can't charge twice? |
| 12 | DA-G8 | Is `Place Bet` disabled while `Placing...` is shown? |
| 13 | DA-G9 | What counts as an invalid `x-user-id` (format, length, character set)? |
| 14 | DA-G10 | What is the error response body schema? |
| 15 | DA-G11 | "May be ignored" is too weak for price fields. Please confirm that client-sent odds, payout and balance are always ignored. |
| 16 | DA-G12 | Which layer enforces the 1.01 to 1000.00 odds range? |
| 17 | DA-G13 | Which odds does the odds filter apply to? What is an invalid range, and what feedback is shown? |
| 18 | DA-G14 | How should a reversed date range behave, and in which time zone? |
| 19 | DA-G15 | What happens to the active selection when its match is filtered out? |
| 20 | DA-G16 | What does "session" mean for static odds? |
| 21 | DA-G17 | Put the initial balance (€125.50) in the spec, not only in the glossary. |
| 22 | DA-G19 | What are the Bet ID and timestamp formats, and the timestamp's time zone? |
| 23 | DA-G20 | Is the stake kept when the selection changes? What does clicking the already-selected odds do? |
| 24 | DA-G21 | What should the UI do without `?user-id=`? |

### Editorial

| # | Ref | Question |
|---|---|---|
| 25 | DA-E1, E4 | Remove the repeated requirement in §2.1, and use one name for retry (`Rebet`). |
| 26 | DA-E2, E3 | Clarify "(positive values)" in §4.1, and align the glossary receipt list with §2.4. |
| 27 | DA-E5 | Add a version, date and owner to the spec. |
