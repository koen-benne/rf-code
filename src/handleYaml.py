import yaml
from config import OPPONENT

def loadYaml(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            if data is None:
                return []
            return data
    except FileNotFoundError:
        return []

def addEntry(entry, file):
    data = loadYaml(file)

    data.append(entry)

    with open(file, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
    print(f"Added new entry: {entry}")

def processTranscriptionFiles(file_name):
    data = loadYaml(file_name)
    return [f"{key}:{value}" for key, value in data.items()]

def getKeywords():
    feyenoord_keywords = processTranscriptionFiles("keywords-feyenoord.yaml")
    opponent_keywords = processTranscriptionFiles(f"keywords-{OPPONENT.lower()}.yaml")
    return feyenoord_keywords + opponent_keywords

def getReplacements():
    feyenoord_replacements = processTranscriptionFiles("replacements-feyenoord.yaml")
    opponent_replacements = processTranscriptionFiles(f"replacements-{OPPONENT.lower()}.yaml")
    return feyenoord_replacements + opponent_replacements
