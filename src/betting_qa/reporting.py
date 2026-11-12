"""Evidence attached to the Allure report.

The report is public, so registered secrets (the candidate's user-id) are replaced by
`***` in every attachment (design F15).
"""

from urllib.parse import urlsplit

import allure
import requests

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
