"""The match list (SPEC §2.1): one card per match, with 1 / X / 2 odds buttons."""

from decimal import Decimal

from selenium.webdriver.common.by import By

from betting_qa.api.models import Match, Odds, Selection
from betting_qa.ui.base import BasePage, Locator

_ODDS_SUFFIX = {Selection.HOME: "home", Selection.DRAW: "draw", Selection.AWAY: "away"}


def _card(match: Match) -> Locator:
    return (By.ID, f"match-card-{match.id}")


def _odds_button(match: Match, selection: Selection) -> Locator:
    return (By.ID, f"odds-{match.id}-{_ODDS_SUFFIX[selection]}")


def _odds_value(match: Match, selection: Selection) -> Locator:
    return (By.CSS_SELECTOR, f"#odds-{match.id}-{_ODDS_SUFFIX[selection]} .oddsButtonValue")


def _kickoff(match: Match) -> Locator:
    return (By.CSS_SELECTOR, f"#match-card-{match.id} .matchMeta span:last-child")


class MatchList(BasePage):
    def select_odds(self, match: Match, selection: Selection) -> None:
        self._find(_card(match))
        self._click(_odds_button(match, selection))

    def is_selected(self, match: Match, selection: Selection) -> bool:
        classes = self._find(_odds_button(match, selection)).get_attribute("class") or ""
        return "oddsButtonSelected" in classes.split()

    def kickoff_label(self, match: Match) -> str:
        return self._text(_kickoff(match))

    def odds_shown(self, match: Match) -> Odds:
        values = {s: Decimal(self._text(_odds_value(match, s))) for s in Selection}
        return Odds(
            home=values[Selection.HOME], draw=values[Selection.DRAW], away=values[Selection.AWAY]
        )
