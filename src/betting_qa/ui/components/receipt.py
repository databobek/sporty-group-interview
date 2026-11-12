"""The success receipt modal (SPEC §2.4)."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from betting_qa.ui.base import BasePage, Locator

MODAL: Locator = (By.ID, "modal-success")
BET_ID: Locator = (By.ID, "modal-success-bet-id")
MATCH: Locator = (By.ID, "modal-success-match")
SELECTION: Locator = (By.ID, "modal-success-selection")  # required by SPEC §2.4; may be missing
STAKE: Locator = (By.ID, "modal-success-stake")
ODDS: Locator = (By.ID, "modal-success-odds")
PAYOUT: Locator = (By.ID, "modal-success-payout")
PLACED_AT: Locator = (By.ID, "modal-success-placed-at")
CLOSE: Locator = (By.ID, "modal-success-close")

_RELATIVE_DAYS = {"today": 0, "yesterday": -1}


@dataclass(frozen=True)
class Receipt:
    bet_id: str
    home_team: str
    away_team: str
    selection_label: str | None  # None when the receipt does not show a selection
    stake: Decimal
    odds: Decimal
    payout: Decimal
    timestamp_text: str


def parse_receipt_timestamp(text: str, today: date | None = None) -> datetime:
    """Parse the receipt's "Today, 05:27 PM" format (minute precision, local time)."""
    day_word, _, clock = text.partition(",")
    offset = _RELATIVE_DAYS.get(day_word.strip().lower())
    if offset is None:
        raise ValueError(f"Unknown receipt timestamp format: {text!r}")
    day = (today or date.today()) + timedelta(days=offset)
    time_of_day = datetime.strptime(clock.strip(), "%I:%M %p").time()
    return datetime.combine(day, time_of_day)


class ReceiptModal(BasePage):
    def wait_until_shown(self) -> "ReceiptModal":
        self._find(MODAL)
        return self

    def is_shown(self) -> bool:
        return self._is_visible(MODAL)

    def read(self) -> Receipt:
        home, _, away = self._text(MATCH).partition(" vs ")
        return Receipt(
            bet_id=self._text(BET_ID),
            home_team=home.strip(),
            away_team=away.strip(),
            selection_label=self._text(SELECTION) if self._is_visible(SELECTION) else None,
            stake=self._money(STAKE),
            odds=Decimal(self._text(ODDS)),
            payout=self._money(PAYOUT),
            timestamp_text=self._text(PLACED_AT),
        )

    def close(self) -> None:
        self._click(CLOSE)
        self._wait().until(ec.invisibility_of_element_located(MODAL), "receipt did not close")
