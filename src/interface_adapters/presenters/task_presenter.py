from src.entities.task import StartedTask
from src.shared.datetime_utils import to_utc_iso


def present_task_started(task: StartedTask) -> dict[str, object]:
    return {
        "status": "started",
        "chat_id": task.chat_id,
        "duration_seconds": task.duration_seconds,
        "force_fail": task.force_fail,
        "modified_files_count": task.modified_files_count,
        "repository_name": task.repository_name,
        "execution_time_seconds": task.execution_time_seconds,
        "start_datetime": to_utc_iso(task.start_datetime),
        "end_datetime": to_utc_iso(task.end_datetime),
    }
