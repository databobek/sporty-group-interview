## ADDED Requirements

### Requirement: Decided test basis

All test scenarios, bug reports and automated tests SHALL use the decisions in `documentation-analysis.md` as
their oracle wherever the feature spec is contradictory or silent. A defect SHALL cite either the spec section
or the DA-ID it violates.

#### Scenario: Behavior is undefined by the spec

- **WHEN** a test needs an expected result that the spec does not define
- **THEN** the expected result comes from the matching DA-ID decision
- **AND** if no decision exists, one is made and recorded before the test is written

### Requirement: Minimum stake (DA-C1)

The minimum stake SHALL be €1.00, inclusive, on both UI and API.

#### Scenario: Stake at the minimum boundary

- **WHEN** a bet is placed with a stake of €1.00
- **THEN** placement is allowed

#### Scenario: Stake below the minimum

- **WHEN** a stake of €0.99 is entered
- **THEN** placement is blocked or rejected, and the UI shows `Minimum stake is €1.00`

### Requirement: Kickoff display (DA-C2)

Each match in the UI SHALL show a kickoff date and time, and the date SHALL equal the API's `kickoffDate`.

#### Scenario: Kickoff time missing

- **WHEN** a match is shown with a date but no time
- **THEN** it is reported as a defect

### Requirement: Clearing the bet slip (DA-C3)

`Remove All` and the per-selection `x` SHALL each clear both the active selection and the entered stake.

#### Scenario: Remove a selection with a stake entered

- **WHEN** a selection with a stake is removed with either control
- **THEN** the bet slip has no selection and no stake

### Requirement: Receipt and API contract (DA-C4)

The receipt SHALL show a Bet ID and timestamp, and its match, selection, stake, odds and payout SHALL equal the
bet slip and the API response. The missing bet ID, timestamp and match details in the `POST /api/place-bet`
response SHALL be reported as an API contract defect.

#### Scenario: Receipt consistency

- **WHEN** a bet is placed successfully
- **THEN** the receipt values match the pre-placement bet slip and the API response

### Requirement: API error classes (DA-C5)

The API SHALL return `400` only for a body that isn't valid JSON or isn't an object, and `422` for every
field-level problem (missing, wrong type, null, out of range, unknown match).

#### Scenario: Non-numeric stake in valid JSON

- **WHEN** `POST /api/place-bet` is called with `{"stake": "abc", ...}`
- **THEN** the response status is `422`

### Requirement: Upcoming matches only (DA-C6)

Every match in `GET /api/matches` SHALL have `kickoffDate` on or after today. The API SHALL reject a bet on a
past match with `422`.

#### Scenario: Bet on a past match

- **WHEN** a bet is placed via the API on a match dated before today
- **THEN** the response status is `422`

### Requirement: Documentation issues are flagged, not assumed away

Where the spec is silent, the gap SHALL be recorded as a documentation issue. Assertions SHALL be no stricter
than the decision (e.g. consistency or a tolerance rather than an invented rule).

#### Scenario: Payout rounding (DA-G1, DA-G18)

- **WHEN** a payout is checked
- **THEN** the bet slip, receipt and API values agree and are within €0.01 of `stake × odds`
- **AND** no specific rounding mode is asserted
