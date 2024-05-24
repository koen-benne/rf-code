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

model = Model(model_name = "vosk-model-nl-spraakherkenning-0.6")
rec = KaldiRecognizer(model, FRAME_RATE)
# Use this confidence level to filter out bad transcriptions or make blog posts more accurate
rec.SetWords(True)

messages = Queue()
recordings = Queue()

output = []

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

def audio_stream_consumer(chunk_size, frames):
    p = pyaudio.PyAudio()
    stream = p.open(format=AUDIO_FORMAT,
                    channels=CHANNELS,
                    rate=FRAME_RATE,
                    output=True,
                    frames_per_buffer=chunk_size)

    radio_stream = load_online_radio(RADIO_URL)
    segment_duration = int((FRAME_RATE * RECORD_SECONDS) / chunk_size)  # Duration of segments in chunks

    try:
        for block in radio_stream.iter_content(chunk_size=chunk_size):
            if messages.empty():
                break

            frames.append(block)

            if len(frames) >= segment_duration:
                print("Add frames")
                audio = process_audio_block(b''.join(frames.copy()))
                recordings.put(audio)
                frames.clear()
                if WRITE_AUDIO:
                    stream.write(audio)

    except Exception as e:
        print(e)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def record_radio(chunk_size=20000):

    frames = []

    # Start audio stream consumer thread
    audio_consumer_thread = Thread(target=audio_stream_consumer, args=(chunk_size, frames))
    audio_consumer_thread.start()
    audio_consumer_thread.join()


def speech_recognition(output):
    while not messages.empty():
        frames = recordings.get()
        if rec.AcceptWaveform(frames):
            result = json.loads(rec.Result())
            output.append(result["text"])
            if PRINT_OUTPUT:
                print("\n" + result["text"] + "\n")

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
