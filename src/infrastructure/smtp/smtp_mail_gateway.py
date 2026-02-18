from email.message import EmailMessage
import json
import logging
import smtplib

from src.entities.contact import ContactMessage
from src.use_cases.ports import MailGateway


class SmtpMailGateway(MailGateway):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool,
        sender: str,
        default_recipient: str,
        logger: logging.Logger,
        timeout_seconds: float = 20.0,
    ) -> None:
        self._host = host.strip()
        self._port = port
        self._username = username.strip()
        self._password = password
        self._use_tls = use_tls
        self._sender = sender.strip()
        self._default_recipient = default_recipient.strip()
        self._logger = logger
        self._timeout_seconds = timeout_seconds

    @staticmethod
    def _safe_text(value: object, max_length: int = 6000) -> str:
        text = str(value)
        sanitized = text.replace("\r", " ").replace("\n", " ").strip()
        if len(sanitized) > max_length:
            return f"{sanitized[:max_length]}..."
        return sanitized

    @classmethod
    def _safe_json(cls, value: object, max_length: int = 6000) -> str:
        serialized = json.dumps(value, ensure_ascii=False, default=str)
        return cls._safe_text(serialized, max_length=max_length)

    def send_contact_email(self, contact_message: ContactMessage, request_id: str) -> None:
        safe_request_id = self._safe_text(request_id, max_length=128)
        message = EmailMessage()
        message["Subject"] = f"[Contact] New request #{safe_request_id}"
        message["From"] = self._sender
        message["To"] = self._default_recipient
        message["Reply-To"] = contact_message.email.value

        body = "\n".join(
            [
                f"request_id: {safe_request_id}",
                f"name: {self._safe_text(contact_message.name, max_length=256)}",
                f"email: {contact_message.email.value}",
                f"message: {self._safe_text(contact_message.message, max_length=6000)}",
                f"meta: {self._safe_json(contact_message.meta, max_length=3000)}",
                f"attribution: {self._safe_json(contact_message.attribution, max_length=3000)}",
            ]
        )
        message.set_content(body)

        self._logger.info("Sending SMTP email. request_id=%s to=%s", safe_request_id, self._default_recipient)
        with smtplib.SMTP(self._host, self._port, timeout=self._timeout_seconds) as smtp:
            if self._use_tls:
                smtp.starttls()
            if self._username:
                smtp.login(self._username, self._password)
            smtp.send_message(message)
