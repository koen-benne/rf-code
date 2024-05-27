# TODO's: better error handling, separating functionality into modules, less global variables, better exit strategy

import sys
import tty
import termios
import json
import requests
from vosk import Model, KaldiRecognizer
from threading import Thread
from queue import Queue
import pyaudio
from pydub import AudioSegment
from io import BytesIO

CHANNELS = 1
FRAME_RATE = 16000
RECORD_SECONDS = 10
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_SIZE = 2
PRINT_OUTPUT = True
WRITE_AUDIO = True
RADIO_URL = "http://d2e9xgjjdd9cr5.cloudfront.net/icecast/rijnmond/radio-mp3"
USE_EXAMPLE_AUDIO = True
EXAMPLE_AUDIO_FILE = "audio.mp3"

model = Model(model_name = "vosk-model-nl-spraakherkenning-0.6")
rec = KaldiRecognizer(model, FRAME_RATE)
# Use this confidence level to filter out bad transcriptions or make blog posts more accurate
rec.SetWords(True)

messages = Queue()
recordings = Queue()

output = []

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

def load_online_radio(url):
    response = requests.get(url, stream=True)
    return response

def process_audio_block(block):
    try:
        pcm_block = AudioSegment.from_mp3(BytesIO(block))
        pcm_block = pcm_block.set_channels(CHANNELS).set_frame_rate(FRAME_RATE).set_sample_width(SAMPLE_SIZE)

        return pcm_block.raw_data

    except Exception as e:
        print(e)

def consume_audio_data(chunk_size, frames, data_source):
    segment_duration = int((FRAME_RATE * RECORD_SECONDS) / chunk_size)  # Duration of segments in chunks

    stream = None
    p = None
    if WRITE_AUDIO:
        stream, p = setup_audio_stream()

    try:
        for block in data_source(chunk_size):
            if messages.empty():
                break

            frames.append(block)

            if len(frames) >= segment_duration:
                audio = process_audio_block(b''.join(frames.copy()))
                recordings.put(audio)
                frames.clear()
                if stream:
                    stream.write(audio)

    except Exception as e:
        print(e)

    finally:
        if WRITE_AUDIO:
            close_audio_stream(stream, p)

def radio_stream_generator(chunk_size):
    """Generates blocks of audio data from the radio stream."""
    radio_stream = load_online_radio(RADIO_URL)
    for block in radio_stream.iter_content(chunk_size=chunk_size):
        yield block

def file_stream_generator(chunk_size):
    """Generates blocks of audio data from an audio file."""
    with open(EXAMPLE_AUDIO_FILE, "rb") as f:
        while True:
            block = f.read(chunk_size)
            if not block:
                break
            yield block

def audio_stream_consumer(chunk_size, frames):
    consume_audio_data(chunk_size, frames, radio_stream_generator)

def audio_file_consumer(chunk_size, frames):
    consume_audio_data(chunk_size, frames, file_stream_generator)

def record_radio(chunk_size=20000):

    frames = []

    # Start audio stream consumer thread
    audio_consumer_thread = Thread(target=audio_stream_consumer, args=(chunk_size, frames))
    audio_consumer_thread.start()
    audio_consumer_thread.join()


def speech_recognition(output):
    while not messages.empty():
        audio = recordings.get()
        if rec.AcceptWaveform(audio):
            result = json.loads(rec.Result())
            output.append(result["text"])
            if PRINT_OUTPUT:
                print(result["text"])

def start_recording():
    messages.put(True)

    print("Starting...")
    record = Thread(target=record_radio)
    record.start()
    transcribe = Thread(target=speech_recognition, args=(output,))
    transcribe.start()

def stop_recording():
    messages.get()
    print("Stopped.")

# Function to get a single character from the user
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Function to quit the program
def on_close():
    stop_recording()
    print("\nExiting...")
    sys.exit(0)


# Entry point of the program
if __name__ == "__main__":
    start_recording()

    try:
        while True:
            # Get a single character from the user
            char = getch()
            if char == 'q':
                on_close()

    except KeyboardInterrupt:
        on_close()
