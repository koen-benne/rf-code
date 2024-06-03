import yaml
from config import OPPONENT

def load_and_process_yaml(file_name):
    with open(file_name, "r") as file:
        data = yaml.safe_load(file)
    return [f"{key}:{value}" for key, value in data.items()]

def getKeywords():
    feyenoord_keywords = load_and_process_yaml("keywords-feyenoord.yaml")
    opponent_keywords = load_and_process_yaml(f"keywords-{OPPONENT.lower()}.yaml")
    return feyenoord_keywords + opponent_keywords

def getReplacements():
    feyenoord_replacements = load_and_process_yaml("replacements-feyenoord.yaml")
    opponent_replacements = load_and_process_yaml(f"replacements-{OPPONENT.lower()}.yaml")
    return feyenoord_replacements + opponent_replacements
