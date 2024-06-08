import threading
from typing import Optional, Callable
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
from .writer import writeSummary
from .threads import streamThread
from .config import API_KEY, MIN_TRANSCRIPT_LENGTH, DEBUG_TRANSCRIPTION, DEFAULT_AUDIO_PATH
from .handleYaml import getKeywords, getReplacements
from .state import opponent, lock_exit, exit_threads

deepgram = None
dg_connection = None
currentTranscription = []
completed = False
transcription_thread = None
summarizer_thread = None
on_output = None

def completeTranscription():
    global currentTranscription, summarizer_thread, on_output
    if currentTranscription == []:
        return
    transcription = " ".join(currentTranscription)
    currentTranscription.clear()
    if len(transcription.split()) < MIN_TRANSCRIPT_LENGTH:
        return
    summarizer_thread = threading.Thread(target=writeSummary, args=(transcription, on_output))
    summarizer_thread.start()

# Event handler for receiving messages from deepgram
def on_message(self, result, **kwargs):
    global completed, on_output
    sentence = result.channel.alternatives[0].transcript

    # If the DEBUG_TRANSCRIPTION flag is set to True, print the transcription and don't write the blog
    if DEBUG_TRANSCRIPTION:
        print(f"Transcription: {sentence}")
    else:
        if len(sentence) == 0:
            if completed:
                return
            completed = True
            completeTranscription()
            return
        completed = False
    currentTranscription.append(sentence)

# Event handler for receiving metadata from deepgram
def on_metadata(self, metadata, **kwargs):
    print(f"\n\n{metadata}\n\n")

# Event handler for receiving errors from deepgram
def on_error(self, error, **kwargs):
    print(f"\n\n{error}\n\n")


def start(opponent_name: str, output_callback: Callable[[str], None], audio_path: str = DEFAULT_AUDIO_PATH, output_index: Optional[int] = None):
    global deepgram, dg_connection, exit, lock_exit, transcription_thread, on_output, opponent

    on_output = output_callback
    opponent = opponent_name

    deepgram = DeepgramClient(API_KEY)
    dg_connection = deepgram.listen.live.v("1")

    # Register the event handlers
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)

    # Configure Deepgram options for live transcription
    options = LiveOptions(
        model="nova-2",
        language="nl",
        encoding="linear16",
        sample_rate=44100,
        channels=1,
        smart_format=True,
        keywords=getKeywords(),
        replace=getReplacements()
    )
    # Start connection
    dg_connection.start(options)

    # Start audio stream thread
    transcription_thread = threading.Thread(target=streamThread, args=(dg_connection, audio_path, output_index))
    transcription_thread.start()

def stop():
    with lock_exit:
        exit_threads()

    print("Stopping...")

    if transcription_thread is not None:
        transcription_thread.join()
    if summarizer_thread is not None:
        summarizer_thread.join()
    dg_connection.finish()

    print("Finished")

