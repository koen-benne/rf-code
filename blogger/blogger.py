import os
from openai import OpenAI

def writeBlogs(summary, opponent, choiceAmt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    chatCompletion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Je bent een partijdige verslaggever voor Feyenoord die tijdens de wedstrijd van Feyenoord-" + opponent + " kleine teksten schrijft over de wedstrijd. Doe dit op basis van de volgende informatie:\n\n" + summary,
            }
        ],
        model="gpt-3.5-turbo",
    )
    # get the first [choiceAmt] choices
    choices = chatCompletion.choices[:choiceAmt]
    # map choices to list of message.content
    return [choice.message.content for choice in choices]

