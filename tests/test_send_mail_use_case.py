import logging

import pytest

from src.entities.contact import ContactMessage, EmailAddress
from src.use_cases.errors import MailDeliveryError
from src.use_cases.send_mail import SendMailUseCase


class FakeMailGateway:
    def __init__(self, raise_error: bool = False) -> None:
        self.raise_error = raise_error
        self.calls: list[tuple[ContactMessage, str]] = []

    def send_contact_email(self, contact_message: ContactMessage, request_id: str) -> None:
        if self.raise_error:
            raise RuntimeError("smtp down")
        self.calls.append((contact_message, request_id))


def _contact_message() -> ContactMessage:
    return ContactMessage(
        name="John Doe",
        email=EmailAddress("john@example.com"),
        message="Need info",
        meta={},
        attribution={},
    )


def test_send_mail_use_case_delegates_to_gateway() -> None:
    gateway = FakeMailGateway()
    use_case = SendMailUseCase(mail_gateway=gateway, logger=logging.getLogger("test"))

    use_case.execute(_contact_message(), "req-1")

    assert len(gateway.calls) == 1
    assert gateway.calls[0][1] == "req-1"


def test_send_mail_use_case_wraps_errors() -> None:
    gateway = FakeMailGateway(raise_error=True)
    use_case = SendMailUseCase(mail_gateway=gateway, logger=logging.getLogger("test"))

    with pytest.raises(MailDeliveryError):
        use_case.execute(_contact_message(), "req-2")
