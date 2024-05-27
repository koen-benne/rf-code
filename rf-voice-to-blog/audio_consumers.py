from config import RADIO_URL, RECORD_SECONDS, FRAME_RATE, WRITE_AUDIO, EXAMPLE_AUDIO_FILE
from audio import load_online_radio, setup_audio_stream, close_audio_stream, process_audio_block

def consume_audio_data(chunk_size, data_source, messages, recordings):
    segment_duration = int((FRAME_RATE * RECORD_SECONDS) / chunk_size)  # Duration of segments in chunks

    stream = None
    p = None
    frames = []
    if WRITE_AUDIO:
        stream, p = setup_audio_stream()

    try:
        for block in data_source(chunk_size):
            if messages.empty():
                break

            frames.append(block)

            if len(frames) >= segment_duration:
                audio = process_audio_block(b''.join(frames.copy()))
                recordings.put(audio)
                frames.clear()
                if stream:
                    stream.write(audio)

    except Exception as e:
        print(e)

    finally:
        if WRITE_AUDIO:
            close_audio_stream(stream, p)

def radio_stream_generator(chunk_size):
    """Generates blocks of audio data from the radio stream."""
    radio_stream = load_online_radio(RADIO_URL)
    for block in radio_stream.iter_content(chunk_size=chunk_size):
        yield block

def file_stream_generator(chunk_size):
    """Generates blocks of audio data from an audio file."""
    with open(EXAMPLE_AUDIO_FILE, "rb") as f:
        while True:
            block = f.read(chunk_size)
            if not block:
                break
            yield block

def audio_stream_consumer(chunk_size, messages, recordings):
    consume_audio_data(chunk_size, radio_stream_generator, messages, recordings)

def audio_file_consumer(chunk_size, messages, recordings):
    consume_audio_data(chunk_size, file_stream_generator, messages, recordings)
