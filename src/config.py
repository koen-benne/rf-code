import pyaudio
import os
from datetime import datetime

CHANNELS = 1
FRAME_RATE = 44100
RECORD_SECONDS = 10
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_SIZE = 2
VERBOSE = True
WRITE_AUDIO = True
RADIO_URL = "http://d2e9xgjjdd9cr5.cloudfront.net/icecast/rijnmond/radio-mp3"
USE_EXAMPLE_AUDIO = True
EXAMPLE_AUDIO_FILE = "../audio.mp3"
OPPONENT = "Ajax"
API_KEY = os.getenv("DEEPGRAM_API_KEY")
MIN_TRANSCRIPT_LENGTH = 6
DEBUG_TRANSCRIPTION = False
OUTPUT_FILE_NAME = "output/Feyenoord-" + OPPONENT + "-" + str(datetime.today()) +".yaml"
