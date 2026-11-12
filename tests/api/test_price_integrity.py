"""TC-03: server-side price integrity (test-plan.md)."""

from decimal import Decimal

import allure
import pytest

from betting_qa.api import Balance, BettingApiClient, Match, Selection
from betting_qa.checks import SoftChecks
from betting_qa.money import expected_payout
from betting_qa.rules import INITIAL_BALANCE


@pytest.mark.api
@allure.epic("Single Bet Placement")
@allure.feature("Bet placement API")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("TC-03")
@allure.title("TC-03: client-supplied odds, payout and balance are ignored")
def test_client_supplied_price_fields_are_ignored(
    api: BettingApiClient, fresh_balance: Balance, upcoming_match: Match, checks: SoftChecks
) -> None:
    """Why this test is automated: it guards against fraud that only the API can show.

    Anyone can send JSON to the API. If the server trusted client-sent odds, payout or
    balance, a customer could set their own price or top up their own balance. The UI
    cannot prevent that; only the server can (SPEC §5.3 "Extra fields may be ignored",
    DA-G11). It is fast, needs no browser, and a failure is unambiguous.
    """
    stake = Decimal("10.00")
    match = upcoming_match
    catalog_odds = match.odds.home

    with allure.step("Step 1: place a bet with odds=1000, payout=99999, balance=99999 added"):
        bet = api.place_bet(
            match.id, Selection.HOME, stake, odds=1000.00, payout=99999.00, balance=99999.00
        )
        checks.equal(bet.odds, catalog_odds, "odds come from the catalog, not the client")
        checks.money(bet.payout, expected_payout(stake, catalog_odds), "payout = stake × odds")
        checks.money(bet.balance, INITIAL_BALANCE - stake, "response balance = initial − stake")

    with allure.step("Step 2: the stored balance matches the response"):
        checks.money(api.get_balance().balance, bet.balance, "GET /api/balance = response")

    checks.assert_all()
