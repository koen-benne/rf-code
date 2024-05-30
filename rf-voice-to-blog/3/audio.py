import pyaudio
import requests
from pydub import AudioSegment
from io import BytesIO
from config import CHANNELS, FRAME_RATE, AUDIO_FORMAT, SAMPLE_SIZE

def load_online_radio(url):
    response = requests.get(url, stream=True)
    return response

def setup_audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=AUDIO_FORMAT,
                    channels=CHANNELS,
                    rate=FRAME_RATE,
                    output=True,
                    frames_per_buffer=10000)
    return stream, p

def close_audio_stream(stream, p):
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate() 

def process_audio_block(block):
    try:
        pcm_block = AudioSegment.from_mp3(BytesIO(block))
        pcm_block = pcm_block.set_channels(CHANNELS).set_frame_rate(FRAME_RATE).set_sample_width(SAMPLE_SIZE)

        return pcm_block.raw_data

    except Exception as e:
        print(e)
