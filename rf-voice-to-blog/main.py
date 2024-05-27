import sys
import tty
import json
import termios
from vosk import Model, KaldiRecognizer
from threading import Thread
from queue import Queue
from config import FRAME_RATE, USE_EXAMPLE_AUDIO, PRINT_OUTPUT
from audio_consumers import audio_stream_consumer, audio_file_consumer

model = Model(model_name = "vosk-model-nl-spraakherkenning-0.6")
rec = KaldiRecognizer(model, FRAME_RATE)
# Use this confidence level to filter out bad transcriptions or make blog posts more accurate
rec.SetWords(True)

messages = Queue()
recordings = Queue()

output = []

def speech_recognition(output):
    while not messages.empty():
        audio = recordings.get()
        if rec.AcceptWaveform(audio):
            result = json.loads(rec.Result())
            output.append(result["text"])
            if PRINT_OUTPUT:
                print(result["text"])

def record_audio(chunk_size=20000):
    if USE_EXAMPLE_AUDIO:
        audio_file_consumer(chunk_size, messages, recordings)
    else:
        audio_stream_consumer(chunk_size, messages, recordings)

def start_recording():
    messages.put(True)

    print("Starting...")
    record = Thread(target=record_audio)
    record.start()
    transcribe = Thread(target=speech_recognition, args=(output,))
    transcribe.start()

    record.join()
    transcribe.join()

def stop_recording():
    messages.get()
    print("Stopped.")

def on_close():
    stop_recording()
    print("\nExiting...")
    sys.exit(0)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


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
