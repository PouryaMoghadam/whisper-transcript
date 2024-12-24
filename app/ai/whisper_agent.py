import threading
from concurrent.futures import ThreadPoolExecutor

import torch
import whisper

from app.platform.config import Config
from app.utils.logger import logger

WHISPER_MODEL = Config.WHISPER_MODEL
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cache_dir = Config.CACHE_DIR

executor = ThreadPoolExecutor(max_workers=2)

model = None
model_lock = threading.Lock()

def load_model():
    global model
    if model is None:
        with model_lock:
            if model is None:
                logger.debug(f"Loading model {WHISPER_MODEL} on device: {device}")
                model = whisper.load_model(WHISPER_MODEL, device=device)
                logger.debug(f"Model {WHISPER_MODEL} loaded successfully")
    return model

def transcribe_with_whisper(audio, lang):
    logger.debug(
        "Starting transcription with Whisper model: %s on device: %s",
        WHISPER_MODEL,
        device,
    )

    try:
        processor_model = load_model()

        result = processor_model.transcribe(audio, language=lang, fp16=True)

        logger.debug("Completed transcription")
        return result['text']

    except Exception as error:
        logger.exception(f"Error during transcription: {str(error)}")
        return f"Server Error"

def handle_transcription_request(audio, lang):
    """
    This function will be called for each API request.
    Each API call will handle a separate transcription request.
    """
    future = executor.submit(transcribe_with_whisper, audio, lang)
    return future.result()