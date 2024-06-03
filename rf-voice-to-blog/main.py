import threading
from blogger import writeBlog, writeBlogGPT
from threads import streamThread
from config import API_KEY, MIN_TRANSCRIPT_LENGTH, DEBUG_TRANSCRIPTION
from getData import getKeywords, getReplacements

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)

def main():
    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        # STEP 2: Create a websocket connection to Deepgram
        dg_connection = deepgram.listen.live.v("1")

        currentTranscription = []
        completed = False

        def completeTranscription():
            if currentTranscription == []:
                return
            transcription = " ".join(currentTranscription)
            currentTranscription.clear()
            if len(transcription.split()) < MIN_TRANSCRIPT_LENGTH:
                return
            blogThread = threading.Thread(target=writeBlogGPT, args=(transcription,))
            blogThread.start()

        # Event handler for receiving messages from deepgram
        def on_message(self, result, **kwargs):
            nonlocal completed
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
            print(sentence)
            currentTranscription.append(sentence)

        # Event handler for receiving metadata from deepgram
        def on_metadata(self, metadata, **kwargs):
            print(f"\n\n{metadata}\n\n")

        # Event handler for receiving errors from deepgram
        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

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

        # Lock and a flag for thread synchronization
        lock_exit = threading.Lock()
        exit = False

        # Start audio stream thread
        myHttp = threading.Thread(target=streamThread, args=(dg_connection, lock_exit, exit))
        myHttp.start()

        # Wait for user input to stop recording
        input("Press Enter to stop recording...\n\n")

        # Set the exit flag to True to stop the thread
        lock_exit.acquire()
        exit = True
        lock_exit.release()

        print("Stopping...")

        myHttp.join()
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return


if __name__ == "__main__":
    main()
