import yaml
from config import OPPONENT

def getFeyenoordKeywords():
    with open("keywords-feyenoord.yaml", "r") as file:
        return yaml.safe_load(file)

def getOpponentKeywords():
    with open("keywords-" + OPPONENT.lower() + ".yaml", "r") as file:
        return yaml.safe_load(file)

def getFeyenoordReplacements():
    with open("replacements-feyenoord.yaml", "r") as file:
        object = yaml.safe_load(file)
        return [f"{key}:{value}" for key, value in object.items()]

def getOpponentReplacements():
    with open("replacements-" + OPPONENT.lower() + ".yaml", "r") as file:
        object = yaml.safe_load(file)
        return [f"{key}:{value}" for key, value in object.items()]

def getKeywords():
    return getFeyenoordKeywords() + getOpponentKeywords()

def getReplacements():
    return getFeyenoordReplacements() + getOpponentReplacements()
