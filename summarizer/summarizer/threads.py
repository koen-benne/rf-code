import time
import os
from .audio import setup_audio_stream, close_audio_stream, setup_ffmpeg_process
from .config import FRAME_RATE

def streamThread(dg_connection, audio_path, output_index, on_breaking_error):
    try:
        stream, p = None, None
        if output_index:
            stream, p = setup_audio_stream(output_index) # Open an audio stream if we want to write the audio to output

        is_live = audio_path.startswith("http") or audio_path.startswith("rtmp")  # Check if the audio source is live

        data_source = audio_stream_generator

        for data in data_source(audio_path):
            from .state import lock_exit, exit

            with lock_exit:
                if exit:
                    break

            dg_connection.send(data)  # Send raw PCM data
            if stream:
                stream.write(data)  # Write data to PyAudio stream for playback
            elif not is_live:
                # Simulate real-time audio stream
                delay = len(data) / FRAME_RATE
                time.sleep(delay)
    except FileNotFoundError as e:
        on_breaking_error(str(e))
    except Exception as e:
        print(f"Error in streamThread: {e}")

    finally:
        if output_index:
            close_audio_stream(stream, p) # Close the audio stream if it was opened


def audio_stream_generator(path):
    # Generates blocks of audio data from the radio stream or audio file
    if not path.startswith("http") and not path.startswith("rtmp"):
        # check if the audio file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

    with setup_ffmpeg_process(path) as process:
        while True:
            data = process.stdout.read(1024)
            if not data:
                break
            yield data


