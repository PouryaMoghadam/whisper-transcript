import librosa
import numpy as np
from datasets import Audio, Dataset
from transformers import WhisperProcessor, WhisperForConditionalGeneration

from app.platform.config import Config
from app.utils.logger import logger

LANG = Config.LANG
WHISPER_MODEL = Config.WHISPER_MODEL
device = Config.DEVICE
compute_type = Config.COMPUTE_TYPE


async def transcribe_with_whisper(audio):
    logger.debug(
        "Starting transcription with Whisper model: %s on device: %s",
        WHISPER_MODEL,
        device,
    )

    try:
        # Check if the CACHE_DIR environment variable is set
        cache_dir_exists = False
        cache_dir = Config.CACHE_DIR
        model_id = WHISPER_MODEL

        if cache_dir:
            cache_dir_exists = True

        # Load the processor
        if cache_dir_exists:
            processor = WhisperProcessor.from_pretrained(model_id, cache_dir=cache_dir)
        else:
            processor = WhisperProcessor.from_pretrained(model_id)

        # Load the model
        if cache_dir_exists:
            model = WhisperForConditionalGeneration.from_pretrained(
                model_id, cache_dir=cache_dir
            )
        else:
            model = WhisperForConditionalGeneration.from_pretrained(model_id)

        # Model configuration
        forced_decoder_ids = processor.get_decoder_prompt_ids(
            language="en", task="transcribe"
        )

        model.config.forced_decoder_ids = forced_decoder_ids

        if isinstance(audio, (list, np.ndarray)):
            wavform = audio
            sr = 16000
        else:
            wavform, sr = librosa.load(audio, sr=16000)

        audio_dataset = Dataset.from_dict(
            {
                "audio": [
                    {
                        "array": wavform.tolist(),
                        "sampling_rate": sr,
                    }
                ]
            }
        ).cast_column("audio", Audio())

        sample = audio_dataset[0]["audio"]

        input_features = await processor(
            sample["array"],
            sampling_rate=sample["sampling_rate"],
            return_tensors="pt",
        ).input_features

        predicted_ids = model.generate(
            input_features, forced_decoder_ids=forced_decoder_ids
        )
        transcription = await processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )[0]

        logger.debug("Completed transcription")
        return transcription

    except Exception as error:
        logger.exception(f"Error during transcription: {str(error)}")
        return f"Server Error"
