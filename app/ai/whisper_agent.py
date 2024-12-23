from concurrent.futures import ThreadPoolExecutor

import torch
import whisper

from app.platform.config import Config
from app.utils.logger import logger

LANG = Config.LANG
WHISPER_MODEL = Config.WHISPER_MODEL
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # Ensure using GPU if available
cache_dir = Config.CACHE_DIR  # Cache directory for caching models

model = None
executor = ThreadPoolExecutor(max_workers=2)

def load_model():
    global model
    if model is None:
        logger.debug(f"Loading model {WHISPER_MODEL} on device: {device}")
        model = whisper.load_model(WHISPER_MODEL, device=device)
        logger.debug(f"Model {WHISPER_MODEL} loaded successfully")
    return model

def transcribe_with_whisper(audio):
    logger.debug(
        "Starting transcription with Whisper model: %s on device: %s",
        WHISPER_MODEL,
        device,
    )

    try:
        # Load the model once and reuse it for all requests
        processor_model = load_model()

        # Transcription in "perform" mode (optimized for speed)
        result = processor_model.transcribe(audio, language=LANG, fp16=False)  # Disable FP16 for more stable performance

        logger.debug("Completed transcription")
        return result['text']

    except Exception as error:
        logger.exception(f"Error during transcription: {str(error)}")
        return f"Server Error"

def handle_transcription_request(audio):
    """
    This function will be called for each API request.
    Each API call will handle a separate transcription request.
    """
    # Submit transcription task to the thread pool
    future = executor.submit(transcribe_with_whisper, audio)

    # Wait for the result (this can be non-blocking if you don't want to wait)
    return future.result()