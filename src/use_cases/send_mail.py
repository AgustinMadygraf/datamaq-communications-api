import logging

from src.entities.contact import ContactMessage
from src.use_cases.errors import MailDeliveryError
from src.use_cases.ports import MailGateway


class SendMailUseCase:
    def __init__(self, mail_gateway: MailGateway, logger: logging.Logger) -> None:
        self._mail_gateway = mail_gateway
        self._logger = logger

    def execute(self, contact_message: ContactMessage, request_id: str) -> None:
        try:
            self._mail_gateway.send_contact_email(contact_message=contact_message, request_id=request_id)
        except Exception as exc:
            self._logger.exception(
                "mail_delivery_failed",
                extra={
                    "event": "mail_delivery_failed",
                    "request_id": request_id,
                },
            )
            raise MailDeliveryError("mail delivery failed") from exc
