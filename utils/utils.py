import re
import json
from clingo.ast import parse_files
import os

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

def extract_line_number_from_error(msg): # FINN: When error on end of line, it gives the next line as error line. Should we handle that? @George
    """
    Try to extract the line number from a Clingo error message.

    Args:
        msg (str): The error message from Clingo.

    Returns:
        int or None: The extracted line number, or None if not found.
    """
    # Example: "Results/CTDeepseek:1:34-41: error: syntax error, unexpected <VARIABLE>"
    # The line nr is between the first and second ":" symbol.
    parts = msg.split(":")
    if len(parts) > 2 and parts[1].isdigit():
        return int(parts[1])
    
    return None

def check_syntax(program: list):
    """
    Parse an entire ASP/Clingo program and collect all syntax errors using Clingo's logger.
    Returns a list of error dictionaries (empty if syntax is correct).

    Args:
        program (list): The ASP/Clingo program to be checked as a list of strings.

    Returns:
        List[Dict]: A list of dictionaries, each containing details about a syntax error.
    """

    # Save the program to a temporary file
    # FINN: This is a bit hacky, but Clingo's parse_files function requires a file. Would parse_string be better? @George
    with open("temp.lp", "w") as f:
        for line in program:
            f.write(line + "\n")

    errors = []
    def collector(_stmt):
        # Not needed here, but required by Clingo API
        pass

    def logger(code, msg):

        line_number = extract_line_number_from_error(msg)
        code_line = program[line_number - 1].strip()

        errors.append({
            "type": str(code).strip(),
            "message": str(msg).strip(),
            "line_number": line_number,
            "code": code_line
        })

    try:
        parse_files(["temp.lp"], collector, logger=logger)
    except RuntimeError as e:
        pass # This error is always generated if an error is found, but not very useful to log "on top".
        # errors.append({"type": "RuntimeError", "message": str(e), "line": None, "col": None})

    # Remove the temporary file
    os.remove("temp.lp")

    return errors

if __name__ == "__main__":
    # Test program
    with open("./testfile.lp", "r") as f:
        program = f.readlines()
        program = [line.replace("\n", "") for line in program]
        program = [line for line in program if line.strip()]

    print(program)

    syntax_errors = check_syntax(program)

    for error in syntax_errors:
        print(error)