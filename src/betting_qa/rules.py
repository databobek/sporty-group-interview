"""Business rules from the feature spec, in one place.

Each value cites its source: the feature spec (SPEC §x) or a decision in
documentation-analysis.md (DA-xx).
"""

from decimal import Decimal

INITIAL_BALANCE = Decimal("125.50")  # glossary "Balance"; DA-G17
MIN_STAKE = Decimal("1.00")  # SPEC §3, §4.4; DA-C1 (not the €1.01 in §4.1)
MAX_STAKE = Decimal("100.00")  # SPEC §3, §4.1, §4.4
MONEY_TOLERANCE = Decimal("0.01")  # DA-G1, DA-G18
CURRENCY = "EUR"  # SPEC §3, §5.3
