"""HTTP client for the betting API (SPEC §5). Every exchange is attached to Allure."""

from __future__ import annotations

import json
from collections.abc import Mapping
from decimal import Decimal
from typing import Any

import requests

from betting_qa.api.models import Balance, BetResponse, Match, Selection
from betting_qa.reporting import attach_api_exchange


class ApiError(Exception):
    """A typed call got something other than a 200 with a JSON body."""

    def __init__(self, method: str, url: str, status_code: int, body: str) -> None:
        super().__init__(f"{method} {url} returned {status_code}: {body[:500]}")
        self.status_code = status_code
        self.body = body


def _json_default(value: object) -> object:
    if isinstance(value, Decimal):
        return float(value)  # JSON has no decimal type; see test plan B-03
    raise TypeError(f"Not JSON serializable: {value!r}")


def _attach_hook(response: requests.Response, *args: object, **kwargs: object) -> None:
    attach_api_exchange(response)


class BettingApiClient:
    """One client per user. Typed methods expect 200; `place_bet_raw` is for negative tests."""

    def __init__(self, base_url: str, user_id: str | None, timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        if user_id is not None:
            self._session.headers["x-user-id"] = user_id
        self._session.hooks["response"].append(_attach_hook)

    def get_matches(self) -> list[Match]:
        data = self._expect_json(self._send("GET", "/api/matches"))
        return [Match.from_json(item) for item in data]

    def get_balance(self) -> Balance:
        return Balance.from_json(self._expect_json(self._send("GET", "/api/balance")))

    def reset_balance(self) -> Balance:
        return Balance.from_json(self._expect_json(self._send("POST", "/api/reset-balance")))

    def place_bet(
        self, match_id: str, selection: Selection, stake: Decimal, **extra_fields: object
    ) -> BetResponse:
        """Place a bet. `extra_fields` are sent alongside the required ones (TC-03)."""
        payload = {
            "matchId": match_id,
            "selection": selection.value,
            "stake": stake,
            **extra_fields,
        }
        return BetResponse.from_json(
            self._expect_json(self._send("POST", "/api/place-bet", payload))
        )

    def place_bet_raw(
        self, payload: object, *, headers: Mapping[str, str | None] | None = None
    ) -> requests.Response:
        """POST any payload without checking the result.

        A `str` payload is sent as-is (for malformed JSON). A header set to None is
        removed from the request, e.g. `{"x-user-id": None}` for an unauthenticated call.
        """
        return self._send("POST", "/api/place-bet", payload, headers)

    def close(self) -> None:
        self._session.close()

    def _send(
        self,
        method: str,
        path: str,
        payload: object = None,
        headers: Mapping[str, str | None] | None = None,
    ) -> requests.Response:
        request_headers: dict[str, str | None] = {}
        data: str | None = None
        if payload is not None:
            data = (
                payload if isinstance(payload, str) else json.dumps(payload, default=_json_default)
            )
            request_headers["Content-Type"] = "application/json"
        request_headers.update(headers or {})
        return self._session.request(
            method,
            f"{self._base_url}{path}",
            data=data,
            headers=request_headers,  # a None value removes that session header
            timeout=self._timeout,
        )

    @staticmethod
    def _expect_json(response: requests.Response) -> Any:
        request = response.request
        if response.status_code != 200:
            raise ApiError(
                str(request.method), str(request.url), response.status_code, response.text
            )
        try:
            return response.json(parse_float=Decimal)
        except ValueError:
            raise ApiError(
                str(request.method), str(request.url), response.status_code, response.text
            ) from None
