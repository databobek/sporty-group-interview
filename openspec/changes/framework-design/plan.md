# Automation Framework Implementation Plan

Goal: build the pytest, Selenium, requests and Allure framework from `design.md`, with TC-03 (API) and
TC-01 (UI) automated.

Architecture: page objects, a typed API client and pytest fixtures (approach A). Tests contain only
business steps and soft checks. Money is `Decimal` end to end. Every API exchange and every UI failure is
attached to Allure.

Tech stack: Python 3.12, Poetry, pytest, selenium (Selenium Manager), requests, allure-pytest,
python-dotenv; ruff, mypy, pre-commit; GitHub Actions.

Spec: `openspec/changes/framework-design/design.md`. Test oracle: `test-plan.md` (TC-01, TC-03) and
`documentation-analysis.md` (DA-IDs). Each task ends in a commit.

## Global constraints

- Python `^3.12`. Required stack: Selenium WebDriver with pytest, `requests`, latest desktop Chrome.
- `CANDIDATE_ID` is required. It is the `user-id` in the UI URL `/?user-id=<CANDIDATE_ID>` and the `x-user-id` header on every API call (F10).
- Money is `decimal.Decimal` everywhere, compared with `money_close` (±€0.01, DA-G1/G18).
- Explicit waits only, inside `BasePage`. No `time.sleep`, no implicit waits, no retries or reruns.
- No selectors, `find_element` or `requests` calls in test functions.
- Test checks go through `SoftChecks`, and every test ends with `checks.assert_all()` (F12).
- The spec is the oracle. A check is never weakened to fit what the app does.
- No framework unit tests (F11). Framework code is verified by ruff, mypy and the live runs of TC-01 and TC-03.
- ruff: line length 100, rules `E, F, I, B, UP, PT, SIM`. mypy `strict` on `src/betting_qa`. pytest `--strict-markers` with markers `ui` and `api`.
- Chrome via Selenium Manager. Headless when `HEADLESS` is true, 1920×1080.
- Tests run one at a time, because they share the candidate's balance.

## Edge cases to verify

With no unit tests, each case below gets a manual check in the task that owns it.

1. A blank or whitespace-only `CANDIDATE_ID` is treated as unset, and the session stops with the "Set CANDIDATE_ID" message. Task 3, step 2.
2. Money text in unusual formats (`€1,234.50`, `115,50 €`, a non-breaking space) is parsed correctly. Garbage raises `ValueError` and is never read as 0. Task 2, step 3.
3. An API error page that isn't JSON gives an `ApiError` with the status and body text, not a `JSONDecodeError`. Task 2, step 3.
4. JSON integers (`"draw": 3`) still become `Decimal`. Task 2, step 3.
5. If evidence capture fails (the browser is already gone), the problem is logged and the original failure is still reported. Task 4, step 5.

## Task 1: Project scaffold

Files:
- Create: `pyproject.toml`, `poetry.toml`, `.pre-commit-config.yaml`, `.env.example`, `src/betting_qa/__init__.py`, `tests/__init__.py`
- Modify: `.gitignore`

Produces: the installable package `betting_qa` (src layout), and the pytest markers `ui` and `api`.

- [ ] Step 1: Install Poetry with `python -m pip install --user pipx && python -m pipx install poetry`. Expected: `poetry --version` prints a version.
- [ ] Step 2: Write `pyproject.toml`:
  - `packages = [{ include = "betting_qa", from = "src" }]`.
  - Main dependencies: `python = "^3.12"`, `pytest`, `selenium`, `requests`, `allure-pytest`, `python-dotenv`.
  - `dev` group: `ruff`, `mypy`, `types-requests`, `pre-commit`.
  - pytest: `testpaths = ["tests"]`, `addopts = "--alluredir=allure-results --clean-alluredir --strict-markers"`, markers `ui` and `api`.
  - ruff and mypy as in the global constraints.

  Also write `poetry.toml` with `[virtualenvs] in-project = true`.
