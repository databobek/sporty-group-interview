# Single Bet Placement: QA Take-Home

Test analysis, a prioritized test plan and a small automation framework for the
*Single Bet Placement* feature of a simulated sports betting app.

| Deliverable | Where |
|---|---|
| Spec review: contradictions, gaps and the assumptions tests rely on | [documentation-analysis.md](documentation-analysis.md) |
| Test plan: six prioritized scenarios (Part A.1) | [test-plan.md](test-plan.md) |
| Automation framework and two tests (Part B) | `src/betting_qa/`, `tests/` (this README) |
| Decision log for every step | [openspec/changes/](openspec/changes/) |

## Automated tests

| Test | Layer | Why it was chosen |
|---|---|---|
| TC-01 `test_successful_single_bet_placement` | UI | The journey that earns money. One run checks that the bet slip, receipt, header and API agree on every amount. |
| TC-03 `test_client_supplied_price_fields_are_ignored` | API | A fraud risk only the server can prevent: client-sent odds, payout or balance must be ignored. |

Both tests use soft checks: they report every failed check in one go, instead of stopping at the
first. TC-01 currently fails on real defects in the application. That is expected: the tests follow
the spec, and the app deviates from it.

## Prerequisites

- Python 3.12
- Google Chrome (latest). Selenium Manager downloads the matching ChromeDriver automatically.
- [Poetry](https://python-poetry.org/) 2.x, e.g. `pipx install poetry`
- Optional, for viewing reports locally: Java 11+ and the [Allure CLI](https://allurereport.org/docs/install/)

## Setup

```bash
poetry install
poetry run pre-commit install
cp .env.example .env        # Windows: copy .env.example .env
```

Then set your user-id in `.env`:

```
CANDIDATE_ID=<your-user-id>
```

`CANDIDATE_ID` is the `user-id` from the assignment
(`https://qae-assignment-tau.vercel.app/?user-id=<your-user-id>`). The UI tests open that URL,
and the API tests send it as the `x-user-id` header. Without it, the test session stops before
running anything.

## Running

```bash
poetry run pytest            # everything
poetry run pytest -m api     # API tests only (no browser)
poetry run pytest -m ui      # UI tests only
HEADLESS=true poetry run pytest   # without a browser window
```

Tests run one at a time, because they share one user's balance. Each test resets the balance
first.

## Reports

Every run writes Allure results to `allure-results/`. They include each API request and response,
and for a failed UI test a screenshot, the page source and the browser console log. The
`CANDIDATE_ID` is replaced by `***` in all of them, because the report is published.

- In CI, each push to `main` publishes the report to this repository's GitHub Pages site.
- Locally, if the Allure CLI is installed: `allure serve allure-results`

## Configuration

Set in `.env` or as environment variables (see [.env.example](.env.example)):

| Variable | Default | Meaning |
|---|---|---|
| `CANDIDATE_ID` | (required) | Your user-id for the app |
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` | Application URL |
| `HEADLESS` | `false` | `true` runs Chrome without a window. CI uses `true`. |
| `UI_TIMEOUT` | `10` | Seconds to wait for UI elements |
| `API_TIMEOUT` | `10` | Seconds per HTTP request |

## Project structure

```
src/betting_qa/
  config.py          settings from env/.env
  rules.py           the spec's numbers (stake limits, initial balance), with their sources
  money.py           euro parsing and comparison (Decimal, ±€0.01)
  checks.py          SoftChecks: collect failed checks, fail once at the end
  reporting.py       Allure attachments, with the user-id masked
  api/               typed API client and payload models
  ui/                Chrome driver, BasePage (all waits) and page objects:
                     HomePage → MatchList, BetSlip, ReceiptModal
tests/
  conftest.py        shared fixtures: settings, api, fresh_balance, catalog, upcoming_match, checks
  api/               TC-03
  ui/                browser fixtures, failure evidence, TC-01
```

Tests contain only business steps and checks. Selectors and waits live in the page objects, HTTP
calls in the API client, and the spec's values in `rules.py`.

## CI

[.github/workflows/tests.yml](.github/workflows/tests.yml) runs on pushes to `main`, on pull requests,
and manually:

1. The lint job runs ruff (lint and format check) and mypy.
2. The test job runs both tests headless, then builds the Allure report and publishes it to GitHub Pages.
   The report is published even when tests fail, and the job is still marked as failed.

To run it, add the repository secret `CANDIDATE_ID` and enable GitHub Pages from the `gh-pages`
branch.

## Tooling choices

| Tool | Why |
|---|---|
| Poetry | One file for dependencies and tool config, with a lock file for repeatable installs. |
| Allure | Readable reports with steps and attached evidence (requests, screenshots). |
| ruff | Fast lint and format in one tool. |
| mypy (strict on `src/`) | Catches interface mistakes between page objects, client and tests. |
| pre-commit | Runs ruff and mypy before every commit, so CI rarely fails on style. |

## Scope note

Framework unit tests (for money parsing, config, the API client and so on) would be required in a
real project. They are out of scope for this assignment. The framework is verified by linting,
strict type checks and the two tests' runs against the live application.
