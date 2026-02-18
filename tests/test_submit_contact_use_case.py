import logging

import pytest

from src.entities.contact import ContactMessage, EmailAddress
from src.use_cases.errors import HoneypotTriggeredError, RateLimitExceededError
from src.use_cases.submit_contact import SubmitContactUseCase


class DummyRateLimiter:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls: list[tuple[str, int, int]] = []

    def hit(self, key: str, window_seconds: int, max_requests: int) -> bool:
        self.calls.append((key, window_seconds, max_requests))
        return self.allowed


class DummyRequestIdProvider:
    def __init__(self, request_id: str = "req-123") -> None:
        self.request_id = request_id

    def new_id(self) -> str:
        return self.request_id


def _build_contact(honeypot_value: str = "") -> ContactMessage:
    return ContactMessage(
        name="Jane Doe",
        email=EmailAddress("jane@example.com"),
        message="Hello",
        meta={"source": "landing"},
        attribution={"website": honeypot_value},
    )


def test_submit_contact_success_returns_accepted_result() -> None:
    use_case = SubmitContactUseCase(
        rate_limiter_gateway=DummyRateLimiter(allowed=True),
        request_id_provider=DummyRequestIdProvider("request-abc"),
        logger=logging.getLogger("test"),
        honeypot_field="website",
        rate_limit_window=60,
        rate_limit_max=5,
    )

    result = use_case.submit(
        contact_message=_build_contact(""),
        client_identifier="127.0.0.1",
        endpoint_key="contact",
        success_message="Contact request accepted for processing",
    )

    assert result.request_id == "request-abc"
    assert result.status == "accepted"


def test_submit_contact_rejects_honeypot() -> None:
    use_case = SubmitContactUseCase(
        rate_limiter_gateway=DummyRateLimiter(allowed=True),
        request_id_provider=DummyRequestIdProvider(),
        logger=logging.getLogger("test"),
        honeypot_field="website",
        rate_limit_window=60,
        rate_limit_max=5,
    )

    with pytest.raises(HoneypotTriggeredError):
        use_case.submit(
            contact_message=_build_contact("spam-value"),
            client_identifier="127.0.0.1",
            endpoint_key="contact",
            success_message="Contact request accepted for processing",
        )


def test_submit_contact_rejects_rate_limit() -> None:
    use_case = SubmitContactUseCase(
        rate_limiter_gateway=DummyRateLimiter(allowed=False),
        request_id_provider=DummyRequestIdProvider(),
        logger=logging.getLogger("test"),
        honeypot_field="website",
        rate_limit_window=60,
        rate_limit_max=5,
    )

    with pytest.raises(RateLimitExceededError):
        use_case.submit(
            contact_message=_build_contact(""),
            client_identifier="127.0.0.1",
            endpoint_key="mail",
            success_message="Mail request accepted for processing",
        )


def test_contact_message_rejects_oversized_utf8_payload() -> None:
    oversized_message = "🙂" * 4000

    with pytest.raises(ValueError, match="message is too large"):
        ContactMessage(
            name="Jane Doe",
            email=EmailAddress("jane@example.com"),
            message=oversized_message,
            meta={},
            attribution={"website": ""},
        )
