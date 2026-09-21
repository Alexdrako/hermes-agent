"""Atria provider profile — Anthropic-compatible API."""

import json
import logging
import os
import urllib.request

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)


class AtriaProfile(ProviderProfile):
    """Atria speaks the Anthropic Messages wire: x-api-key + anthropic-version."""

    def fetch_models(
        self, *, api_key: str | None = None, base_url: str | None = None, timeout: float = 8.0
    ) -> list[str] | None:
        effective_base = (base_url or os.getenv("ATRIA_BASE_URL") or self.base_url).rstrip("/")
        if not api_key:
            api_key = os.getenv("ATRIA_API_KEY") or ""
        if not api_key:
            return None
        try:
            req = urllib.request.Request(effective_base + "/v1/models")
            for k, v in (
                ("x-api-key", api_key),
                ("anthropic-version", "2023-06-01"),
                ("Accept", "application/json"),
            ):
                req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            return [m["id"] for m in data.get("data", []) if isinstance(m, dict) and "id" in m]
        except Exception as exc:
            logger.debug("fetch_models(atria): %s", exc)
            return None


atria = AtriaProfile(
    name="atria",
    aliases=("atria-ai", "atria-asi"),
    display_name="Atria",
    description="Atria — Anthropic-compatible multi-model API",
    signup_url="https://api.atria-asi.ai/",
    env_vars=("ATRIA_API_KEY", "ATRIA_BASE_URL"),
    api_mode="anthropic_messages",
    base_url="https://api.atria-asi.ai",
    auth_type="api_key",
    fallback_models=(
        "Atria-Dawn-Preview",
    ),
)

register_provider(atria)
