from gpt4all import GPT4All
from config import OPPONENT
from shared import messages

def generate_blogpost(transcriptions):
    model = GPT4All("wizardlm-13b-v1.2.Q4_0.gguf")
    last_length = 0

    with model.chat_session():
        while not messages.empty():
            current_length = len(transcriptions)
            if current_length < 3 or current_length == last_length:
                continue

            print(transcriptions[-1])
            # response = model.generate(prompt="Jij bent een live blogger voor Feyenoord.\n\nSchrijf een korte blogpost voor tijdens de wedstrijd tegen " + OPPONENT + "gebaseerd op de volgende transcripties:\n\n" + transcriptions[-1],
            #    temp=0)
            # print(response)

            last_length = current_length
