import asyncio
import logging
import time

from src.entities.task import StartedTask, TaskExecutionRequest
from src.use_cases.errors import LastChatNotAvailableError
from src.use_cases.ports import ChatStateGateway, TelegramNotificationGateway


class StartTaskUseCase:
    def __init__(
        self,
        chat_state_gateway: ChatStateGateway,
        telegram_notification_gateway: TelegramNotificationGateway,
        logger: logging.Logger,
        repository_name: str,
        fallback_chat_id: int | None = None,
    ) -> None:
        self._chat_state_gateway = chat_state_gateway
        self._telegram_notification_gateway = telegram_notification_gateway
        self._logger = logger
        self._repository_name = repository_name.strip() or "unknown-repository"
        self._fallback_chat_id = fallback_chat_id

    @staticmethod
    def _normalize_modified_files(modified_files: tuple[str, ...] | None) -> tuple[str, ...]:
        if not modified_files:
            return ()
        normalized: list[str] = []
        for raw_path in modified_files:
            path = raw_path.strip()
            if path:
                normalized.append(path)
        return tuple(normalized)

    @staticmethod
    def _normalize_repository_name(repository_name: str | None) -> str:
        if repository_name is None:
            return ""
        return repository_name.strip()

    def _build_notification_message(
        self,
        status_text: str,
        task: StartedTask,
        elapsed_seconds: float,
    ) -> str:
        modified_files = self._normalize_modified_files(task.modified_files)
        if modified_files:
            files_line = "Archivos modificados: " + ", ".join(modified_files)
        else:
            files_line = "Archivos modificados: (sin detalle)"

        repository_name = self._normalize_repository_name(task.repository_name)
        if not repository_name:
            repository_name = self._repository_name

        return "\n".join(
            [
                status_text,
                f"Repositorio: {repository_name}",
                f"Tiempo de ejecucion: {elapsed_seconds:.2f}s",
                files_line,
            ]
        )

    def start(self, request: TaskExecutionRequest) -> StartedTask:
        modified_files = self._normalize_modified_files(request.modified_files)
        repository_name = self._normalize_repository_name(request.repository_name)
        self._logger.info(
            "POST /tasks/start payload=%s",
            {
                "duration_seconds": request.duration_seconds,
                "force_fail": request.force_fail,
                "modified_files": modified_files,
                "repository_name": repository_name,
                "execution_time_seconds": request.execution_time_seconds,
            },
        )
        chat_id = self._chat_state_gateway.get_last_chat_id()
        if chat_id is None:
            if self._fallback_chat_id is not None:
                chat_id = self._fallback_chat_id
                self._chat_state_gateway.set_last_chat_id(chat_id)
                self._logger.info("Usando TELEGRAM_CHAT_ID fallback: %s", chat_id)
            else:
                raise LastChatNotAvailableError(
                    "last_chat_id es null. Escribile al bot primero para capturarlo "
                    "o configura TELEGRAM_CHAT_ID en .env."
                )

        self._logger.info("Programando tarea para chat_id=%s", chat_id)
        return StartedTask(
            chat_id=chat_id,
            duration_seconds=request.duration_seconds,
            force_fail=request.force_fail,
            modified_files=modified_files or None,
            repository_name=repository_name or None,
            execution_time_seconds=request.execution_time_seconds,
        )

    async def run_task_and_notify(self, task: StartedTask) -> None:
        self._logger.info(
            "Tarea iniciada. chat_id=%s duration_seconds=%s force_fail=%s modified_files=%s",
            task.chat_id,
            task.duration_seconds,
            task.force_fail,
            task.modified_files,
        )
        started_at = time.perf_counter()
        try:
            await asyncio.sleep(task.duration_seconds)
            self._logger.info("Tarea finalizo espera. chat_id=%s", task.chat_id)

            if task.force_fail:
                raise RuntimeError("Falla forzada para prueba MVP.")

            elapsed_seconds = time.perf_counter() - started_at
            if task.execution_time_seconds is not None:
                elapsed_seconds = task.execution_time_seconds
            message = self._build_notification_message("Termin\u00e9", task, elapsed_seconds)
            await self._telegram_notification_gateway.send_message(task.chat_id, message)
        except Exception:
            self._logger.exception("La tarea fallo.")
            elapsed_seconds = time.perf_counter() - started_at
            if task.execution_time_seconds is not None:
                elapsed_seconds = task.execution_time_seconds
            message = self._build_notification_message("Fall\u00f3", task, elapsed_seconds)
            await self._telegram_notification_gateway.send_message(task.chat_id, message)
