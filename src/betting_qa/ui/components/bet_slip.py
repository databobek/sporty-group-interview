"""The bet slip (SPEC §2.2, §2.3): one selection, stake, totals and Place Bet."""

from dataclasses import dataclass
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from betting_qa.ui.base import BasePage, Locator

COUNT: Locator = (By.ID, "bet-slip-count")
BALANCE: Locator = (By.ID, "bet-slip-balance")
EMPTY: Locator = (By.CSS_SELECTOR, "#bet-slip .betSlipBodyEmpty")
SELECTION_CARD: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionCard")
SELECTION_TEAMS: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionTeams")
SELECTION_MARKET: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionMarket")
SELECTION_ODDS: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionOdds")
STAKE_INPUT: Locator = (By.ID, "bet-slip-stake-input")
VALIDATION: Locator = (By.CSS_SELECTOR, "#bet-slip .stakeWarning span:last-child")
TOTAL_STAKE: Locator = (By.ID, "bet-slip-total-stake")
PAYOUT: Locator = (By.ID, "bet-slip-potential-payout")
PLACE_BET: Locator = (By.ID, "bet-slip-place-bet")
REMOVE_ALL: Locator = (By.ID, "bet-slip-remove-all")
REMOVE_SELECTION: Locator = (By.ID, "bet-slip-selection-remove")
RESULT_MODAL: Locator = (By.CSS_SELECTOR, ".modalRoot[role=dialog]")  # success or error


@dataclass(frozen=True)
class SlipSelection:
    home_team: str
    away_team: str
    selection_label: str  # as shown, e.g. "Home" from "Match Winner: Home"
    odds: Decimal


class BetSlip(BasePage):
    def current_selection(self) -> SlipSelection | None:
        if not self._is_visible(SELECTION_CARD):
            return None
        home, _, away = self._text(SELECTION_TEAMS).partition(" vs ")
        market = self._text(SELECTION_MARKET).rsplit(":", 1)[-1].strip()
        odds = Decimal(self._text(SELECTION_ODDS).rsplit(":", 1)[-1].strip())
        return SlipSelection(home.strip(), away.strip(), market, odds)

    def selection_count(self) -> int:
        return int(self._text(COUNT))

    def enter_stake(self, raw: str) -> None:
        """Type exactly what a user would type, so invalid input can be tested (TC-04)."""
        field = self._find(STAKE_INPUT)
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.DELETE)
        field.send_keys(raw)

    @property
    def stake_value(self) -> str:
        return self._find(STAKE_INPUT).get_attribute("value") or ""

    @property
    def available_balance(self) -> Decimal | None:
        """None when the slip does not show a balance (SPEC §2.2 says it must)."""
        return self._money(BALANCE) if self._is_visible(BALANCE) else None

    @property
    def total_stake(self) -> Decimal:
        return self._money(TOTAL_STAKE)

    @property
    def potential_payout(self) -> Decimal:
        return self._money(PAYOUT)

    @property
    def validation_message(self) -> str | None:
        return self._text(VALIDATION) if self._is_visible(VALIDATION) else None

    def is_place_bet_enabled(self) -> bool:
        return self._find(PLACE_BET).is_enabled()

    def place_bet(self) -> None:
        """Click Place Bet and wait until it resolves to a result modal (SPEC §2.3)."""
        self._click(PLACE_BET)
        self._wait_until(
            lambda d: self._is_visible(RESULT_MODAL), "placement did not resolve to a modal"
        )

    @property
    def place_bet_text(self) -> str:
        """Button text as rendered (CSS upper-cases it, e.g. "PLACING...")."""
        return self._text(PLACE_BET)

    def double_click_place_bet(self) -> None:
        button = self._find(PLACE_BET)
        button.click()
        button.click()

    def remove_all(self) -> None:
        self._click(REMOVE_ALL)

    def remove_selection(self) -> None:
        self._click(REMOVE_SELECTION)

    def is_empty(self) -> bool:
        return self._is_visible(EMPTY)
