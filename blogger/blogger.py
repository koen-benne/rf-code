from summarizer import start, stop
import yaml
import pyaudio
from datetime import datetime

OPPONENT = "Ajax"

def loadYaml(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            if data is None:
                return []
            return data
    except FileNotFoundError:
        return []

def addEntry(entry):
    file_name = f"feyenoord-{OPPONENT.lower()}_{datetime.now().strftime('%Y-%m-%d')}.yaml"
    data = loadYaml(file_name)

    data.append(entry)

    with open(file_name, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

def on_output(output):
    addEntry(output)

def main():
    p = pyaudio.PyAudio()
    index = p.get_default_output_device_info().get('index')
    start(OPPONENT, on_output, "audio.mp3", index)
    input("Press Enter to stop the program...")
    stop()


if __name__ == "__main__":
    main()
