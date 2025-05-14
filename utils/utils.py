import re
import json

def extract_json(string):
    # Regular expression to match JSON objects
    json_regex = r"\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}"

    # Find all JSON objects in the text
    matches = re.findall(json_regex, string)


    for match in matches:
        try:
            # Replace standalone None with "None", but leave "None" unchanged
            match = re.sub(r'(?<!")\bNone\b(?!")', '"None"', match)
            # Convert the extracted JSON string to a Python dictionary
            json_data = json.loads(match)
            
        except json.JSONDecodeError:
            print("Did not find JSON.")
            return "no json found"
    
    return json_data