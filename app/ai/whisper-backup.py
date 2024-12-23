# import librosa
# import numpy as np
# import torch
# from datasets import Audio, Dataset
# from transformers import WhisperProcessor, WhisperForConditionalGeneration
#
# from app.platform.config import Config
# from app.utils.logger import logger
#
# LANG = Config.LANG
# WHISPER_MODEL = Config.WHISPER_MODEL
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# compute_type = Config.COMPUTE_TYPE
#
#
# def transcribe_with_whisper(audio):
#     logger.debug(
#         "Starting transcription with Whisper model: %s on device: %s",
#         WHISPER_MODEL,
#         device,
#     )
#
#     try:
#         cache_dir_exists = False
#         cache_dir = Config.CACHE_DIR
#         model_id = WHISPER_MODEL
#
#         if cache_dir:
#             cache_dir_exists = True
#
#         if cache_dir_exists:
#             processor = WhisperProcessor.from_pretrained(model_id, cache_dir=cache_dir)
#         else:
#             processor = WhisperProcessor.from_pretrained(model_id)
#
#         if cache_dir_exists:
#             model = WhisperForConditionalGeneration.from_pretrained(
#                 model_id, cache_dir=cache_dir
#             )
#         else:
#             model = WhisperForConditionalGeneration.from_pretrained(model_id)
#
#         model.to(device)
#
#         forced_decoder_ids = processor.get_decoder_prompt_ids(
#             language="en", task="transcribe"
#         )
#
#         model.config.forced_decoder_ids = forced_decoder_ids
#
#         # If the input 'audio' is already a waveform, no need to load it again.
#         # We will directly proceed with creating the dataset.
#         if isinstance(audio, (list, np.ndarray)):  # Check if it's a waveform (list or ndarray)
#             wavform = audio
#             sr = 16000  # You can adjust the sample rate if needed
#         else:
#             # If 'audio' is a path, use librosa to load the file
#             wavform, sr = librosa.load(audio, sr=16000)
#
#         # Creating a dataset from the wavform
#         audio_dataset = Dataset.from_dict(
#             {
#                 "audio": [
#                     {
#                         "array": wavform.tolist(),
#                         "sampling_rate": sr,
#                     }
#                 ]
#             }
#         ).cast_column("audio", Audio())
#
#         sample = audio_dataset[0]["audio"]
#
#         input_features = processor(
#             sample["array"],
#             sampling_rate=sample["sampling_rate"],
#             return_tensors="pt",
#         ).input_features
#
#         input_features = input_features.to(device)
#
#         predicted_ids = model.generate(
#             input_features, forced_decoder_ids=forced_decoder_ids
#         )
#         transcription = processor.batch_decode(
#             predicted_ids, skip_special_tokens=True
#         )[0]
#
#         logger.debug("Completed transcription")
#         return transcription
#
#     except Exception as error:
#         logger.exception(f"Error during transcription: {str(error)}")
#         return f"Server Error"
