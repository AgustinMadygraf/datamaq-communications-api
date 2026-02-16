import os
from dataclasses import dataclass
from pathlib import Path


def parse_bool(value: str, default: bool) -> bool:
    text = value.strip().lower()
    if not text:
        return default
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def parse_int(value: str, default: int) -> int:
    text = value.strip()
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


def parse_optional_int(value: str) -> int | None:
    text = value.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def load_env_file(env_path: Path) -> list[str]:
    if not env_path.exists():
        return []

    loaded_keys: list[str] = []
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
            loaded_keys.append(key)

    return loaded_keys


@dataclass(frozen=True)
class Settings:
    project_root: Path
    env_path: Path
    state_file_path: Path
    loaded_env_keys: tuple[str, ...]
    server_host: str
    server_port: int
    ngrok_enabled: bool
    ngrok_authtoken: str
    ngrok_domain: str
    auto_set_webhook: bool
    drop_pending_updates: bool
    telegram_webhook_path: str
    repository_name: str
    telegram_chat_id: int | None
    telegram_token: str
    telegram_webhook_secret: str
    telegram_api_base_url: str


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"
    loaded_env_keys = load_env_file(env_path)

    return Settings(
        project_root=project_root,
        env_path=env_path,
        state_file_path=project_root / ".last_chat_id",
        loaded_env_keys=tuple(loaded_env_keys),
        server_host=os.getenv("SERVER_HOST", "0.0.0.0").strip() or "0.0.0.0",
        server_port=parse_int(os.getenv("SERVER_PORT", "8000"), 8000),
        ngrok_enabled=parse_bool(os.getenv("NGROK_ENABLED", "true"), True),
        ngrok_authtoken=os.getenv("NGROK_AUTHTOKEN", "").strip(),
        ngrok_domain=os.getenv("NGROK_DOMAIN", "").strip(),
        auto_set_webhook=parse_bool(os.getenv("AUTO_SET_WEBHOOK", "true"), True),
        drop_pending_updates=parse_bool(os.getenv("DROP_PENDING_UPDATES", "true"), True),
        telegram_webhook_path=os.getenv("TELEGRAM_WEBHOOK_PATH", "/telegram/webhook").strip()
        or "/telegram/webhook",
        repository_name=os.getenv("REPOSITORY_NAME", project_root.name).strip() or project_root.name,
        telegram_chat_id=parse_optional_int(os.getenv("TELEGRAM_CHAT_ID", "")),
        telegram_token=os.getenv("TELEGRAM_TOKEN", "").strip(),
        telegram_webhook_secret=os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip(),
        telegram_api_base_url=os.getenv("TELEGRAM_API_BASE_URL", "https://api.telegram.org").strip(),
    )
