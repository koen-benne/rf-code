from openai import OpenAI
import os
import re
import datetime
from .state import opponent
from .handleYaml import getFeyenoordLastNames, getOpponentLastNames

def writeSummary(transcription, on_output):
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

    transcription = add_club_to_player(transcription)

    correctedTranscript = promptGpt3_5("'" + transcription +\
            "'\n\nDit is een automatisch transcript van een Feyenoord-" + opponent +\
            " wedstrijd. Mogelijk kloppen sommige woorden en interpunctie niet en is er herhaling. Verbeter de tekst.")

    relevancy = promptGpt3_5("'" + correctedTranscript +\
            "'\n\nBeschrijft dit een relevant moment van de wedstrijd? Antwoord alleen ja of nee.")

    if "ja" in relevancy.lower():
        summary = promptGpt3_5("'" + correctedTranscript +\
                "'\n\nLeg uit wat er gebeurt in dit fragment van een transcript van de wedstrijd tussen Feyenoord en " +\
                opponent + ".")

        output = {
            'timestamp': datetime.datetime.now().isoformat(),
            'summary': summary
        }

        on_output(output)
        client.close()

def add_club_to_player(transcription):
    feyenoord_last_names = getFeyenoordLastNames()
    opponent_last_names = getOpponentLastNames()

    # Construct a translation map for Feyenoord players
    feyenoord_map = {name: f"{name} van Feyenoord" for name in feyenoord_last_names}
    # Construct a translation map for opponent players
    opponent_map = {name: f"{name} van {opponent}" for name in opponent_last_names}
    # Merge both maps
    translation_map = {**feyenoord_map, **opponent_map}
    # Create a regex pattern to match any player name
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, translation_map.keys())) + r')\b')
    # Function to replace names using the translation map
    def translate(match):
        return translation_map[match.group(0)]
    # Use re.sub with the translation function
    result = pattern.sub(translate, transcription)
    return result
