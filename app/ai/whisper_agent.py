import threading
from concurrent.futures import ThreadPoolExecutor

import torch
import whisper

from app.platform.config import Config
from app.utils.logger import logger

WHISPER_MODEL = Config.WHISPER_MODEL
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cache_dir = Config.CACHE_DIR

executor = ThreadPoolExecutor(max_workers=1)

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
            else:
                logger.debug(f"Model {WHISPER_MODEL} already loaded")
    return model

def transcribe_with_whisper(audio, lang):
    logger.debug("Starting transcription process...")
    logger.debug(f"Audio file: {audio}")
    logger.debug(f"Language: {lang}")

    try:
        processor_model = load_model()

        result = processor_model.transcribe(audio, language=lang, fp16=False)

        logger.debug("Completed transcription")
        print(result['text'])
        return result['text']

    except Exception as error:
        logger.exception(f"Error during transcription: {str(error)}")
        return f"Server Error"

def handle_transcription_request(audio, lang):
    logger.debug(f"Handling transcription request for audio: {audio} and language: {lang}")
    future = executor.submit(transcribe_with_whisper, audio, lang)
    result = future.result()
    logger.debug(f"Transcription result for request: {result}")
    return result