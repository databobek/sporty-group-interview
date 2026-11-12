"""Base for page objects. All waiting happens here; page objects never call find_element."""

from collections.abc import Callable
from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from betting_qa.money import parse_eur

Locator = tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: float) -> None:
        self.driver = driver
        self.timeout = timeout

    def _wait(self, timeout: float | None = None) -> WebDriverWait[WebDriver]:
        return WebDriverWait(self.driver, self.timeout if timeout is None else timeout)

    def _find(self, locator: Locator) -> WebElement:
        """Wait until the element is visible and return it."""
        return self._wait().until(
            ec.visibility_of_element_located(locator), f"not visible: {locator}"
        )

    def _find_all(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def _click(self, locator: Locator) -> None:
        self._wait().until(ec.element_to_be_clickable(locator), f"not clickable: {locator}").click()

    def _type(self, locator: Locator, text: str) -> None:
        element = self._find(locator)
        element.clear()
        element.send_keys(text)

    def _text(self, locator: Locator) -> str:
        return self._find(locator).text.strip()

    def _money(self, locator: Locator) -> Decimal:
        """Read a euro amount from text that may carry a label, e.g. "Balance: €1.00"."""
        text = self._text(locator)
        return parse_eur(text.rsplit(":", 1)[-1])

    def _is_visible(self, locator: Locator, timeout: float | None = 0) -> bool:
        """Visible now (timeout 0) or within the timeout."""
        try:
            self._wait(timeout).until(ec.visibility_of_element_located(locator))
        except TimeoutException:
            return False
        return True

    def _wait_until(self, condition: Callable[[WebDriver], object], message: str) -> None:
        self._wait().until(condition, message)
