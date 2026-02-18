from contextvars import ContextVar, Token
from uuid import uuid4

from src.use_cases.ports import RequestIdProvider


_request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> Token[str | None]:
    return _request_id_context.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id_context.reset(token)


def get_request_id() -> str | None:
    return _request_id_context.get()


class ContextRequestIdProvider(RequestIdProvider):
    def new_id(self) -> str:
        request_id = get_request_id()
        if request_id:
            return request_id
        return str(uuid4())
