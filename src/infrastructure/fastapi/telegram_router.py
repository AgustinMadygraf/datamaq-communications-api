from typing import Any

from fastapi import APIRouter, Header, HTTPException

from src.interface_adapters.controllers.telegram_controller import TelegramController
from src.use_cases.errors import InvalidTelegramSecretError


def create_telegram_router(telegram_controller: TelegramController) -> APIRouter:
    router = APIRouter()

    @router.post("/telegram/webhook")
    async def telegram_webhook(
        update: dict[str, Any],
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ) -> dict[str, Any]:
        try:
            return telegram_controller.handle_webhook(update, x_telegram_bot_api_secret_token)
        except InvalidTelegramSecretError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.get("/telegram/last_chat")
    async def telegram_last_chat() -> dict[str, Any]:
        return telegram_controller.handle_last_chat()

    return router
