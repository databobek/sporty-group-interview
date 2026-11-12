"""Fixtures shared by API and UI tests."""

from collections.abc import Generator, Iterator
from datetime import date

import allure
import pytest

from betting_qa.api import Balance, BettingApiClient, Match
from betting_qa.checks import SoftChecks
from betting_qa.config import ConfigError, Settings
from betting_qa.reporting import register_secret
from betting_qa.rules import INITIAL_BALANCE


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Store each phase's report on the item, so fixtures can tell whether the test failed."""
    report = yield
    setattr(item, f"rep_{report.when}", report)
    return report


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Run settings. Stops the whole session if CANDIDATE_ID is missing."""
    try:
        loaded = Settings.from_env()
    except ConfigError as err:
        pytest.exit(str(err), returncode=4)
    register_secret(loaded.candidate_id)
    return loaded


@pytest.fixture(scope="session")
def user_id(settings: Settings) -> str:
    """The app's user-id: the candidate's own id (design F10)."""
    return settings.candidate_id


@pytest.fixture
def api(settings: Settings, user_id: str) -> Iterator[BettingApiClient]:
    client = BettingApiClient(settings.base_url, user_id, settings.api_timeout)
    yield client
    client.close()


@pytest.fixture
def fresh_balance(api: BettingApiClient) -> Balance:
    """Test plan P3: reset the balance and return what is actually stored (design F16).

    All tests share one user, so the reset is what isolates them. Money checks are made
    relative to the stored balance, so a broken reset is reported once (TC-01 step 2)
    instead of breaking every balance check.
    """
    with allure.step(f"Precondition: reset balance to €{INITIAL_BALANCE}"):
        replied = api.reset_balance()
        stored = api.get_balance()
        if replied.balance != stored.balance:
            allure.attach(
                f"reset-balance replied €{replied.balance} but stored €{stored.balance}; "
                "SPEC §5.3 requires them to be consistent. Checks use the stored balance.",
                name="Reset inconsistency",
                attachment_type=allure.attachment_type.TEXT,
            )
    return stored


@pytest.fixture
def catalog(api: BettingApiClient) -> list[Match]:
    """Test plan P4: the match catalog. An empty catalog fails the entry criteria."""
    with allure.step("Precondition: load the match catalog"):
        matches = api.get_matches()
        assert matches, "GET /api/matches returned no matches (entry criterion)"
    return matches


@pytest.fixture
def upcoming_match(catalog: list[Match]) -> Match:
    """The first match that has not kicked off yet.

    Betting on a past match should be rejected (DA-C6), so tests of a valid bet must
    not pick one; otherwise two defects would mix in one result.
    """
    today = date.today()
    upcoming = [match for match in catalog if match.kickoff_date >= today]
    assert upcoming, f"No match on or after {today} in the catalog (DA-C6)"
    return upcoming[0]


@pytest.fixture
def checks() -> SoftChecks:
    return SoftChecks()
