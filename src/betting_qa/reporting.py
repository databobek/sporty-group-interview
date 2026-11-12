"""Evidence attached to the Allure report."""

from urllib.parse import urlsplit

import allure
import requests

MASKED_HEADERS = frozenset({"x-user-id"})


def attach_api_exchange(response: requests.Response) -> None:
    """Attach one HTTP request/response pair as a text attachment."""
    request = response.request
    path = urlsplit(request.url or "").path
    headers = "\n".join(
        f"{name}: {'***' if name.lower() in MASKED_HEADERS else value}"
        for name, value in request.headers.items()
    )
    body = request.body.decode() if isinstance(request.body, bytes) else (request.body or "")
    elapsed_ms = int(response.elapsed.total_seconds() * 1000)
    text = (
        f"{request.method} {request.url}\n{headers}\n\n{body}\n\n"
        f"--- {response.status_code} {response.reason} ({elapsed_ms} ms)\n{response.text}"
    )
    allure.attach(
        text,
        name=f"{request.method} {path} → {response.status_code}",
        attachment_type=allure.attachment_type.TEXT,
    )
