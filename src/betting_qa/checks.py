"""Soft checks: collect every failed check and fail the test once, at the end (design F12)."""

from decimal import Decimal

import allure

from betting_qa.money import money_close
from betting_qa.rules import MONEY_TOLERANCE


class SoftChecks:
    """Records failed checks instead of stopping at the first one.

    Each check returns whether it passed. Call `assert_all()` as the last line of the test.
    """

    def __init__(self) -> None:
        self._failures: list[str] = []

    def check(self, condition: bool, description: str) -> bool:
        if not condition:
            self._failures.append(description)
        return condition

    def equal(self, actual: object, expected: object, what: str) -> bool:
        return self.check(actual == expected, f"{what}: expected {expected!r}, got {actual!r}")

    def money(self, actual: Decimal, expected: Decimal, what: str) -> bool:
        return self.check(
            money_close(actual, expected),
            f"{what}: expected €{expected} (±€{MONEY_TOLERANCE}), got €{actual}",
        )

    @property
    def failures(self) -> list[str]:
        return list(self._failures)

    def assert_all(self) -> None:
        """Fail with every recorded failure listed, and attach the list to the Allure report."""
        __tracebackhide__ = True
        if not self._failures:
            return
        report = f"{len(self._failures)} check(s) failed:\n" + "\n".join(
            f"- {failure}" for failure in self._failures
        )
        allure.attach(report, name="Failed checks", attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(report)
