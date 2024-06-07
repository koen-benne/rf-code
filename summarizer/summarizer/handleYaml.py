import yaml
import os
from .state import opponent

package_dir = os.path.dirname(os.path.abspath(__file__))

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

def processTranscriptionFiles(file_name):
    data = loadYaml(file_name)
    if not data:
        return []
    return [f"{key}:{value}" for key, value in data.items()]

def getKeywords():
    feyenoord_keywords = processTranscriptionFiles(os.path.join(package_dir, "transcription-configs/keywords-feyenoord.yaml"))
    opponent_keywords = processTranscriptionFiles(os.path.join(package_dir, f"transcription-configs/keywords-{opponent.lower()}.yaml"))
    return feyenoord_keywords + opponent_keywords

def getReplacements():
    feyenoord_replacements = processTranscriptionFiles(os.path.join(package_dir, "transcription-configs/replacements-feyenoord.yaml"))
    opponent_replacements = processTranscriptionFiles(os.path.join(package_dir, f"transcription-configs/replacements-{opponent.lower()}.yaml"))
    return feyenoord_replacements + opponent_replacements
