import speech_recognition as sr
import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))
p.terminate()

init_rec = sr.Recognizer()
print("Let's speak!!")
with sr.Microphone() as source:
    while True:
        audio_data = init_rec.record(source, duration=5)
        print("Recognizing your text.............")
        text = init_rec.recognize_google(audio_data)
        print(text)






def start_recording():
    messages.put(True)
    
    with output:
        display("Starting...")
        record = Thread(target=record_microphone)
        record.start()
        transcribe = Thread(target=speech_recognition, args=(output,))
        transcribe.start()



messages = Queue()
recordings = Queue()


def stop_recording(data):
    with output:
        messages.get()
        display("Stopped.")
    
record_button.on_click(start_recording)
stop_button.on_click(stop_recording)

display(record_button, stop_button, output)
