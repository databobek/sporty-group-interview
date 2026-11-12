"""Fixtures shared by API and UI tests."""

from collections.abc import Iterator
from datetime import date

import allure
import pytest

from betting_qa.api import Balance, BettingApiClient, Match
from betting_qa.checks import SoftChecks
from betting_qa.config import ConfigError, Settings
from betting_qa.reporting import register_secret
from betting_qa.rules import INITIAL_BALANCE


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
    """Test plan P3: reset the balance. All tests share one user, so this is the isolation."""
    with allure.step(f"Precondition: reset balance to €{INITIAL_BALANCE}"):
        balance = api.reset_balance()
        assert balance.balance == INITIAL_BALANCE, (
            f"reset-balance returned €{balance.balance}, expected €{INITIAL_BALANCE} (DA-G17)"
        )
    return balance


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
