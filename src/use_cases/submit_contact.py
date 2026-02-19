from dataclasses import dataclass
import logging

from src.entities.contact import ContactMessage
from src.use_cases.errors import HoneypotTriggeredError, RateLimitExceededError
from src.use_cases.ports import RateLimiterGateway, RequestIdProvider


@dataclass(frozen=True)
class SubmitContactResult:
    request_id: str
    status: str
    message: str


class SubmitContactUseCase:
    def __init__(
        self,
        rate_limiter_gateway: RateLimiterGateway,
        request_id_provider: RequestIdProvider,
        logger: logging.Logger,
        honeypot_field: str,
        rate_limit_window: int,
        rate_limit_max: int,
    ) -> None:
        self._rate_limiter_gateway = rate_limiter_gateway
        self._request_id_provider = request_id_provider
        self._logger = logger
        self._honeypot_field = honeypot_field.strip()
        self._rate_limit_window = rate_limit_window
        self._rate_limit_max = rate_limit_max

    def submit(
        self,
        contact_message: ContactMessage,
        client_identifier: str,
        endpoint_key: str,
        success_message: str,
    ) -> SubmitContactResult:
        honeypot_raw = contact_message.attribution.get(self._honeypot_field, "")
        honeypot_value = str(honeypot_raw).strip() if honeypot_raw is not None else ""
        if honeypot_value:
            self._logger.warning(
                "honeypot_triggered",
                extra={
                    "event": "honeypot_triggered",
                    "endpoint": endpoint_key,
                    "client_identifier": client_identifier,
                },
            )
            raise HoneypotTriggeredError("honeypot triggered")

        limited_key = f"{endpoint_key}:{client_identifier}"
        is_allowed = self._rate_limiter_gateway.hit(
            key=limited_key,
            window_seconds=self._rate_limit_window,
            max_requests=self._rate_limit_max,
        )
        if not is_allowed:
            self._logger.warning(
                "rate_limit_exceeded",
                extra={
                    "event": "rate_limit_exceeded",
                    "endpoint": endpoint_key,
                    "client_identifier": client_identifier,
                },
            )
            raise RateLimitExceededError("rate limit exceeded")

        request_id = self._request_id_provider.new_id()
        self._logger.info(
            "contact_accepted",
            extra={
                "event": "contact_accepted",
                "endpoint": endpoint_key,
                "request_id": request_id,
                "client_identifier": client_identifier,
            },
        )
        return SubmitContactResult(
            request_id=request_id,
            status="accepted",
            message=success_message,
        )
