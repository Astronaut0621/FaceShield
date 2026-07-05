from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.enums import TaskStatus, TaskType
from app.models.detection_result import DetectionResult
from app.models.detection_task import DetectionTask


class DetectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        file_id: int,
        user_id: int | None = None,
        task_type: TaskType = TaskType.IMAGE,
    ) -> DetectionTask:
        task = DetectionTask(
            user_id=user_id,
            file_id=file_id,
            task_status=TaskStatus.PENDING.value,
            task_type=task_type.value,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_task_running(self, task: DetectionTask) -> DetectionTask:
        task.task_status = TaskStatus.RUNNING.value
        task.started_at = datetime.now()
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_task_success(self, task: DetectionTask) -> DetectionTask:
        task.task_status = TaskStatus.SUCCESS.value
        task.finished_at = datetime.now()
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_task_failed(self, task: DetectionTask, error_message: str) -> DetectionTask:
        task.task_status = TaskStatus.FAILED.value
        task.error_message = error_message
        task.finished_at = datetime.now()
        self.db.commit()
        self.db.refresh(task)
        return task

    def create_result(self, **values) -> DetectionResult:
        result = DetectionResult(**values)
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
