"""TC-01: successful single bet placement (test-plan.md)."""

import re
from datetime import datetime
from decimal import Decimal

import allure
import pytest

from betting_qa.api import Balance, BettingApiClient, Match, Selection
from betting_qa.checks import SoftChecks
from betting_qa.money import expected_payout
from betting_qa.rules import INITIAL_BALANCE
from betting_qa.ui.components.bet_slip import SlipSelection
from betting_qa.ui.components.receipt import parse_receipt_timestamp
from betting_qa.ui.home_page import HomePage

STAKE = Decimal("10.00")


@pytest.mark.ui
@allure.epic("Single Bet Placement")
@allure.feature("Bet placement UI")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("TC-01")
@allure.title("TC-01: a single bet is placed and the receipt and balance agree")
def test_successful_single_bet_placement(
    home: HomePage,
    api: BettingApiClient,
    fresh_balance: Balance,
    upcoming_match: Match,
    checks: SoftChecks,
) -> None:
    """Why this test is automated: it is the journey that earns money.

    It runs the whole customer path once (select odds, enter a stake, place, read the
    receipt, close) and checks that slip, receipt, header and API agree on every amount.
    A break anywhere here means no bets, or bets charged or paid at the wrong amount.
    """
    match = upcoming_match
    odds = match.odds.home
    side = Selection.HOME.value.title()  # "Home", as the slip and receipt label it
    start = fresh_balance.balance  # stored balance after the reset (design F16)

    with allure.step("Step 2: header shows the starting balance"):
        checks.money(home.header_balance, INITIAL_BALANCE, "step 2: header balance (DA-G17)")

    with allure.step("Step 3: select the home odds (1)"):
        kickoff = home.match_list.kickoff_label(match)
        checks.check(
            bool(re.search(r"\d{1,2}:\d{2}", kickoff)),
            f"step 3: kickoff label shows a time (DA-C2), got {kickoff!r}",
        )
        home.match_list.select_odds(match, Selection.HOME)
        checks.equal(
            home.bet_slip.current_selection(),
            SlipSelection(match.home_team, match.away_team, side, odds),
            "step 3: slip selection",
        )

    with allure.step(f"Step 4: enter a stake of €{STAKE}"):
        home.bet_slip.enter_stake(str(STAKE))
        checks.money(home.bet_slip.total_stake, STAKE, "step 4: slip stake")
        slip_balance = home.bet_slip.available_balance
        if slip_balance is None:
            checks.check(False, "step 4: slip shows the available balance (SPEC §2.2)")
        else:
            checks.money(slip_balance, start, "step 4: slip balance")

    with allure.step("Step 5: potential payout = stake × odds"):
        slip_payout = home.bet_slip.potential_payout
        checks.money(slip_payout, expected_payout(STAKE, odds), "step 5: potential payout")

    with allure.step("Step 6: place the bet"):
        home.bet_slip.place_bet()

    with allure.step("Step 7: the receipt matches the bet"):
        receipt = home.receipt.wait_until_shown().read()
        checks.check(bool(receipt.bet_id.strip("# ")), "step 7: Bet ID present")
        checks.equal(
            (receipt.home_team, receipt.away_team),
            (match.home_team, match.away_team),
            "step 7: match (home vs away)",
        )
        checks.equal(receipt.selection_label, side, "step 7: selection")
        checks.money(receipt.stake, STAKE, "step 7: stake")
        checks.equal(receipt.odds, odds, "step 7: odds")
        checks.money(receipt.payout, slip_payout, "step 7: payout matches the slip")
        # Design F13a: recorded, not asserted. The receipt shows minutes only (DA-G19).
        delay = datetime.now() - parse_receipt_timestamp(receipt.timestamp_text)
        allure.attach(
            f"Displayed {receipt.timestamp_text!r}; now minus displayed = {delay} "
            "(display precision is 1 minute)",
            name="Receipt timestamp",
            attachment_type=allure.attachment_type.TEXT,
        )

    with allure.step("Step 8: closing the receipt clears the slip and deducts the stake"):
        home.receipt.close()
        checks.check(home.bet_slip.is_empty(), "step 8: slip cleared")
        checks.money(home.header_balance, start - STAKE, "step 8: header balance = start − stake")

    with allure.step("Step 9: the API balance matches the header"):
        checks.money(api.get_balance().balance, home.header_balance, "step 9: API = header")

    with allure.step("Second bet: its Bet ID differs from the first (DA-G19)"):
        home.match_list.select_odds(match, Selection.HOME)
        home.bet_slip.enter_stake(str(STAKE))
        home.bet_slip.place_bet()
        second = home.receipt.wait_until_shown().read()
        checks.check(second.bet_id != receipt.bet_id, "second bet has a different Bet ID")
        home.receipt.close()

    checks.assert_all()
