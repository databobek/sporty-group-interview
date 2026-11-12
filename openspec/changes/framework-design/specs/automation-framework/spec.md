## ADDED Requirements

### Requirement: Layered structure

Tests SHALL contain only business steps and assertions. Selectors and waits SHALL live in page objects,
HTTP calls in `BettingApiClient`, and money parsing in `money.py`.

#### Scenario: Reviewer reads a test

- **WHEN** a reviewer opens `tests/ui/test_place_bet.py` or `tests/api/test_price_integrity.py`
- **THEN** it contains no locators, no `find_element`, no `requests` calls and no sleeps

### Requirement: Candidate identity

All UI and API calls SHALL use `CANDIDATE_ID` from the environment as the app's user-id: in the UI URL
`/?user-id=<CANDIDATE_ID>` and as the `x-user-id` header. The test session SHALL stop at startup if it is unset.

#### Scenario: CANDIDATE_ID missing

- **WHEN** `poetry run pytest` starts without `CANDIDATE_ID` set
- **THEN** no test runs, and the output says to set `CANDIDATE_ID` in `.env`

### Requirement: Test isolation

Tests SHALL run one at a time, and each test SHALL reset the candidate's balance to €125.50 before it starts.

#### Scenario: Two tests run back to back

- **WHEN** a second test starts after the first one placed a bet
- **THEN** the second test sees a balance of €125.50

### Requirement: Money handling

The framework SHALL represent money as `Decimal` and compare it at 2 decimal places with a €0.01 tolerance.

#### Scenario: Payout comparison

- **WHEN** a payout is compared with `stake × odds`
- **THEN** the comparison uses `money_close` and no float arithmetic

### Requirement: Evidence in the report

Every API exchange SHALL be attached to the Allure report. A failing UI test SHALL attach a screenshot, the
page source and the browser console log.

#### Scenario: UI test fails

- **WHEN** a UI test fails
- **THEN** its Allure entry shows the screenshot, the page source and the console log

### Requirement: One-command setup and run

A reviewer SHALL be able to set up with `poetry install` and run with `poetry run pytest`, with the README
covering prerequisites, configuration and reports.

#### Scenario: Fresh clone

- **WHEN** a reviewer with Python 3.12, Chrome and Poetry follows the README
- **THEN** both tests run and produce Allure results

### Requirement: Continuous integration

CI SHALL run lint (ruff, mypy) and the tests on push to `main`, on pull requests and on manual trigger, and
SHALL publish the Allure report to GitHub Pages even when tests fail.

#### Scenario: A test fails on a real defect

- **WHEN** a test fails in CI
- **THEN** the workflow is marked failed, and the Allure report showing the failure is still published
