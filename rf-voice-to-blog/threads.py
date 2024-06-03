import httpx
from audio import setup_audio_stream, close_audio_stream, setup_ffmpeg_process, close_ffmpeg_process
from config import RADIO_URL, WRITE_AUDIO

def streamThread(dg_connection, lock_exit, exit):
    with httpx.stream("GET", RADIO_URL) as r:
        for data in r.iter_bytes():
            lock_exit.acquire()
            if exit:
                break
            lock_exit.release()

            dg_connection.send(data)

def fileStreamThread(dg_connection, lock_exit, exit):
    if WRITE_AUDIO:
        stream, p = setup_audio_stream() # Open an audio stream if we want to write the audio to output
    process = setup_ffmpeg_process() # Use ffmpeg to decode MP3 data on-the-fly

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

    if WRITE_AUDIO:
        close_audio_stream(stream, p) # Close the audio stream if it was opened

    close_ffmpeg_process(process)
