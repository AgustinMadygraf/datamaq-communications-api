from typing import Protocol


class ChatStateGateway(Protocol):
    def get_last_chat_id(self) -> int | None:
        ...

    def set_last_chat_id(self, chat_id: int) -> None:
        ...


class TelegramNotificationGateway(Protocol):
    async def send_message(self, chat_id: int, text: str) -> None:
        ...


class MailGateway(Protocol):
    def send_contact_email(self, contact_message: object, request_id: str) -> None:
        ...


class RateLimiterGateway(Protocol):
    def hit(self, key: str, window_seconds: int, max_requests: int) -> bool:
        ...


class RequestIdProvider(Protocol):
    def new_id(self) -> str:
        ...

