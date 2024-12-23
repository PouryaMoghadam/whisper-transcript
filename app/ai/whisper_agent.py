import torch
import whisper

from app.platform.config import Config
from app.utils.logger import logger

LANG = Config.LANG
WHISPER_MODEL = Config.WHISPER_MODEL
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # Ensure using GPU if available
cache_dir = Config.CACHE_DIR  # Cache directory for caching models

def transcribe_with_whisper(audio):
    logger.debug(
        "Starting transcription with Whisper model: %s on device: %s",
        WHISPER_MODEL,
        device,
    )

    try:
        # Load the Whisper model (will automatically use GPU if available)
        model = whisper.load_model(WHISPER_MODEL, device=device)  # Use Whisper's built-in model loading
        logger.debug(f"Using model: {WHISPER_MODEL} on device: {device}")

        # Transcription in "perform" mode (optimized for speed)
        result = model.transcribe(audio, language=LANG, fp16=False)  # Disable FP16 for more stable performance

        logger.debug("Completed transcription")
        return result['text']

    except Exception as error:
        logger.exception(f"Error during transcription: {str(error)}")
        return f"Server Error"
