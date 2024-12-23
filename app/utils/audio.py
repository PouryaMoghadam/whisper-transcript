import subprocess
from tempfile import NamedTemporaryFile

from whisper import load_audio
from whisper.audio import SAMPLE_RATE

from app.platform.config import Config
from .files import check_file_extension


def convert_video_to_audio(file):
    temp_filename = NamedTemporaryFile(delete=False, dir=Config.CUSTOM_TMP_ADDRESS).name
    subprocess.call(
        [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists"
            "-i",
            file,
            "-vn",
            "-ac",
            "1",  # Mono audio
            "-ar",
            "16000",  # Sample rate of 16kHz
            "-f",
            "wav",  # Output format WAV
            temp_filename,
        ]
    )
    return temp_filename


def process_audio_file(audio_file):
    if not check_file_extension(audio_file, audio_only=True):
        audio_file = convert_video_to_audio(audio_file)
    return load_audio(audio_file)


def get_audio_duration(audio):
    return len(audio) / SAMPLE_RATE