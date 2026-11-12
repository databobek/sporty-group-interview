"""Typed views of the API payloads (SPEC §5.3). Money fields are always Decimal."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Any


def _decimal(value: Any) -> Decimal:
    """JSON parsed with parse_float=Decimal still yields int for whole numbers."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float) and not isinstance(value, bool):
        return Decimal(str(value))
    raise TypeError(f"Expected a number, got {value!r}")


class Selection(StrEnum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"

    @property
    def ui_label(self) -> str:
        """The odds button label in the UI: 1 (home), X (draw), 2 (away)."""
        return {"HOME": "1", "DRAW": "X", "AWAY": "2"}[self.value]


@dataclass(frozen=True)
class Odds:
    home: Decimal
    draw: Decimal
    away: Decimal

    def for_selection(self, selection: Selection) -> Decimal:
        return {Selection.HOME: self.home, Selection.DRAW: self.draw, Selection.AWAY: self.away}[
            selection
        ]

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> Odds:
        return cls(
            home=_decimal(data["home"]), draw=_decimal(data["draw"]), away=_decimal(data["away"])
        )


@dataclass(frozen=True)
class Match:
    id: str
    competition: str
    kickoff_date: date
    home_team: str
    away_team: str
    odds: Odds

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> Match:
        return cls(
            id=str(data["id"]),
            competition=str(data["competition"]),
            kickoff_date=date.fromisoformat(data["kickoffDate"]),
            home_team=str(data["homeTeam"]),
            away_team=str(data["awayTeam"]),
            odds=Odds.from_json(data["odds"]),
        )


@dataclass(frozen=True)
class Balance:
    balance: Decimal
    currency: str

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> Balance:
        return cls(balance=_decimal(data["balance"]), currency=str(data["currency"]))


@dataclass(frozen=True)
class BetResponse:
    message: str
    match_id: str
    selection: Selection
    stake: Decimal
    odds: Decimal
    payout: Decimal
    balance: Decimal
    currency: str

    @classmethod
    def from_json(cls, data: Mapping[str, Any]) -> BetResponse:
        return cls(
            message=str(data["message"]),
            match_id=str(data["matchId"]),
            selection=Selection(data["selection"]),
            stake=_decimal(data["stake"]),
            odds=_decimal(data["odds"]),
            payout=_decimal(data["payout"]),
            balance=_decimal(data["balance"]),
            currency=str(data["currency"]),
        )
