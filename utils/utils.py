import re
import json
from clingo.ast import parse_files, parse_string
import os
import time

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
    with open("temp.lp", "w", encoding="utf-8") as f:
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

    # Remove the temporary file (including a timeout in case of file locks)
    timeout = 5.0
    deadline = time.time() + timeout
    removed = False
    while time.time() < deadline:
        try:
            os.remove("temp.lp")
            removed = True
            break
        except OSError:
            time.sleep(0.1)

    if not removed:
        print("Could not remove temp.lp within 5 seconds.")
        return errors

    return errors

def check_syntax_string(program: str):
    """
    Parse an ASP/Clingo code block given as a string (may include \n) and collect all syntax errors using Clingo's logger.
    Returns an error string (empty if syntax is correct).

    Args:
        program (str): The ASP/Clingo program to be checked as a single string.
    Returns:
        str: An error message if syntax errors are found, otherwise an empty string.
    """
    # Split the program string into lines
    program_lines = program.splitlines()

    # Use Clingo parse_string to check syntax
    #error = 

def split_ASP_code_into_statement_blocks(code: list):
    """
    Splits ASP code into individual 'statement blocks' based on the presence of a period (.) at the end of each statement.
    Handles multi-line statements and keeps comments. 

    Args:
        code (List[str]): The ASP code as a list of strings (lines).

    Returns:
        List[str]: A list of individual ASP statement blocks (potentially including line breaks in a
                   block, if they syntactically belong together).
    """
    statements = []
    current_parts = []  # collects lines for a multi-line statement

    # Normalize the input: elements in `code` may already contain newlines.
    # Split them into physical lines so we handle each logical line separately
    all_lines = []
    for raw in code:
        if raw is None:
            continue
        parts = raw.split('\n')
        for p in parts:
            all_lines.append(p)

    for raw_line in all_lines:
        # Preserve empty physical lines as '' (they are meaningful for tests)
        line = raw_line.rstrip()

        # Split off the first comment ("%" starts a comment in ASP)
        code_part, sep, comment_part = line.partition('%')
        comment_text = (sep + comment_part).strip() if sep else ''

        # Work on the code portion (may contain multiple dot-terminated statements)
        code_before = code_part

        # Split into segments by single '.' terminators, but ignore any '.' that is adjacent
        # to another '.' (so '..' or '...' sequences are not considered terminators).
        segments = []
        buf = []
        i = 0
        n = len(code_before)
        while i < n:
            ch = code_before[i]
            buf.append(ch)
            if ch == '.':
                prev_is_dot = (i - 1 >= 0 and code_before[i - 1] == '.')
                next_is_dot = (i + 1 < n and code_before[i + 1] == '.')
                # Only treat '.' as terminator when it's not part of a multi-dot sequence
                if not prev_is_dot and not next_is_dot:
                    segments.append(''.join(buf))
                    buf = []
                # otherwise it's part of '..' or '...'; do not terminate here
            i += 1

        tail = ''.join(buf).strip()

        # Process complete dot-terminated segments
        for j, seg in enumerate(segments):
            seg = seg.strip()
            if not seg:
                continue

            # Attach comment only if this is the last segment AND there is a comment on the line
            seg_with_comment = seg
            if (j == len(segments) - 1) and comment_text:
                # ensure spacing before comment
                if not seg_with_comment.endswith(' '):
                    seg_with_comment = seg_with_comment + ' '
                seg_with_comment = seg_with_comment + comment_text

            # If we are currently collecting a multi-line statement, append this segment and finish the block
            if current_parts:
                current_parts.append(seg_with_comment)
                statements.append('\n'.join(current_parts).strip())
                current_parts = []
            else:
                # standalone segment from this line
                statements.append(seg_with_comment)

        # If there is a trailing (non-terminated) piece, it continues onto the next lines
        if tail:
            tail_piece = tail
            # If there was no dot-terminated segment that consumed the line, attach the inline comment to this tail
            if not segments and comment_text:
                if not tail_piece.endswith(' '):
                    tail_piece = tail_piece + ' '
                tail_piece = tail_piece + comment_text
            # If there were dot-terminated segments and the tail exists, the comment should be attached to the tail
            if segments and comment_text and not tail_piece.endswith(comment_text):
                if not tail_piece.endswith(' '):
                    tail_piece = tail_piece + ' '
                tail_piece = tail_piece + comment_text

            # Start or continue collecting a multi-line statement
            if current_parts:
                current_parts.append(tail_piece)
            else:
                current_parts = [tail_piece]

        # If there were no segments and no tail (i.e., the line was just a comment), attach comment to current_parts
        if not segments and not tail and comment_text:
            if current_parts:
                # append comment line to the current statement
                current_parts.append(comment_text)
            else:
                # standalone comment-only line -> treat as its own small statement
                statements.append(comment_text)

        # If the physical line is completely empty (''), preserve it as an empty statement block
        if not segments and not tail and not comment_text and line == '':
            if current_parts:
                current_parts.append('')
            else:
                statements.append('')

    # If anything remains un-terminated, add as a final statement block
    if current_parts:
        statements.append('\n'.join(current_parts).strip())

    # If the input ended with a trailing newline we may have produced an extra
    # empty-string statement at the end. Remove a single trailing '' if present
    # and if it's the only reason the length increased (keeps intentional blank
    # lines in the middle).
    if statements and statements[-1] == '':
        # Only drop it if the original input ended with a newline (common case)
        # Detect by checking if the last element of the provided `code` ends with '\n'
        try:
            last_raw = code[-1]
            if isinstance(last_raw, str) and last_raw.endswith('\n'):
                statements.pop()
        except Exception:
            # If we can't determine, be conservative and keep it
            pass

    # TODO: Minor improvement could be to merge empty lines (\n) with the block before or after.
    # Not very urgent, as the functionality works correctly even with separate empty lines.

    return statements

def check_syntax_of_one_string(code: str):
    """
    Parse an ASP/Clingo statement given as a single string and collect any syntax error using Clingo's logger.
    Returns an error string (empty if syntax is correct).

    Args:
        code (str): The ASP/Clingo statement to be checked as a single string. This should be ONE statement only,
                    possibly spanning multiple lines separated by \n.

    Returns:
        str: An error message if a syntax error is found, otherwise an empty string.
    """

    error_message = ""

    def collector(_stmt):
        # Not needed here, but required by Clingo API
        pass

    def logger(code, msg):
        nonlocal error_message
        #error_message = f"{str(code).strip()}: {str(msg).strip()}"
        error_message = str(msg).strip()

    try:
        parse_string(code, collector, logger=logger)
    except RuntimeError as e:
        pass # This error is always generated if an error is found, but not very useful to log "on top".

    return error_message

if __name__ == "__main__":
    # Test program
    with open("./testfile.lp", "r", encoding='utf-8') as f:
        program = f.readlines()
    print()
    
    statement_blocks = split_ASP_code_into_statement_blocks(program)
    
    # Check syntax of each statement block individually and print statement and whether or not there was an error
    for statement in statement_blocks:
        syntax_error = check_syntax_of_one_string(statement)

        # Add enter before stmt if it's a multi-line statement
        stmt_display = statement
        if '\n' in stmt_display:
            stmt_display = '\n' + statement

        if syntax_error:
            print(f"STATEMENT WITH ERROR: {stmt_display}")
            print('---------------------------')
            print(f"ERROR: {syntax_error}")
        else:
            print(f"STATEMENT OK: {stmt_display}")
        
        print('==============================================')
