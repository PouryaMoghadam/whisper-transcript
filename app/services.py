from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.whisper import transcribe_with_whisper
from app.tasks import update_task_status_in_db
from app.utils.logger import logger


def process_transcribe(
    audio,
    identifier,
    task_type: str,
    session: Session,
    *args,
):
    try:
        start_time = datetime.now()
        logger.info(f"Starting {task_type} task for identifier {identifier}")
        
        result = transcribe_with_whisper(audio)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(
            f"Completed {task_type} task for identifier {identifier}. Duration: {duration}s"
        )

        update_task_status_in_db(
            identifier=identifier,
            update_data={
                "status": "completed",
                "result": result,
                "duration": duration,
                "start_time": start_time,
                "end_time": end_time,
            },
            session=session,
        )

    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(
            f"Task {task_type} failed for identifier {identifier}. Error: {str(e)}"
        )
        update_task_status_in_db(
            identifier=identifier,
            update_data={"status": "failed", "error": str(e)},
            session=session,
        )
    except MemoryError as e:
        logger.error(
            f"Task {task_type} failed for identifier {identifier} due to out of memory. Error: {str(e)}"
        )
        update_task_status_in_db(
            identifier=identifier,
            update_data={"status": "failed", "error": str(e)},
            session=session,
        )


def validate_language_code(language_code):
    if language_code not in ["en"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid language code: {language_code}"
        )