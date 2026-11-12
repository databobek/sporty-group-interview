# Design: Automation framework (Part B)

## Intent

Build a small, well-structured pytest, Selenium and requests framework that automates two scenarios from
`test-plan.md`: TC-01 (UI, successful single bet placement) and TC-03 (API, server-side price integrity).
The brief says the framework is evaluated more than the tests, so the structure must visibly hold all six
test-plan scenarios even though only two are implemented.

## Goals

- A reviewer can clone the repo, run one setup command and one test command, and get a readable Allure report.
- Tests read as business steps. Selectors, waits, HTTP details and money parsing live in the framework, not in the tests.
- All six scenarios (TC-01 to TC-06) fit the structure without restructuring it.
- Every automated check traces to a SPEC section or a DA-ID, as in the test plan.

## Non-goals

- Implementing TC-02, TC-04, TC-05 or TC-06 (designed for, not built).
- Cross-browser runs, mobile, parallel execution, and the error modal (#7).

## Anti-goals (a failure even if the tests run)

- A test that passes because it was adapted to app behavior that contradicts the spec. The spec is the oracle.
- `time.sleep`, implicit waits, or retries that hide flakiness.
- Selectors or raw HTTP calls inside test functions.

## Constraints

| Constraint | Source |
|---|---|
| Python 3, Selenium WebDriver with pytest, `requests`, latest desktop Chrome | Assignment brief (required stack) |
| Additional tooling documented in the README | Assignment brief |
| The spec is the only documentation, and differences in the app are defects | Decision in the test-plan change |
| Selectors aren't in the spec, so they are read from the live DOM at build time, read-only | Decision F6 |
| Java and Node are not installed locally, so the Allure CLI is optional locally | Environment |

## Approaches considered

| | Approach | Trade-off | Outcome |
|---|---|---|---|
| A | Page objects, a typed API client and pytest fixtures | Standard and familiar to reviewers. Slightly more code than two tests need. | Chosen |
| B | Screenplay pattern (actors, tasks, questions) | Scales for large suites, but is heavy for two tests and reads as over-engineering | Rejected |
| C | Plain helper functions, no classes | Least code, but shows little framework structure, which the brief evaluates | Rejected |

## Decisions (2026-11-12)

| # | Topic | Decision |
|---|---|---|
| F1 | Reach | Design for all six scenarios, implement two |
| F2 | Automated tests | TC-01 (UI) and TC-03 (API) |
| F3 | Packaging | Poetry |
| F4 | Reports | Allure. CI builds the report and publishes it to GitHub Pages. The Allure CLI is optional locally. |
| F5 | Architecture | Approach A |
| F6 | Selectors | Inspect the live DOM at build time, read-only, with a throwaway user-id |
| F7 | Config | Environment variables with defaults, documented in `.env.example` |
| F8 | Code quality | ruff (lint and format), mypy and pre-commit hooks, also run in CI |
| F9 | Defaults | Balance reset per test; Chrome via Selenium Manager; headed locally, headless in CI, 1920×1080; explicit waits only inside page objects; `Decimal` for all money, compared at 2 dp with a €0.01 tolerance; on failure, attach a screenshot, the page source and the browser console log; attach every API exchange; CI on push to `main`, on pull requests and on manual trigger; Python 3.12; no retries; no parallel runs. (A new user-id per test was planned here and replaced by F10.) |
| F10 | User identity | `CANDIDATE_ID` (env) is the app's `user-id`. It goes in the UI URL `/?user-id=<CANDIDATE_ID>`, as the brief specifies, and in the `x-user-id` header of every API call, so UI and API share one balance. It is required: if it is unset, the session stops at startup. |
| F11 | Unit tests | None. Framework unit tests are required in a real implementation but are outside this task's scope, and the README says so. |
| F12 | Assertion style | Soft checks: each test collects its failed checks and fails once at the end, listing all of them. Errors that stop the journey (a missing element, an `ApiError`) still fail at once. |
| F13 | Receipt timestamp tolerance | Measured, not assumed. The first TC-01 run records the actual delay, and the tolerance is set from it. DA-G19 is updated with the measured delay as a documentation issue. |
| F14 | Virtualenv | In-project `.venv/` (`poetry.toml`) |
| F15 | `CANDIDATE_ID` in the public report | Hidden everywhere. `reporting.register_secret()` records it, and every Allure attachment (API exchanges, page source, console log) has it replaced by `***`. It is not a report parameter and does not appear in step titles. Screenshots show only the viewport, not the address bar. |

## Project layout

```
.
├── pyproject.toml              Poetry project, dependencies, pytest/ruff/mypy config
├── poetry.lock
├── .pre-commit-config.yaml
├── .env.example                documents CANDIDATE_ID, BASE_URL, HEADLESS, UI_TIMEOUT, API_TIMEOUT
├── README.md                   setup, run, report, config, structure, tooling choices
├── .github/workflows/tests.yml lint → test → Allure report → GitHub Pages
├── src/betting_qa/
│   ├── __init__.py
│   ├── config.py               Settings loaded from env
│   ├── rules.py                business constants from the spec (stake limits, initial balance)
│   ├── money.py                Decimal parsing and comparison helpers
│   ├── checks.py               SoftChecks: collect failed checks, fail once at the end (F12)
│   ├── reporting.py            Allure attachment helpers
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py           BettingApiClient
│   │   └── models.py           Selection, Odds, Match, Balance, BetResponse
│   └── ui/
│       ├── __init__.py
│       ├── driver.py           create_driver()
│       ├── base.py             BasePage: wait-based element helpers
│       ├── home_page.py        HomePage: the app shell (header + components)
│       └── components/
│           ├── __init__.py
│           ├── match_list.py   MatchList
│           ├── bet_slip.py     BetSlip
│           └── receipt.py      ReceiptModal, Receipt
└── tests/
    ├── conftest.py             shared fixtures: settings, user_id, api, fresh_balance, catalog
    ├── api/
    │   └── test_price_integrity.py   TC-03
    └── ui/
        ├── conftest.py         driver, home fixtures and failure evidence
        └── test_place_bet.py         TC-01
```

The package is `betting_qa` with a `src/` layout, so tests import the installed package and not loose
files from the repository.

## Module definitions

The signatures are the contract; the bodies are left to the implementation.

### `config.py`

```python
@dataclass(frozen=True)
class Settings:
    candidate_id: str              # required; the app's user-id (F10)
    base_url: str = "https://qae-assignment-tau.vercel.app"
    headless: bool = False
    ui_timeout: float = 10.0       # seconds, explicit waits
    api_timeout: float = 10.0      # seconds, HTTP requests
    window_size: tuple[int, int] = (1920, 1080)

    @classmethod
    def from_env(cls) -> "Settings": ...
```

`from_env` loads an optional `.env` (python-dotenv), then reads `CANDIDATE_ID`, `BASE_URL`, `HEADLESS`,
`UI_TIMEOUT` and `API_TIMEOUT`, falling back to the defaults above. `CANDIDATE_ID` has no default. If it
is missing or blank, `from_env` raises `ConfigError("Set CANDIDATE_ID in .env (see .env.example)")`, and
the session-scoped `settings` fixture turns that into `pytest.exit(...)`, so no test runs.

### `rules.py`

The spec's numbers in one place, each commented with its source.

```python
INITIAL_BALANCE = Decimal("125.50")   # GLOSSARY, DA-G17
MIN_STAKE = Decimal("1.00")           # SPEC §3, DA-C1
MAX_STAKE = Decimal("100.00")         # SPEC §3
MONEY_TOLERANCE = Decimal("0.01")     # DA-G1, DA-G18
CURRENCY = "EUR"
```

### `money.py`

```python
def parse_eur(text: str) -> Decimal: ...
    # "€115.50" / "115.50 €" / "115,50" → Decimal("115.50"); raises ValueError on anything else

def money_close(actual: Decimal, expected: Decimal, tolerance: Decimal = MONEY_TOLERANCE) -> bool: ...

def expected_payout(stake: Decimal, odds: Decimal) -> Decimal: ...
    # stake × odds, unrounded (DA-G1: no rounding mode assumed)
```

### `checks.py` (F12)

```python
class SoftChecks:
    def check(self, condition: bool, description: str) -> bool: ...          # record a failure if False
    def equal(self, actual: object, expected: object, what: str) -> bool: ...
    def money(self, actual: Decimal, expected: Decimal, what: str) -> bool: ...  # uses money_close
    @property
    def failures(self) -> list[str]: ...
    def assert_all(self) -> None: ...
        # if any failed: attach "Failed checks" to Allure and raise AssertionError("N check(s) failed:\n- ...")
```

Tests call `checks.assert_all()` explicitly as their last line, so a failure shows up as a test failure and
not as a fixture teardown error. The helper is written by hand, with no `pytest-check` dependency.

### `api/models.py`

Frozen dataclasses. Money fields are `Decimal`, and each class has a `from_json(data: Mapping[str, Any])`
classmethod.

```python
class Selection(StrEnum):
    HOME = "HOME"; DRAW = "DRAW"; AWAY = "AWAY"
    @property
    def ui_label(self) -> str: ...     # "1" / "X" / "2"  (GLOSSARY Odds)

@dataclass(frozen=True)
class Odds:
    home: Decimal; draw: Decimal; away: Decimal
    def for_selection(self, selection: Selection) -> Decimal: ...

@dataclass(frozen=True)
class Match:
    id: str; competition: str; kickoff_date: date
    home_team: str; away_team: str; odds: Odds

@dataclass(frozen=True)
class Balance:
    balance: Decimal; currency: str

@dataclass(frozen=True)
class BetResponse:
    message: str; match_id: str; selection: Selection
    stake: Decimal; odds: Decimal; payout: Decimal
    balance: Decimal; currency: str
```

### `api/client.py`

```python
class BettingApiClient:
    def __init__(self, base_url: str, user_id: str | None, timeout: float) -> None: ...
        # one requests.Session; sets x-user-id when user_id is not None;
        # registers a response hook that attaches every exchange to Allure

    # Typed calls: expect 200, raise ApiError otherwise, parse JSON with parse_float=Decimal
    def get_matches(self) -> list[Match]: ...
    def get_balance(self) -> Balance: ...
    def reset_balance(self) -> Balance: ...
    def place_bet(self, match_id: str, selection: Selection, stake: Decimal,
                  **extra_fields: object) -> BetResponse: ...

    # Raw call for negative tests (TC-02/04 422, TC-06 409): no status check, no parsing
    def place_bet_raw(self, payload: object, *, headers: Mapping[str, str] | None = None) -> requests.Response: ...

    def close(self) -> None: ...

class ApiError(Exception):
    status_code: int; body: str
```

Money is read from JSON with `parse_float=Decimal`, so the framework itself never introduces float drift.
`Decimal` is sent as a JSON number; precision on the wire is a known limitation (B-03).

TC-03 uses `place_bet(**extra_fields)` to send `odds`, `payout` and `balance` alongside a valid bet.

### `reporting.py`

```python
def attach_api_exchange(response: requests.Response) -> None: ...
    # request method, URL, headers, body + response status and body, as one Allure attachment
def attach_ui_evidence(driver: WebDriver, name: str) -> None: ...
    # screenshot (PNG), page source (HTML), browser console log (text)
```

### `ui/driver.py`

```python
def create_driver(settings: Settings) -> WebDriver: ...
    # Chrome via Selenium Manager; --headless=new when settings.headless;
    # window size from settings; browser console logging enabled (goog:loggingPrefs)
```

### `ui/base.py`

All waiting happens here. Page objects never call `find_element` directly.

```python
Locator = tuple[str, str]

class BasePage:
    def __init__(self, driver: WebDriver, timeout: float) -> None: ...
    def _find(self, locator: Locator) -> WebElement: ...             # wait until visible
    def _find_all(self, locator: Locator) -> list[WebElement]: ...
    def _click(self, locator: Locator) -> None: ...                  # wait until clickable
    def _type(self, locator: Locator, text: str) -> None: ...        # clear, then type
    def _text(self, locator: Locator) -> str: ...
    def _is_visible(self, locator: Locator, timeout: float | None = None) -> bool: ...
    def _wait_until(self, condition: Callable[[WebDriver], object], message: str) -> None: ...
```

### `ui/home_page.py`

```python
class HomePage(BasePage):
    def open(self, base_url: str, user_id: str) -> "HomePage": ...   # /?user-id=<id>, wait for match list
    @property
    def header_balance(self) -> Decimal: ...
    @property
    def match_list(self) -> MatchList: ...
    @property
    def bet_slip(self) -> BetSlip: ...
    @property
    def receipt(self) -> ReceiptModal: ...
```

### `ui/components/match_list.py`

```python
class MatchList(BasePage):
    def select_odds(self, match: Match, selection: Selection) -> None: ...
        # finds the match row (by id if the DOM exposes it, else by team names), clicks 1 / X / 2
    def kickoff_label(self, match: Match) -> str: ...                 # TC-01 DA-C2 check
    def odds_shown(self, match: Match) -> Odds: ...                    # TC-05
```

### `ui/components/bet_slip.py`

```python
@dataclass(frozen=True)
class SlipSelection:
    home_team: str; away_team: str; selection_label: str; odds: Decimal

class BetSlip(BasePage):
    def current_selection(self) -> SlipSelection | None: ...          # None when empty
    def selection_count(self) -> int: ...                              # TC-05 "still one selection"
    def enter_stake(self, raw: str) -> None: ...                       # str, so "1,00" and "abc" can be typed (TC-04)
    @property
    def available_balance(self) -> Decimal: ...
    @property
    def potential_payout(self) -> Decimal: ...
    @property
    def validation_message(self) -> str | None: ...                    # TC-02, TC-04
    def place_bet(self) -> None: ...                                   # click, then wait for "Placing..." to resolve
    def double_click_place_bet(self) -> None: ...                      # TC-06
    def is_place_bet_enabled(self) -> bool: ...                        # TC-06
    def remove_all(self) -> None: ...
    def remove_selection(self) -> None: ...
    def is_empty(self) -> bool: ...
```

### `ui/components/receipt.py`

```python
@dataclass(frozen=True)
class Receipt:
    bet_id: str; home_team: str; away_team: str; selection_label: str
    stake: Decimal; odds: Decimal; payout: Decimal; timestamp_text: str

class ReceiptModal(BasePage):
    def wait_until_shown(self) -> "ReceiptModal": ...
    def read(self) -> Receipt: ...
    def close(self) -> None: ...                                       # waits until the modal is gone
    def is_shown(self) -> bool: ...
```

## Fixtures

| Fixture | Scope | Provides |
|---|---|---|
| `settings` | session | `Settings.from_env()`; exits the session if `CANDIDATE_ID` is unset |
| `user_id` | session | `settings.candidate_id` (F10); never shown in the report (F15) |
| `api` | function | `BettingApiClient` for `user_id`, closed on teardown |
| `fresh_balance` | function | Calls `reset_balance()`, asserts €125.50 (P3) and returns the `Balance`. All tests share one user, so this reset is what isolates them. |
| `catalog` | function | `api.get_matches()` (P4) |
| `checks` | function | A new `SoftChecks` (F12) |
| `driver` | function (`tests/ui`) | `create_driver(settings)`; attaches UI evidence when the test fails; always quits |
| `home` | function (`tests/ui`) | `HomePage` opened for `user_id` after `fresh_balance` |

Failure detection uses the standard `pytest_runtest_makereport` hookwrapper. It stores the call outcome on
the test item, so the `driver` teardown knows whether to attach evidence.

## The two tests

Both use `allure.title`, `epic("Single Bet Placement")`, `feature`, `severity(CRITICAL)`, `tag("TC-0x")`,
and `allure.step` blocks that follow the test-plan steps. Both have a docstring that explains why the test
was chosen for automation, as the brief requires.

| Test | File | Markers | Covers test-plan steps |
|---|---|---|---|
| `test_successful_single_bet_placement` | `tests/ui/test_place_bet.py` | `ui` | TC-01 steps 1 to 9, and the second-bet Bet ID uniqueness check |
| `test_client_supplied_price_fields_are_ignored` | `tests/api/test_price_integrity.py` | `api` | TC-03 steps 1 and 2 |

The markers are registered with `--strict-markers`, so `pytest -m api` and `pytest -m ui` select each layer.

## How the remaining scenarios fit (designed, not built)

| Scenario | Uses | Needs added |
|---|---|---|
| TC-02 Insufficient balance | `BetSlip.validation_message`, `HomePage.header_balance`, `api.place_bet_raw` (422) | Nothing |
| TC-04 Stake boundaries | `BetSlip.enter_stake(raw)`, `validation_message`, `api.place_bet_raw`; `pytest.mark.parametrize` over the case table | Nothing |
| TC-05 Outcome mapping | `MatchList.select_odds`, `odds_shown`, `BetSlip.current_selection`, `selection_count`, `ReceiptModal.read`, `api.place_bet` per `Selection` | Nothing |
| TC-06 Duplicate placement | `BetSlip.double_click_place_bet`, `is_place_bet_enabled`, `ReceiptModal.is_shown` | `api/concurrency.py` with `fire_concurrently(calls: Sequence[Callable[[], Response]]) -> list[Response]`, which uses a `threading.Barrier` to line the requests up. Step 5 (the control with two different users) needs a second user-id besides `CANDIDATE_ID` (open, see below). |

## Dependencies

Poetry resolves the versions at build time (latest stable) and pins them in `poetry.lock`.

| Group | Package | Why |
|---|---|---|
| main | `python = "^3.12"` | The local interpreter is 3.12.8 |
| main | `pytest` | Required stack |
| main | `selenium` | Required stack. Selenium Manager resolves ChromeDriver, so `webdriver-manager` isn't needed. |
| main | `requests` | Required stack |
| main | `allure-pytest` | Allure results |
| main | `python-dotenv` | Optional `.env` loading (F7) |
| dev | `ruff` | Lint and format (F8) |
| dev | `mypy`, `types-requests` | Type checks (F8) |
| dev | `pre-commit` | Git hooks (F8) |

## Tool configuration (in `pyproject.toml`)

- pytest: `testpaths = ["tests"]`; `addopts = "--alluredir=allure-results --clean-alluredir --strict-markers"`; markers `ui` and `api`.
- ruff: line length 100; rules `E, F, I, B, UP, PT, SIM`; formatter enabled.
- mypy: `strict = true` for `src/betting_qa`; tests are checked without `disallow_untyped_defs`.

## Pre-commit

The hooks are `ruff` (lint, `--fix`), `ruff-format`, `mypy` (a local hook running `poetry run mypy`, so it
uses the project's own environment), `end-of-file-fixer` and `trailing-whitespace`.

## CI (`.github/workflows/tests.yml`)

Triggers: push to `main`, pull requests, `workflow_dispatch`.

1. The lint job checks out the code, sets up Python 3.12, installs Poetry, runs `poetry install`, then
   runs `ruff check`, `ruff format --check` and `mypy`.
2. The test job (after lint) does the same setup, then runs `HEADLESS=true poetry run pytest`. Chrome is
   preinstalled on GitHub's Ubuntu runners. The job still records a failure when tests fail.
3. The report steps (`if: always()`) download the previous report history from `gh-pages`, generate the
   Allure report, publish it to GitHub Pages and upload `allure-results` as a build artifact.

## `.gitignore` additions

`.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `allure-results/`,
`allure-report/`, `.env`

## README outline

1. What this is: one paragraph, with links to the four deliverables
2. Prerequisites: Python 3.12, Chrome, Poetry; optionally Java and the Allure CLI for local reports
3. Setup: `poetry install`, `poetry run pre-commit install`
4. Running: all tests, `-m api`, `-m ui`, headless
5. Reports: local (`allure serve allure-results`) and the CI GitHub Pages link
6. Configuration: a table of environment variables, matching `.env.example`
7. Project structure: a short tree with one line per module
8. Tooling choices: Poetry, Allure, ruff, mypy and pre-commit, each with one sentence on why
9. Scope note: framework unit tests are required in a real implementation but are outside this task's scope (F11)

## Left open

| Item | When it's settled |
|---|---|
| Exact selectors, and how `MatchList` finds a match row | At build time, from the live DOM (F6) |
| Whether tests that fail on a known defect are marked `xfail` (with the bug ID) or left failing | After Part A.2 execution, once the defects are known |
| GitHub Pages enabled on the public repo | When the repo is pushed |
| `CANDIDATE_ID` in CI | Stored as a GitHub Actions secret (or variable) and passed to the test job as an environment variable, when the repo is pushed |
| A second user-id for TC-06 step 5 | When TC-06 is built (not in scope now) |

## Smaller calls

- The package name `betting_qa` and the `src/` layout.
- `rules.py` for the spec's constants, and `money.py` for parsing and comparison.
- `HomePage` as one shell page with components, because the spec describes a single screen with a header,
  a match list, a bet slip and modals.
- Typed client methods raise `ApiError` on any status other than 200, and `place_bet_raw` exists for
  negative tests.
- JSON is parsed with `parse_float=Decimal`.
- `pytest`, `selenium`, `requests` and `allure-pytest` sit in the main dependency group, because this is a
  test project and they are its runtime. The lint tools sit in `dev`.
- The CI workflow shape: separate lint and test jobs, with report steps that run even when tests fail.
