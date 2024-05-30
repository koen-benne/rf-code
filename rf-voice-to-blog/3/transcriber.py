from vosk import Model, KaldiRecognizer, SetLogLevel
import speech_recognition as sr
from shared import messages, recordings
import json
from config import FRAME_RATE, VERBOSE, SAMPLE_SIZE

def speech_recognition(transcriptions):
    if not VERBOSE:
        SetLogLevel(-1)
    # model = Model(model_name = "vosk-model-nl-spraakherkenning-0.6")
    model = Model(model_name = "vosk-model-nl-spraakherkenning-0.6-lgraph")
    rec = KaldiRecognizer(model, FRAME_RATE)
    # Use this confidence level to filter out bad transcriptions or make blog posts more accurate
    rec.SetWords(True)

    while not messages.empty():
        audio = recordings.get()
        if rec.AcceptWaveform(audio):
            result = json.loads(rec.Result())
            text = replace_strings(result["text"])
            transcriptions.append(text)
            if VERBOSE:
                print(text)


def replace_strings(text):
    replacements = [("gemeen es", "Gimenez"), ("santiago", "Santiago")]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def speech_recognition_google(transcriptions):
    init_rec = sr.Recognizer()

    while not messages.empty():
        if not recordings.empty():
            audio = recordings.get()
            audio_data = sr.AudioData(audio, FRAME_RATE, SAMPLE_SIZE)
            text = init_rec.recognize_google(audio_data, language="nl-NL")
            transcriptions.append(text)
            if VERBOSE:
                print(text)
