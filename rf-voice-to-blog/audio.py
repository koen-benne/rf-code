import pyaudio
import subprocess
from config import CHANNELS, FRAME_RATE, AUDIO_FORMAT

def setup_audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=AUDIO_FORMAT,
                    channels=CHANNELS,
                    rate=FRAME_RATE,
                    output=True)
    return stream, p

def close_audio_stream(stream, p):
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate()

def setup_ffmpeg_process():
    process = subprocess.Popen(
        ['ffmpeg', '-i', '../audio.mp3', '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', '-'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    return process

def close_ffmpeg_process(process):
    process.stdout.close()
    process.wait()
