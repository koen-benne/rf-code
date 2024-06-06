import time
from .audio import setup_audio_stream, close_audio_stream, setup_ffmpeg_process
from .config import FRAME_RATE

def streamThread(dg_connection, lock_exit, exit, audio_path, output_index):
    stream, p = None, None
    if output_index:
        stream, p = setup_audio_stream(output_index) # Open an audio stream if we want to write the audio to output

    is_live = audio_path.startswith("http") or audio_path.startswith("rtmp")  # Check if the audio source is live

    data_source = audio_stream_generator

    try:
        for data in data_source(audio_path):
            lock_exit.acquire()
            if exit:
                break
            lock_exit.release()

            dg_connection.send(data)  # Send raw PCM data
            if stream:
                stream.write(data)  # Write data to PyAudio stream for playback
            elif not is_live:
                # Simulate real-time audio stream
                delay = len(data) / FRAME_RATE
                time.sleep(delay)

    finally:
        if output_index:
            close_audio_stream(stream, p) # Close the audio stream if it was opened


def audio_stream_generator(path):
    # Generates blocks of audio data from the radio stream or audio file
    with setup_ffmpeg_process(path) as process:
        while True:
            data = process.stdout.read(1024)
            if not data:
                break
            yield data


