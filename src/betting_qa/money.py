"""Money parsing and comparison. Money is always `Decimal`, never float."""

import re
from decimal import Decimal

from betting_qa.rules import MONEY_TOLERANCE

_NOISE = re.compile(r"[€\s]")  # \s also covers the non-breaking space
_AMOUNT = re.compile(r"-?\d+(\.\d+)?")


def parse_eur(text: str) -> Decimal:
    """Parse a euro amount as shown in the UI, e.g. "€1,234.50", "115,50 €", "€ 0.00".

    If both separators appear, "," groups thousands. If only "," appears, it is the
    decimal separator. Anything that is not an amount raises ValueError.
    """
    cleaned = _NOISE.sub("", text)
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    if not _AMOUNT.fullmatch(cleaned):
        raise ValueError(f"Not a euro amount: {text!r}")
    return Decimal(cleaned)


def money_close(actual: Decimal, expected: Decimal, tolerance: Decimal = MONEY_TOLERANCE) -> bool:
    """True when the two amounts differ by at most the tolerance (DA-G1, DA-G18)."""
    return abs(actual - expected) <= tolerance


def expected_payout(stake: Decimal, odds: Decimal) -> Decimal:
    """Stake × odds, unrounded. The spec defines no rounding mode (DA-G1)."""
    return stake * odds
