import os
from tempfile import NamedTemporaryFile

from fastapi import HTTPException

from app.platform.config import Config
from .logger import logger

AUDIO_EXTENSIONS = Config.AUDIO_EXTENSIONS
VIDEO_EXTENSIONS = Config.VIDEO_EXTENSIONS
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS


def validate_extension(filename, allowed_extensions: dict):
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in allowed_extensions:
        logger.info("Received file upload request: %s", filename)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension for file {filename} . Allowed: {allowed_extensions}",
        )


def validate_audio_extension(filename):
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in AUDIO_EXTENSIONS:
        return False


def check_file_extension(file, audio_only: bool = False):
    if audio_only:
        need_convert = validate_audio_extension(file)
        return need_convert
    else:
        validate_extension(file, ALLOWED_EXTENSIONS)


def save_temporary_file(temporary_file, original_filename):
    _, original_extension = os.path.splitext(original_filename)

    temp_filename = NamedTemporaryFile(
        suffix=original_extension, delete=False, dir=Config.CUSTOM_TMP_ADDRESS
    ).name

    with open(temp_filename, "wb") as dest:
        dest.write(temporary_file.read())

    return temp_filename