- [ ] Step 3: Run `poetry install`. Expected: `poetry.lock` is created and `.venv/` exists.
- [ ] Step 4: Write `.env.example` with `CANDIDATE_ID=`, `BASE_URL=https://qae-assignment-tau.vercel.app`, `HEADLESS=false`, `UI_TIMEOUT=10` and `API_TIMEOUT=10`, each with a one-line comment. Add `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `allure-results/`, `allure-report/` and `.env` to `.gitignore`.
- [ ] Step 5: Write `.pre-commit-config.yaml` with these hooks:
  - `pre-commit-hooks`: `end-of-file-fixer`, `trailing-whitespace`, `check-yaml`.
  - `ruff-pre-commit`: `ruff` with `--fix`, and `ruff-format`.
  - A local `mypy` hook that runs `poetry run mypy`, with `language: system` and `pass_filenames: false`.

  Then run `poetry run pre-commit install`.
- [ ] Step 6: Verify. `poetry run pytest` reports "no tests ran" (exit code 5), and `poetry run pre-commit run --all-files` passes.
- [ ] Step 7: Commit: `build: scaffold Poetry project, tooling and pre-commit`.

## Task 2: Core modules and API client

Files:
- Create:
  - `src/betting_qa/config.py`, `rules.py`, `money.py`, `checks.py`, `reporting.py`
  - `src/betting_qa/api/__init__.py`, `api/models.py`, `api/client.py`

Produces, exactly as in `design.md`:
- `Settings`, `Settings.from_env() -> Settings`, `ConfigError`
- the `rules.*` constants
- `parse_eur`, `money_close`, `expected_payout`
- `SoftChecks`
- `attach_api_exchange(response) -> None`
- `Selection`, `Odds`, `Match`, `Balance`, `BetResponse` (each with `from_json`)
- `BettingApiClient(base_url, user_id, timeout)` with `get_matches`, `get_balance`, `reset_balance`, `place_bet(match_id, selection, stake, **extra_fields)`, `place_bet_raw(payload, *, headers=None)` and `close`
- `ApiError(status_code, body)`

- [ ] Step 1: Implement `config.py`, `rules.py`, `money.py` and `checks.py`:
  - `from_env` calls `load_dotenv()` and reads `os.environ`. A blank or whitespace `CANDIDATE_ID` raises `ConfigError("Set CANDIDATE_ID in .env (see .env.example)")`.
  - `HEADLESS` accepts `true/1/yes` or `false/0/no/""`, in any case. Anything else, and any non-positive or non-numeric timeout, raises `ConfigError`.
  - `parse_eur` strips `€`, whitespace and non-breaking spaces. If both `,` and `.` appear, `,` is the thousands separator. If only `,` appears, it is the decimal separator. Anything else raises `ValueError`.
  - Each constant in `rules.py` has a comment citing its source.
  - `SoftChecks.assert_all` attaches a "Failed checks" text to Allure and raises an `AssertionError` that lists every failure on its own line.
- [ ] Step 2: Implement `models.py` (money goes through `Decimal(str(v))` when the value isn't already a `Decimal`), `client.py` (per `design.md`: `response.json(parse_float=Decimal)`; `ApiError` on any status other than 200, using `response.text`; the body serialized with `json.dumps(default=float)` for `Decimal`; a session response hook that calls `attach_api_exchange`) and `reporting.attach_api_exchange`.
- [ ] Step 3: Manual verification (no committed tests, per F11). Run a throwaway script from a temporary folder outside the repo with `poetry run python -I <script>`. Expected:
  - `parse_eur` returns `1234.50`, `115.50` and `0.00` for `€1,234.50`, `115,50 €` and ` € 0.00`, and raises `ValueError` for `abc`.
  - `Match.from_json` with `"draw": 3` gives `Decimal('3')`.
  - `BettingApiClient(base_url, "probe", 10)` pointed at `https://qae-assignment-tau.vercel.app/does-not-exist` raises `ApiError` with status 404 and a non-empty body, not a `JSONDecodeError`.

  Delete the script afterwards.
- [ ] Step 4: Run `poetry run pre-commit run --all-files`. Expected: ruff and strict mypy pass.
- [ ] Step 5: Commit: `feat: settings, money helpers, soft checks and typed API client`.

## Task 3: Shared fixtures and TC-03 (API)

Files:
- Create: `tests/conftest.py`, `tests/api/__init__.py`, `tests/api/test_price_integrity.py`

Uses Task 2. Produces these fixtures:
- `settings` (session): `pytest.exit(str(err), returncode=4)` on `ConfigError`.
- `user_id` (session).
- `api` (function, closed on teardown).
- `fresh_balance` (function): resets, then requires `== INITIAL_BALANCE`. A failed precondition raises at once.
- `catalog` (function).
- `checks` (function).

- [ ] Step 1: Write the test `test_client_supplied_price_fields_are_ignored(api, fresh_balance, catalog, checks)`, marked `api`. Allure labels: `epic("Single Bet Placement")`, `feature("Bet placement API")`, `severity(CRITICAL)`, `tag("TC-03")`. The docstring says why it was chosen: a fraud risk that only the API can show and only the server can prevent. The two test-plan steps are `allure.step` blocks.

