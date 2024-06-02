import os
import httpx
import threading
import subprocess
import pyaudio
import yaml
from blogger import writeBlog, writeBlogGPT

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)

URL = "http://d2e9xgjjdd9cr5.cloudfront.net/icecast/rijnmond/radio-mp3"

API_KEY = os.getenv("DEEPGRAM_API_KEY")

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
            print(sentence)

        def on_metadata(self, metadata, **kwargs):
            print(f"\n\n{metadata}\n\n")

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        # STEP 4: Register the event handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        def getKeywords():
            with open("keywords.yaml", "r") as file:
                return yaml.safe_load(file)

        def getReplacements():
            with open("replacements.yaml", "r") as file:
                object = yaml.safe_load(file)
                return [f"{key}:{value}" for key, value in object.items()]


        # STEP 5: Configure Deepgram options for live transcription
        options = LiveOptions(
            model="nova-2",
            language="nl",
            encoding="linear16",
            sample_rate=44100,
            channels=1,
            smart_format=True,
            keywords=getKeywords(),
            replace=getReplacements(),
        )

        # STEP 6: Start the connection
        dg_connection.start(options)

        # STEP 7: Create a lock and a flag for thread synchronization
        lock_exit = threading.Lock()
        exit = False

        # STEP 8: Define a thread that streams the audio and sends it to Deepgram
        def streamThread():
            with httpx.stream("GET", URL) as r:
                for data in r.iter_bytes():
                    lock_exit.acquire()
                    if exit:
                        break
                    lock_exit.release()

                    dg_connection.send(data)

        def fileStreamThread():
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            output=True)

            # Use ffmpeg to decode MP3 data on-the-fly
            process = subprocess.Popen(
                ['ffmpeg', '-i', '../audio.mp3', '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', '-'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )


            while True:
                data = process.stdout.read(1024)
                if not data:
                    break

                lock_exit.acquire()
                if exit:
                    break
                lock_exit.release()

                dg_connection.send(data)  # Send raw PCM data
                stream.write(data)  # Write data to PyAudio stream for playback

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Ensure the ffmpeg process is properly terminated
            process.stdout.close()
            process.wait()

        # STEP 9: Start the thread
        # myHttp = threading.Thread(target=streamThread)
        myHttp = threading.Thread(target=fileStreamThread)
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
