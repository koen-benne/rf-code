from openai import OpenAI
import os
from config import OPPONENT, OUTPUT_FILE_NAME
import datetime
from handleYaml import addEntry

def writeBlog(transcription):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def promptGpt3_5(prompt):
        chatCompletion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-3.5-turbo",
        )
        return chatCompletion.choices[0].message.content


    correctedTranscript = promptGpt3_5("'" + transcription +\
            "'\n\nDit is een automatisch transcript van een Feyenoord-" + OPPONENT +\
            " wedstrijd. Mogelijk kloppen sommige woorden en interpunctie niet. Verbeter de tekst.")

    relevancy = promptGpt3_5("'" + correctedTranscript +\
            "'\n\nBeschrijft dit een relevant moment van de wedstrijd? Antwoord alleen ja of nee.")

    if "ja" in relevancy.lower():
        summary = promptGpt3_5("'" + correctedTranscript +\
                "'\n\nLeg uit wat er gebeurt in dit fragment van een transcript van de wedstrijd tussen Feyenoord en " +\
                OPPONENT + ".")

        addEntry(
            {
                'timestamp': datetime.datetime.now().isoformat(),
                'summary': summary
            },
            OUTPUT_FILE_NAME
        )

