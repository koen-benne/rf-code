from openai import OpenAI
import os
from config import OPPONENT

def writeBlogGPT(transcription):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "'" + transcription + "'\n\nDit is een automatisch transcript van een Feyenoord-" + OPPONENT + " wedstrijd. Mogelijk kloppen sommige woorden en interpunctie niet. Verbeter de tekst."
            }
        ],
        model="gpt-3.5-turbo",
    )

    corrected_transcript = chat_completion.choices[0].message.content

    # print("Corrected transcript: " + corrected_transcript)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "'" + corrected_transcript + "'\n\nBeschrijft dit een relevant moment van de wedstrijd? Antwoord alleen ja of nee."
            }
        ],
        model="gpt-3.5-turbo",
    )

    if "ja" in chat_completion.choices[0].message.content.lower():
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "'" + corrected_transcript + "'\n\nLeg uit wat er gebeurt in dit fragment van een transcript van de wedstrijd tussen Feyenoord en " + OPPONENT + "."
                }
            ],
            model="gpt-3.5-turbo",
        )

        print(chat_completion.choices[0].message.content)
