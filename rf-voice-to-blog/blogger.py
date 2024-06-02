from gpt4all import GPT4All
from openai import OpenAI
import os

def writeBlog(transcription):
    model = GPT4All("wizardlm-13b-v1.2.Q4_0.gguf")

    response = model.generate(prompt=transcription + "\n\nDit is een automatisch transcript van een Feyenoord-Ajax wedstrijd. Mogelijk kloppen sommige woorden en interpunctie niet. Verbeter de tekst.",
        temp=0)
    print(response)

def writeBlogGPT(transcription):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": transcription + "\n\nDit is een automatisch transcript van een Feyenoord-Ajax wedstrijd. Mogelijk kloppen sommige woorden en interpunctie niet. Verbeter de tekst."
            }
        ],
        model="gpt-3.5-turbo",
    )

    print(chat_completion.choices[0].message['content'])
