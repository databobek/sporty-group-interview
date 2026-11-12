"""Browser fixtures for UI tests."""

from collections.abc import Iterator

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from betting_qa.api import Balance
from betting_qa.config import Settings
from betting_qa.reporting import attach_ui_evidence
from betting_qa.ui.driver import create_driver
from betting_qa.ui.home_page import HomePage


@pytest.fixture
def driver(settings: Settings, request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    """A fresh Chrome per test. On failure, the evidence is attached before it closes."""
    browser = create_driver(settings)
    yield browser
    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        attach_ui_evidence(browser, "On failure")
    browser.quit()


@pytest.fixture
def home(driver: WebDriver, settings: Settings, user_id: str, fresh_balance: Balance) -> HomePage:
    """The app opened as the candidate, after the balance reset (test plan P1-P3)."""
    return HomePage(driver, settings.ui_timeout).open(settings.base_url, user_id)
