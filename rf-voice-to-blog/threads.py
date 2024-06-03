from audio import setup_audio_stream, close_audio_stream, setup_ffmpeg_process
from config import RADIO_URL, WRITE_AUDIO, EXAMPLE_AUDIO_FILE, USE_EXAMPLE_AUDIO

def streamThread(dg_connection, lock_exit, exit):
    if WRITE_AUDIO:
        stream, p = setup_audio_stream() # Open an audio stream if we want to write the audio to output

    data_source = file_stream_generator if USE_EXAMPLE_AUDIO else radio_stream_generator

    try:
        for data in data_source():
            if not data:
                continue

            lock_exit.acquire()
            if exit:
                break
            lock_exit.release()

            dg_connection.send(data)  # Send raw PCM data
            if stream:
                stream.write(data)  # Write data to PyAudio stream for playback

    finally:
        if WRITE_AUDIO:
            close_audio_stream(stream, p) # Close the audio stream if it was opened


def radio_stream_generator():
    # Generates blocks of audio data from the radio stream.
    with setup_ffmpeg_process(RADIO_URL) as process:
        while True:
            data = process.stdout.read(1024)
            yield data

def file_stream_generator():
    # Generates blocks of audio data from an audio file.
    with setup_ffmpeg_process(EXAMPLE_AUDIO_FILE) as process:
        while True:
            data = process.stdout.read(1024)
            yield data

