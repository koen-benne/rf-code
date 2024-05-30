import sys
import tty
import termios
from threading import Thread
from config import USE_EXAMPLE_AUDIO
from audio_consumers import audio_stream_consumer, audio_file_consumer
from blogger import generate_blogpost
from shared import messages
from transcriber import speech_recognition, speech_recognition_google

transcriptions = []

def record_audio(chunk_size=20000):
    if USE_EXAMPLE_AUDIO:
        audio_file_consumer(chunk_size,)
    else:
        audio_stream_consumer(chunk_size,)

def start_recording():
    messages.put(True)

    print("Starting...")
    record = Thread(target=record_audio)
    record.start()
    transcribe = Thread(target=speech_recognition, args=(transcriptions,))
    # transcribe = Thread(target=speech_recognition_google, args=(transcriptions,))
    transcribe.start()
    generate = Thread(target=generate_blogpost, args=(transcriptions,))
    generate.start()

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
