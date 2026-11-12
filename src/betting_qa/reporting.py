"""Evidence attached to the Allure report.

The report is public, so registered secrets (the candidate's user-id) are replaced by
`***` in every attachment (design F15).
"""

import logging
from urllib.parse import urlsplit

import allure
import requests
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webdriver import WebDriver

log = logging.getLogger(__name__)

MASK = "***"
MASKED_HEADERS = frozenset({"x-user-id"})

_secrets: set[str] = set()


def register_secret(value: str) -> None:
    """Mask this value in every attachment from now on."""
    if value:
        _secrets.add(value)


def mask(text: str) -> str:
    for secret in _secrets:
        text = text.replace(secret, MASK)
    return text


def attach_ui_evidence(driver: WebDriver, name: str) -> None:
    """Attach screenshot, page source and browser console log.

    Each part is captured on its own: if the browser is already gone, the failure is
    logged and the test's original failure is still the one reported.
    """
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"{name}: screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as exc:  # evidence must never replace the real failure
        log.warning("Could not capture screenshot: %s", exc)
    try:
        allure.attach(
            mask(driver.page_source),
            name=f"{name}: page source",
            attachment_type=allure.attachment_type.HTML,
        )
    except Exception as exc:  # evidence must never replace the real failure
        log.warning("Could not capture page source: %s", exc)
    try:
        if not isinstance(driver, ChromiumDriver):
            return
        entries = driver.get_log("browser")  # type: ignore[no-untyped-call]  # selenium is untyped here
        console = "\n".join(f"[{e['level']}] {e['message']}" for e in entries) or "(empty)"
        allure.attach(
            mask(console),
            name=f"{name}: console log",
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception as exc:  # evidence must never replace the real failure
        log.warning("Could not capture console log: %s", exc)


def attach_api_exchange(response: requests.Response) -> None:
    """Attach one HTTP request/response pair as a text attachment."""
    request = response.request
    path = urlsplit(request.url or "").path
    headers = "\n".join(
        f"{name}: {MASK if name.lower() in MASKED_HEADERS else value}"
        for name, value in request.headers.items()
    )
    body = request.body.decode() if isinstance(request.body, bytes) else (request.body or "")
    elapsed_ms = int(response.elapsed.total_seconds() * 1000)
    text = (
        f"{request.method} {request.url}\n{headers}\n\n{body}\n\n"
        f"--- {response.status_code} {response.reason} ({elapsed_ms} ms)\n{response.text}"
    )
    allure.attach(
        mask(text),
        name=f"{request.method} {path} → {response.status_code}",
        attachment_type=allure.attachment_type.TEXT,
    )
