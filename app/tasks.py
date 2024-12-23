from typing import Any, Dict

from fastapi import Depends
from sqlalchemy.orm import Session

from app.platform.db import get_db_session, handle_database_errors
from .models import Task
from .schemas import ResultTasks, TaskSimple


@handle_database_errors
def add_task_to_db(
    session,
    status,
    task_type,
    language=None,
    task_params=None,
    file_name=None,
    url=None,
    audio_duration=None,
    start_time=None,
    end_time=None,
):
    task = Task(
        status=status,
        language=language,
        file_name=file_name,
        url=url,
        task_type=task_type,
        task_params=task_params,
        audio_duration=audio_duration,
        start_time=start_time,
        end_time=end_time,
    )
    session.add(task)
    session.commit()
    return task.uuid


@handle_database_errors
def update_task_status_in_db(
    identifier: str,
    update_data: Dict[str, Any],
    session: Session = Depends(get_db_session),
):
    task = session.query(Task).filter_by(uuid=identifier).first()
    if task:
        for key, value in update_data.items():
            setattr(task, key, value)
        session.commit()


@handle_database_errors
def get_task_status_from_db(identifier, session: Session = Depends(get_db_session)):
    task = session.query(Task).filter(Task.uuid == identifier).first()
    if task:
        return {
            "status": task.status,
            "result": task.result,
            "metadata": {
                "task_type": task.task_type,
                "task_params": task.task_params,
                "language": task.language,
                "file_name": task.file_name,
                "url": task.url,
                "duration": task.duration,
                "audio_duration": task.audio_duration,
                "start_time": task.start_time,
                "end_time": task.end_time,
            },
            "error": task.error,
        }
    else:
        return None


@handle_database_errors
def get_all_tasks_status_from_db(session: Session = Depends(get_db_session)):
    tasks = []
    columns = [Task.uuid, Task.status, Task.task_type]

    query = session.query(*columns)
    for task in query:
        tasks.append(
            TaskSimple(
                identifier=task.uuid,
                status=task.status,
                task_type=task.task_type,
            )
        )
    return ResultTasks(tasks=tasks)


@handle_database_errors
def delete_task_from_db(identifier: str, session: Session):
    task = session.query(Task).filter(Task.uuid == identifier).first()
    
    if task:
        session.delete(task)
        session.commit()
        return True
    else:
        return False
