import math
import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    mode: str = "demo"
    base_url: str = "http://127.0.0.1:8000/v1"
    api_key: str = field(default="", repr=False)
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    timeout: float = 60

    def __post_init__(self):
        if self.mode not in {"demo", "live"}:
            raise ValueError("SPECGUARD_MODE must be demo or live.")
        if not math.isfinite(self.timeout) or not 0 < self.timeout <= 300:
            raise ValueError("REQUEST_TIMEOUT must be between 0 and 300 seconds.")
        url = urlsplit(self.base_url)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("VLLM_BASE_URL must be an HTTP(S) URL without embedded credentials or query parameters.")
        if url.scheme == "http" and url.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError("Use HTTPS for remote endpoints or localhost through SSH forwarding.")
        if self.mode == "live" and (not self.model.strip() or not self.api_key.strip() or self.api_key.startswith("replace-")):
            raise ValueError("Set VLLM_MODEL and a private VLLM_API_KEY before using Live Mode.")


def load_config() -> Config:
    load_dotenv()
    try:
        return Config(mode=os.getenv("SPECGUARD_MODE", "demo").lower(), base_url=os.getenv("VLLM_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/"), api_key=os.getenv("VLLM_API_KEY", ""), model=os.getenv("VLLM_MODEL", "Qwen/Qwen2.5-7B-Instruct"), timeout=float(os.getenv("REQUEST_TIMEOUT", "60")))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid application configuration: {exc}") from exc
