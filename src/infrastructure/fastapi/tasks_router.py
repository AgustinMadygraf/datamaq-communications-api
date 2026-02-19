from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.entities.task import TaskExecutionRequest
from src.infrastructure.fastapi.schemas import TaskStartRequestModel
from src.interface_adapters.controllers.tasks_controller import TasksController
from src.use_cases.errors import LastChatNotAvailableError
from src.use_cases.start_task import StartTaskUseCase


def create_tasks_router(tasks_controller: TasksController, start_task_use_case: StartTaskUseCase) -> APIRouter:
    router = APIRouter()

    @router.post("/tasks/start")
    async def tasks_start(
        payload: TaskStartRequestModel,
        background_tasks: BackgroundTasks,
    ) -> dict[str, Any]:
        request = TaskExecutionRequest(
            duration_seconds=payload.duration_seconds,
            force_fail=payload.force_fail,
            modified_files_count=payload.modified_files_count,
            repository_name=payload.repository_name,
            execution_time_seconds=payload.execution_time_seconds,
            start_datetime=payload.start_datetime,
            end_datetime=payload.end_datetime,
        )

        try:
            return tasks_controller.handle_start_task(
                request=request,
                schedule_background_task=lambda task: background_tasks.add_task(
                    start_task_use_case.run_task_and_notify,
                    task,
                ),
            )
        except LastChatNotAvailableError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return router
