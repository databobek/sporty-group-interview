"""Run settings, read from environment variables (and an optional .env file)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://qae-assignment-tau.vercel.app"
DEFAULT_TIMEOUT = 10.0

_TRUE_VALUES = frozenset({"true", "1", "yes"})
_FALSE_VALUES = frozenset({"false", "0", "no", ""})


class ConfigError(Exception):
    """Raised when the environment does not describe a runnable configuration."""


@dataclass(frozen=True)
class Settings:
    candidate_id: str  # the app's user-id (design F10)
    base_url: str = DEFAULT_BASE_URL
    headless: bool = False
    ui_timeout: float = DEFAULT_TIMEOUT  # seconds, explicit waits
    api_timeout: float = DEFAULT_TIMEOUT  # seconds, HTTP requests
    window_size: tuple[int, int] = (1920, 1080)

    @classmethod
    def from_env(cls) -> Settings:
        """Load `.env` if present, then build settings from the process environment."""
        load_dotenv()
        env = os.environ

        candidate_id = env.get("CANDIDATE_ID", "").strip()
        if not candidate_id:
            raise ConfigError("Set CANDIDATE_ID in .env (see .env.example)")

        return cls(
            candidate_id=candidate_id,
            base_url=env.get("BASE_URL", "").strip().rstrip("/") or DEFAULT_BASE_URL,
            headless=_parse_bool(env, "HEADLESS"),
            ui_timeout=_parse_timeout(env, "UI_TIMEOUT"),
            api_timeout=_parse_timeout(env, "API_TIMEOUT"),
        )


def _parse_bool(env: Mapping[str, str], name: str) -> bool:
    raw = env.get(name, "").strip().lower()
    if raw in _TRUE_VALUES:
        return True
    if raw in _FALSE_VALUES:
        return False
    raise ConfigError(f"{name} must be true/false, 1/0 or yes/no, got {raw!r}")


def _parse_timeout(env: Mapping[str, str], name: str) -> float:
    raw = env.get(name, "").strip()
    if not raw:
        return DEFAULT_TIMEOUT
    try:
        value = float(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a number of seconds, got {raw!r}") from None
    if value <= 0:
        raise ConfigError(f"{name} must be positive, got {raw!r}")
    return value
