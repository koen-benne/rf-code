import threading
from blogger import writeBlog, writeBlogGPT
from threads import streamThread, fileStreamThread
from config import API_KEY
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
            transcription = " ".join(currentTranscription)
            print(transcription)
            blogThread = threading.Thread(target=writeBlogGPT, args=(transcription,))
            blogThread.start()

        # STEP 3: Define the event handlers for the connection
        def on_message(self, result, **kwargs):
            nonlocal completed
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                if completed:
                    return
                completed = True
                completeTranscription()
                return
            completed = False
            currentTranscription.append(sentence)

        def on_metadata(self, metadata, **kwargs):
            print(f"\n\n{metadata}\n\n")

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        # STEP 4: Register the event handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        # STEP 5: Configure Deepgram options for live transcription
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

        # STEP 6: Start the connection
        dg_connection.start(options)

        # STEP 7: Create a lock and a flag for thread synchronization
        lock_exit = threading.Lock()
        exit = False

        # STEP 9: Start the thread
        # myHttp = threading.Thread(target=streamThread)
        myHttp = threading.Thread(target=fileStreamThread, args=(dg_connection, lock_exit, exit))
        myHttp.start()

        # STEP 10: Wait for user input to stop recording
        input("Press Enter to stop recording...\n\n")

        # STEP 11: Set the exit flag to True to stop the thread
        lock_exit.acquire()
        exit = True
        lock_exit.release()

        # STEP 12: Wait for the thread to finish
        myHttp.join()

        # STEP 13: Close the connection to Deepgram
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return


if __name__ == "__main__":
    main()
