"""The application shell: header balance plus the match list, bet slip and receipt."""

from decimal import Decimal

from selenium.webdriver.common.by import By

from betting_qa.ui.base import BasePage, Locator
from betting_qa.ui.components.bet_slip import BetSlip
from betting_qa.ui.components.match_list import MatchList
from betting_qa.ui.components.receipt import ReceiptModal

HEADER_BALANCE: Locator = (By.ID, "header-balance")
MATCH_LIST: Locator = (By.ID, "match-list")
MATCH_CARD: Locator = (By.CSS_SELECTOR, "#match-list .matchCard")


class HomePage(BasePage):
    def open(self, base_url: str, user_id: str) -> "HomePage":
        """Open the app as this user and wait until the matches have rendered."""
        self.driver.get(f"{base_url}/?user-id={user_id}")
        self._find(MATCH_LIST)
        self._wait_until(lambda d: len(self._find_all(MATCH_CARD)) > 0, "no match cards rendered")
        return self

    @property
    def header_balance(self) -> Decimal:
        return self._money(HEADER_BALANCE)

    @property
    def match_list(self) -> MatchList:
        return MatchList(self.driver, self.timeout)

    @property
    def bet_slip(self) -> BetSlip:
        return BetSlip(self.driver, self.timeout)

    @property
    def receipt(self) -> ReceiptModal:
        return ReceiptModal(self.driver, self.timeout)
