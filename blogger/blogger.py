from summarizer import start, stop
import pyaudio

def on_output(output):
    print(output)

def main():
    p = pyaudio.PyAudio()
    index = p.get_default_output_device_info().get('index')
    start(on_output, "audio.mp3")

    # start(on_output, "audio.mp3")
    input("Press Enter to stop the program...")
    stop()

if __name__ == "__main__":
    main()

