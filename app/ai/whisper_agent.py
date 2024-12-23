import threading

import torch
import whisper

from app.platform.config import Config
from app.utils.logger import logger

LANG = Config.LANG
WHISPER_MODEL = Config.WHISPER_MODEL
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # Ensure using GPU if available
cache_dir = Config.CACHE_DIR  # Cache directory for caching models

# Global variable for the model, will be loaded once
model = None
model_lock = threading.Lock()

def load_model():
    global model
    if model is None:
        with model_lock:  # Ensure thread safety while loading the model
            if model is None:  # Double-check if model is still not loaded
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
