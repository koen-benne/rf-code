import pyaudio
import os
from datetime import datetime

CHANNELS = 1
FRAME_RATE = 44100
RECORD_SECONDS = 10
AUDIO_FORMAT = pyaudio.paInt16
SAMPLE_SIZE = 2
RADIO_URL = "http://d2e9xgjjdd9cr5.cloudfront.net/icecast/rijnmond/radio-mp3"
EXAMPLE_AUDIO_FILE = "../audio.mp3"
API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPPONENT = "Ajax"
OUTPUT_FILE_NAME = "output/Feyenoord-" + OPPONENT + "_" + str(datetime.today()).split()[0] +".yaml"
MIN_TRANSCRIPT_LENGTH = 6

VERBOSE = True
WRITE_AUDIO = True
USE_EXAMPLE_AUDIO = True
DEBUG_TRANSCRIPTION = False