```python
stake = Decimal("10.00"); match = catalog[0]
bet = api.place_bet(match.id, Selection.HOME, stake, odds=1000.00, payout=99999.00, balance=99999.00)
checks.equal(bet.odds, match.odds.home, "odds come from the catalog, not the client")
checks.money(bet.payout, expected_payout(stake, match.odds.home), "payout = stake × catalog odds")
checks.money(bet.balance, INITIAL_BALANCE - stake, "response balance = initial − stake")
checks.money(api.get_balance().balance, bet.balance, "stored balance matches the response")
checks.assert_all()
```

- [ ] Step 2: Run `poetry run pytest -m api` with `CANDIDATE_ID` unset, then set to `"   "`. Expected both times: the session exits with "Set CANDIDATE_ID in .env (see .env.example)" and no test runs (edge case 1).
- [ ] Step 3: Copy `.env.example` to `.env` and set `CANDIDATE_ID`. Run `poetry run pytest -m api -v`. Expected: the test runs to completion. A pass, or a single failure listing the failed checks, are both valid outcomes; a failure is a defect for Part A.2. An error in framework code is not valid. `allure-results/` holds the request and response attachments.
- [ ] Step 4: Commit: `test: TC-03 server-side price integrity (API)`.

## Task 4: Selector discovery, UI layer and TC-01 (UI)

Files:
- Create:
  - `src/betting_qa/ui/__init__.py`, `ui/driver.py`, `ui/base.py`, `ui/home_page.py`
  - `ui/components/__init__.py`, `ui/components/match_list.py`, `ui/components/bet_slip.py`, `ui/components/receipt.py`
  - `tests/ui/__init__.py`, `tests/ui/conftest.py`, `tests/ui/test_place_bet.py`
- Modify: `src/betting_qa/reporting.py`, `tests/conftest.py`

Uses Tasks 2 and 3. Produces:
- `create_driver(settings) -> WebDriver`
- `BasePage`, `HomePage`, `MatchList`, `BetSlip`, `SlipSelection`, `ReceiptModal` and `Receipt`, as in `design.md`
- `parse_receipt_timestamp(text: str) -> datetime`, in `receipt.py`
- `attach_ui_evidence(driver, name) -> None`
- the fixtures `driver` and `home`, and the `pytest_runtest_makereport` hookwrapper in `tests/conftest.py`

- [ ] Step 1: Discover selectors (read-only, F6). Open `{BASE_URL}/?user-id=<CANDIDATE_ID>` with `create_driver`, save `page_source` to a temporary folder, click one odds button, save the source again and close. Place no bets. Note the locators for every element the components need (prefer `data-testid`, then `id`, then stable CSS, never positional XPath), whether match rows expose the match id, and the money text format. The receipt only exists after a bet, so its locators and timestamp format come from step 6.
- [ ] Step 2: Implement `driver.py` (options per the global constraints, `goog:loggingPrefs` `{"browser": "ALL"}`) and `base.py` (`WebDriverWait` with `expected_conditions`).
- [ ] Step 3: Implement `HomePage`, `MatchList` and `BetSlip` with the locators from step 1, as module-level `Locator` constants. `BetSlip.place_bet()` clicks, then waits until `Placing...` has gone and either the receipt or an error is shown.
- [ ] Step 4: Implement `tests/ui/conftest.py`:
  - `driver` fixture: function scope. On teardown, if `request.node.rep_call.failed`, call `attach_ui_evidence`. Always `quit()`.
  - `home` fixture: depends on `fresh_balance` and returns `HomePage(driver, settings.ui_timeout).open(settings.base_url, user_id)`.
- [ ] Step 5: Implement `attach_ui_evidence`. The screenshot, page source and console log each sit in their own `try/except WebDriverException` that logs a warning. Verify with a throwaway script that calls it on a driver after `quit()`. Expected: a logged warning and no exception (edge case 5).
- [ ] Step 6: Receipt discovery and delay measurement (F13). Write TC-01 (step 7) with the timestamp check replaced by a measurement, `delay = datetime.now() - parse_receipt_timestamp(...)`, attached to Allure as "Receipt timestamp delay". Implement `ReceiptModal` and `parse_receipt_timestamp` from one headed run: place the bet, save the receipt's page source to a temporary folder, and read its locators and timestamp format. Run `poetry run pytest -m ui -v` and read the measured delay *X*. Set the tolerance from X, then:
  - Replace the measurement with `checks.check(abs(delay) <= <tolerance>, ...)`.
  - Add to DA-G19 in `documentation-analysis.md`: "Observed: actual delay is X minutes. Proposal: the spec should state the timestamp's time zone and accuracy."
