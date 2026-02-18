from dataclasses import dataclass
import re
from typing import Any


_EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
_MAX_MESSAGE_CHARS = 5000
_MAX_MESSAGE_BYTES = 15000


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("email is required")
        if len(normalized) > 254:
            raise ValueError("email is too long")
        if not _EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("email format is invalid")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class ContactMessage:
    name: str
    email: EmailAddress
    message: str
    meta: dict[str, Any]
    attribution: dict[str, Any]

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        normalized_message = self.message.strip()

        if not normalized_name:
            raise ValueError("name is required")
        if len(normalized_name) > 120:
            raise ValueError("name is too long")
        if not normalized_message:
            raise ValueError("message is required")
        if len(normalized_message) > _MAX_MESSAGE_CHARS:
            raise ValueError("message is too long")
        if len(normalized_message.encode("utf-8")) > _MAX_MESSAGE_BYTES:
            raise ValueError("message is too large")

        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "message", normalized_message)
        object.__setattr__(self, "meta", dict(self.meta or {}))
        object.__setattr__(self, "attribution", dict(self.attribution or {}))
