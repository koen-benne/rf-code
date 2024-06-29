import os
from openai import OpenAI

def writeBlogs(summary, opponent, choiceAmt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    chatCompletion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Je bent een erg entousiaste, partijdige verslaggever voor Feyenoord die tijdens de wedstrijd van Feyenoord-"\
                        + opponent + " kleine, niet te diepgaande teksten schrijft over de wedstrijd. Bij veelbelovende momenten voor Feyenoord\
                        wordt je erg blij en schrijf je met uitroeptekens.\n\nSchrijf zo een hele korte tekst in weinig en korte,\
                        informele Nederlandse zinnen waarbij de belangrijke aspecten eerst komen. Benoem geen commentatoren. \
                        Doe dit op basis van de volgende korte samenvatting, deze samenvatting kan fouten bevatten:\n\n" + summary,
            }
        ],
        model="gpt-3.5-turbo",
        n=choiceAmt,
    )
    # map choices to list of message.content
    return [choice.message.content for choice in chatCompletion.choices]