- [ ] Step 7: Write TC-01, `test_successful_single_bet_placement(home, api, catalog, checks)`, marked `ui`. Allure labels as in TC-03, with `feature("Bet placement UI")` and `tag("TC-01")`. The docstring says why it was chosen: it is the core revenue journey, and it checks receipt and balance consistency across UI and API. One `allure.step` per test-plan step.

```python
stake = Decimal("10.00"); match = catalog[0]; odds = match.odds.home
checks.money(home.header_balance, INITIAL_BALANCE, "step 2: header balance")
checks.check(bool(re.search(r"\d{1,2}:\d{2}", home.match_list.kickoff_label(match))),
             "step 3: kickoff label shows a time (DA-C2)")
home.match_list.select_odds(match, Selection.HOME)
checks.equal(home.bet_slip.current_selection(),
             SlipSelection(match.home_team, match.away_team, "1", odds), "step 3: slip selection")
home.bet_slip.enter_stake("10.00")
checks.money(home.bet_slip.available_balance, INITIAL_BALANCE, "step 4: slip balance")
slip_payout = home.bet_slip.potential_payout
checks.money(slip_payout, expected_payout(stake, odds), "step 5: potential payout")
home.bet_slip.place_bet()
receipt = home.receipt.wait_until_shown().read()                       # raises if no receipt: journey stops
checks.check(bool(receipt.bet_id.strip()), "step 7: Bet ID present")
checks.equal((receipt.home_team, receipt.away_team, receipt.selection_label),
             (match.home_team, match.away_team, "1"), "step 7: match and selection")
checks.money(receipt.stake, stake, "step 7: stake")
checks.equal(receipt.odds, odds, "step 7: odds")
checks.money(receipt.payout, slip_payout, "step 7: payout matches slip")
# step 7 timestamp: see Step 6 (F13)
home.receipt.close()
checks.check(home.bet_slip.is_empty(), "step 8: slip cleared")
checks.money(home.header_balance, INITIAL_BALANCE - stake, "step 8: header balance")
checks.money(api.get_balance().balance, home.header_balance, "step 9: API balance = header")
# second bet the same way; its receipt.bet_id must differ (DA-G19)
checks.assert_all()
```

- [ ] Step 8: Run `poetry run pytest -v` headed, then `HEADLESS=true poetry run pytest -v`. Expected: both tests run end to end. A pass, or a failure listing the failed checks, are both valid outcomes. A failing UI test has a screenshot, the page source and the console log in `allure-results/`. Then run `poetry run pre-commit run --all-files`, which must pass.
- [ ] Step 9: Commit: `test: UI page objects and TC-01 successful bet placement`.

## Task 5: CI workflow and README

Files:
- Create: `.github/workflows/tests.yml`, `README.md`
- Modify: `openspec/changes/framework-design/tasks.md`

- [ ] Step 1: Write `tests.yml`:
  - Triggers: `push` to `main`, `pull_request`, `workflow_dispatch`, with `permissions: contents: write`.
  - `lint` job: Python 3.12, `pipx install poetry`, `poetry install`, then `ruff check`, `ruff format --check` and `mypy`.
  - `test` job (`needs: lint`): env `HEADLESS: "true"` and `CANDIDATE_ID: ${{ secrets.CANDIDATE_ID }}`, then `poetry run pytest`.
  - Steps with `if: always()`: fetch the `gh-pages` history, generate the Allure report with a maintained Allure action, publish it to GitHub Pages, and upload `allure-results` as an artifact.
- [ ] Step 2: Verify. `poetry run pre-commit run check-yaml --all-files` passes, and `poetry run python -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml'))"` exits 0.
- [ ] Step 3: Write `README.md` to the outline in `design.md`. Include the F11 scope note on unit tests, the `CANDIDATE_ID` instructions (local `.env`, CI secret), the run commands (`poetry run pytest`, `-m api`, `-m ui`), the local report (`allure serve allure-results`, optional, needs Java and the Allure CLI), and the tooling choices with a one-line reason each.
- [ ] Step 4: Fresh-clone check. Clone the repo into a temporary folder with `git clone`, copy `.env` in, then run `poetry install` and `poetry run pytest -m api`. Expected: the same outcome as in the working repo.
- [ ] Step 5: Tick tasks 2.1 to 2.9 in `tasks.md`. Commit: `ci: lint, test and Allure report to GitHub Pages; README`.
