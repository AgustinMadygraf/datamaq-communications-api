from src.entities.task import StartedTask


def present_task_started(task: StartedTask) -> dict[str, object]:
    return {
        "status": "started",
        "chat_id": task.chat_id,
        "duration_seconds": task.duration_seconds,
        "force_fail": task.force_fail,
        "modified_files": list(task.modified_files or ()),
        "repository_name": task.repository_name,
        "execution_time_seconds": task.execution_time_seconds,
    }
