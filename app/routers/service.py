import os
from datetime import datetime
from tempfile import NamedTemporaryFile

import requests
from fastapi import APIRouter, BackgroundTasks, Form, Depends
from sqlalchemy.orm import Session

from app.platform.config import Config
from app.platform.db import get_db_session
from app.schemas import Response
from app.services import process_transcribe
from app.tasks import add_task_to_db
from app.utils.audio import process_audio_file, get_audio_duration
from app.utils.files import validate_extension, ALLOWED_EXTENSIONS
from app.utils.logger import logger

service_router = APIRouter(prefix="/service")


@service_router.post("/transcript", tags=["Speech-2-Text"])
def speech_to_text(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    session: Session = Depends(get_db_session),
) -> Response:
    logger.info("Received URL for processing: %s", url)

    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename=" in content_disposition:
            filename = content_disposition.split("filename=")[1].strip('"')
        else:
            filename = os.path.basename(url)

        _, original_extension = os.path.splitext(filename)

        temp_audio_file = NamedTemporaryFile(
            suffix=original_extension, delete=False, dir=Config.CUSTOM_TMP_ADDRESS
        )
        for chunk in response.iter_content(chunk_size=8192):
            temp_audio_file.write(chunk)

    logger.info("File downloaded and saved temporarily: %s", temp_audio_file.name)
    validate_extension(temp_audio_file.name, ALLOWED_EXTENSIONS)

    audio = process_audio_file(temp_audio_file, temp_audio_file.name)
    logger.info("Audio file processed: duration %s seconds", get_audio_duration(audio))

    identifier = add_task_to_db(
        status="processing",
        file_name=temp_audio_file.name,
        audio_duration=get_audio_duration(audio),
        language="en",
        task_type="transcription",
        task_params={
            "url": url,
        },
        start_time=datetime.now(),
        session=session,
    )

    background_tasks.add_task(
        process_transcribe, audio, identifier, "transcription", session
    )

    logger.info("Background task scheduled for processing: ID %s", identifier)
    return Response(identifier=identifier, message="Task queued")
