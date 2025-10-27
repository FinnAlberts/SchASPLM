from sched import scheduler
from LLM import bots
import time
import os
import re
import utils.utils as utils
from utils import logger

BASE_DIR = os.path.dirname(__file__)

def read_system_prompt(file_path):
    ''' Read a system prompt from a file.

    Args:
        file_path (str): The path to the file containing the system prompt.

    Returns:
        str: The system prompt as a string.
    '''
    file_path = os.path.join(BASE_DIR, file_path)
    with open(file_path, 'r') as file:
        system_prompt = file.read()
    return system_prompt


def sleep_if_using_remote_clients(pipe, seconds=10):
    """Sleep for `seconds` only if the provided pipe indicates a remote client.

    Remote clients are represented by `pipe is None` (use HF API) or the
    string `'deepseek'` (the Deepseek provider).
    """
    if pipe is None or pipe == 'deepseek':
        time.sleep(seconds)

def get_hard_constraints(hard_constraint_descriptions, problem_description, instance_template, generator, pipe=None, printer=False, k=0, temperature=None, top_p=None, seed=None, max_new_tokens=512):
    ''' Get hard constraints based on their descriptions. Uses different prompts based on the type of constraint.

    Args:
        hard_constraint_descriptions (list): A list of descriptions for each hard constraint.
        problem_description (str): The overall problem description.
        instance_template (str): The instance template generated from the instance description.
        generator (str): The generator generated from the generator description.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.
        printer (bool, optional): Whether to print intermediate results. Defaults to False.
        k (int, optional): The number of retries to get a syntactically correct response. Defaults to 0 (no retries).

    Returns:
        list: A list of hard constraints as strings.
    '''
    # If there are no hard constraints we return None
    if hard_constraint_descriptions is None:
        return None
    
    hard_constraints = []
    print('\n\nHard Constraints\n') if printer else None

    # For every hard constraint description
    for constraint_description in hard_constraint_descriptions:
        # Use the correct hard constraint prompt based on the type of constraint
        if 'type: count' in constraint_description.lower():
            # Remove type: count from the prompt
            constraint_description = constraint_description.replace('type: count', '')
            hard_constraint = get_partial_program(
                system_prompt_path='system_prompts/count_hard_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe,
                k=k,
                printer=printer,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_new_tokens=max_new_tokens
            )
            sleep_if_using_remote_clients(pipe)
        elif 'type: sum' in constraint_description.lower():
            # Remove type: sum from the prompt
            constraint_description = constraint_description.replace('type: sum', '')
            hard_constraint = get_partial_program(
                system_prompt_path='system_prompts/sum_hard_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe,
                k=k,
                printer=printer,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_new_tokens=max_new_tokens
            )
            sleep_if_using_remote_clients(pipe)
        else:
            hard_constraint = get_partial_program(
                system_prompt_path='system_prompts/regular_hard_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe,
                k=k,
                printer=printer,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_new_tokens=max_new_tokens
            )
            sleep_if_using_remote_clients(pipe)
        
        # Append the generated hard constraint to the list
        hard_constraints.append(hard_constraint)

        print(constraint_description + '\n' + hard_constraints[-1]+ '\n') if printer else None
    
    return hard_constraints

# Get Soft Constraints
def get_soft_constraints(soft_constraint_descriptions, problem_description, instance_template, generator, pipe=None, printer=False, k=0, temperature=None, top_p=None, seed=None, max_new_tokens=512):
    ''' Get soft constraints based on their descriptions. Uses different prompts based on the type of constraint.

    Args:
        soft_constraint_descriptions (list): A list of descriptions for each soft constraint.
        problem_description (str): The overall problem description.
        instance_template (str): The instance template generated from the instance description.
        generator (str): The generator generated from the generator description.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.
        printer (bool, optional): Whether to print intermediate results. Defaults to False.
        k (int, optional): The number of retries to get a syntactically correct response. Defaults to 0 (no retries).

    Returns:
        list: A list of soft constraints as strings.
    '''
    # If there are no soft constraints we return None
    if soft_constraint_descriptions is None:
        return None
    
    soft_constraints = []
    print('\nSoft Constraints:\n') if printer else None

    # For every hard constraint description
    for constraint_description in soft_constraint_descriptions:
        # Use the correct soft constraint prompt based on the type of constraint
        if 'type: count' in constraint_description.lower():
            # Remove type: count from the prompt
            constraint_description = constraint_description.replace('type: count', '')
            soft_constraint = get_partial_program(
                system_prompt_path='system_prompts/count_soft_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe,
                k=k,
                printer=printer,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_new_tokens=max_new_tokens
            )
            sleep_if_using_remote_clients(pipe)
        elif 'type: sum' in constraint_description.lower():
            # Remove type: sum from the prompt
            constraint_description = constraint_description.replace('type: sum', '')
            soft_constraint = get_partial_program(
                system_prompt_path='system_prompts/sum_soft_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe,
                k=k,
                printer=printer,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_new_tokens=max_new_tokens
            )
            sleep_if_using_remote_clients(pipe)
        else:
            soft_constraint = get_partial_program(
                system_prompt_path='system_prompts/regular_soft_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe,
                k=k,
                printer=printer,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                max_new_tokens=max_new_tokens
            )
            sleep_if_using_remote_clients(pipe)

        # Append the generated soft constraint to the list
        soft_constraints.append(soft_constraint)

        print(constraint_description + '\n' + soft_constraints[-1]+ '\n') if printer else None
    
    return soft_constraints

def extract_constraints(descriptions, constraints):
    ''' Extract ASP constraints from the LLM output, removing markdown and comments. Also add the description as a comment before each constraint.

    Args:
        descriptions (list): A list of descriptions for each constraint.
        constraints (list): A list of constraints as returned by the LLM.

    Returns:
        str: A string containing all the extracted constraints with descriptions as comments.
    '''
    program = ''
    for i in range(len(descriptions)):
        description = descriptions[i]
        description = description.splitlines()
        description = description[0]
        description = description[2:]
        output = constraints[i]

        output_lines = output.splitlines()
        asp = ''
        for line in output_lines:
            if '```' in line:
                continue
            if '%' in line:
                continue
            else:
                asp += line + '\n'
        
        program += f'''% {description}\n{asp}\n\n'''
    
    return program

def extract_bullet_points(text):
    ''' Extract bullet points from a text block, where main points start with '- ' and can span multiple lines.

    Args:
        text (str): The input text containing bullet points.

    Returns:
        list: A list of strings, each representing a main point with its sub-points.
    '''
    lines = text.split('\n')
    result = []
    current_point = ""

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('- '):  # Main point
            if current_point:  # Save the previous point
                result.append(current_point.strip())
            current_point = stripped_line  # Start a new point
        else:  # Sub-point
            current_point += f"\n {stripped_line}"  # Append to the current point

    if current_point:  # Append the last point
        result.append(current_point.strip())
    
    return result

def extract_descriptions(problem):
    ''' Extract all descriptions from a full problem description.

    Args:
        problem (dict): A dictionary containing the problem descriptions.

    Returns:
        tuple: A tuple containing the extracted descriptions.
    '''

    problem_description = problem['problem_description']
    instance_description = problem['instance_description']
    generator_description = problem['generator_description']
    hard_constraint_descriptions = extract_bullet_points(problem['hard_constraint_descriptions'])
    soft_constraint_descriptions = extract_bullet_points(problem['soft_constraint_descriptions'])
   
    return problem_description, instance_description, generator_description, hard_constraint_descriptions, soft_constraint_descriptions


def check_and_repair_statement_blocks(statement_blocks, prompt, syntax_corrector_bot, k, generation_type, printer=False):
    '''Check syntax for each statement block and attempt to repair using the provided syntax_corrector_bot.

    Args:
        statement_blocks (list): List of ASP statement block strings.
        prompt (str): The original user prompt describing intended semantics (used in repair prompts).
        syntax_corrector_bot (object): Bot to use for repair.
        k (int): Number of retries per statement block.
        printer (bool): Whether to print debug information.

    Returns:
        tuple: (updated_statement_blocks, total_errors)
    '''
    total_errors = 0

    for idx, stmt in enumerate(statement_blocks):
        syntax_error = utils.check_syntax_of_one_string(stmt)
        retries = k  # Number of syntax repair retries left

        if syntax_error:
            # Try to repair the syntax k times
            if printer:
                print("================================================================================")
                print(f'Initial response with syntax error:\n{stmt}\n\nError: {syntax_error}\n')
                print(f" Starting syntax repair attempts...")
                print("================================================================================")

            while retries > 0 and syntax_error and syntax_corrector_bot is not None:
                retries -= 1

                # Create a prompt for repairing the syntax
                repair_prompt = f"Intended semantics:\n{prompt}\n\nErroneous ASP code:\n{stmt}\n\nClingo error message:\n{syntax_error}"
                stmt = syntax_corrector_bot.prompt(repair_prompt)

                if printer:
                    print("--------------------------------------------------------------------------------")
                    print(f'Correction attempt {k - retries}:\n{stmt}\n')

                # Failsafe to correct the bot if it returned multiple statements
                while len(utils.split_ASP_code_into_statement_blocks(stmt)) > 1 and retries > 0:
                    retries -= 1
                    repair_prompt = "The previous response contained multiple statements, which is not allowed. Please provide only one corrected ASP code without any extra explanations."
                    stmt = syntax_corrector_bot.prompt(repair_prompt)

                    if printer:
                        print("--------------------------------------------------------------------------------")
                        print(f'Multiple statement blocks returned by LLM - Correction attempt {k - retries}:\n{stmt}\n')

                # Check the syntax again
                syntax_error = utils.check_syntax_of_one_string(stmt)

                if printer:
                    print("--------------------------------------------------------------------------------")
                    if syntax_error:
                        print(f'Syntax error still present: {syntax_error}\n')
                    else:
                        print(f'Syntax corrected successfully!\n')

        # Replace the original statement with the (possibly) corrected one
        statement_blocks[idx] = stmt

        # Collect metrics (per statement block)
        fix_success = not syntax_error
        if not fix_success:
            total_errors += 1
        # attempts_made = k - retries  # kept locally if later needed

        # Log metrics to logfile, one log line for each statement block.
        # ONLY log if the block is a program statement (not a comment or empty) - for correct metrics.
        if utils.check_if_block_is_program_statement(stmt):
            # generation_type is now required by the logger API and is provided by the caller
            logger.log(generation_type, fix_attempt_count=k - retries, correct_syntax=fix_success)

    return statement_blocks, total_errors

def get_partial_program(system_prompt_path, prompt, system_prompt_variables={}, pipe=None, k=0, printer=False, temperature=None, top_p=None, seed=None, max_new_tokens=512):
    ''' Generate a partial ASP program based on a system prompt and variables.

    Args:
        system_prompt_path (str): The path to the system prompt file.
        prompt (str): The user prompt to send to the LLM for the specific partial program.
        system_prompt_variables (dict): A dictionary containing variables to replace in the system prompt.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.
        k (int, optional): The number of retries to get a syntactically correct response. Defaults to 0 (no retries).
        printer (bool, optional): Whether to print intermediate results. Defaults to False.

    Returns:
        str: The generated partial ASP program as a string.
    '''
    # Total errors for metrics
    total_errors = 0

    # Read the system prompt and replace variables
    system_prompt = read_system_prompt(system_prompt_path)
    
    # Replace variables in the system prompt
    for key, value in system_prompt_variables.items():
        system_prompt = system_prompt.replace(f'<<{key}>>', value)

    # Load the bot and get the response
    asp_generator_bot = bots.load_bot(system_prompt, pipe, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, seed=seed)
    initial_response = [asp_generator_bot.prompt(prompt)]

    # Remove any lines that start with triple backticks (```) - code-fence markers that some LLMs include around code blocks.
    initial_response = [utils.remove_backtick_lines(initial_response[0])]

    # Split the response into separate statement blocks, so each can be syntax checked individually
    statement_blocks = utils.split_ASP_code_into_statement_blocks(initial_response)

    # Create a repair prompt if k > 0
    if k > 0:
        repair_prompt = read_system_prompt('system_prompts/syntax_corrector.txt')

        # Replace variables in the system prompt
        for key, value in system_prompt_variables.items():
            repair_prompt = repair_prompt.replace(f'<<{key}>>', value)

        # Replace remaining variables with None using regex
        repair_prompt = re.sub(r'<<[^<>]*>>', 'None', repair_prompt)

        # Create a new bot for repairing the syntax
        syntax_corrector_bot = bots.load_bot(repair_prompt, pipe, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, seed=seed)
    
    # Determine generation_type for logging based on the system prompt file used. A bit hacky but works for now.
    if 'instance' in system_prompt_path:
        gen_type = 'instance'
    elif 'generator' in system_prompt_path:
        gen_type = 'generator'
    elif 'hard_constraints' in system_prompt_path or 'hard constraints' in system_prompt_path:
        gen_type = 'hard constraints'
    elif 'soft_constraints' in system_prompt_path or 'soft constraints' in system_prompt_path:
        gen_type = 'soft constraints'
    else:
        gen_type = 'unknown'

    # Check syntax of each statement block individually and attempt to fix error
    if k > 0:
        # Use the previously created syntax_corrector_bot to repair statement blocks
        statement_blocks, total_errors = check_and_repair_statement_blocks(
            statement_blocks=statement_blocks,
            prompt=prompt,
            syntax_corrector_bot=syntax_corrector_bot,
            k=k,
            generation_type=gen_type,
            printer=printer
        )
    else:
        # When no repairs are requested, still run a basic syntax check to count errors
        for idx, stmt in enumerate(statement_blocks):
            syntax_error = utils.check_syntax_of_one_string(stmt)
            if syntax_error:
                total_errors += 1

    # All statement blocks have been (attempted to be) fixed, combine them back into one program
    resulting_program_part = '\n'.join(statement_blocks)
    joined_initial_response = '\n'.join(initial_response)

    if printer:
        if(resulting_program_part != joined_initial_response):
            print("####################################################################################")
            print(f"PROGRAM PART WAS REPAIRED {', BUT UN' if total_errors > 0 else ''}SUCCESSFULLY")
            print(f'INITIAL RESPONSE:\n{joined_initial_response}\n\nREPAIRED RESPONSE:\n{resulting_program_part}\n')
            print(f'Total statement blocks: {len(statement_blocks)}\n')
            print(f'Total syntax errors remaining after repair attempts: {total_errors}\n')
            print("####################################################################################")
        else:
            print("####################################################################################")
            print("PROGRAM PART DID NOT NEED REPAIR!")
            print(f'RESPONSE:\n{resulting_program_part}\n')
            print(f'Total statement blocks: {len(statement_blocks)}\n')
            print("####################################################################################")
        
    return(resulting_program_part)

def full_ASP_program(problem, printer=False, pipe=None, k=0, temperature=None, top_p=None, seed=None, max_new_tokens=512):
    ''' Generate a full ASP program based on the problem description.

    Args:
        problem (dict): A dictionary containing the problem descriptions.
        printer (bool, optional): Whether to print intermediate results. Defaults to False.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.
        k (int, optional): The number of retries to get a syntactically correct response. Defaults to 0 (no retries).

    Returns:
        str: The full ASP program as a string.
    '''

    problem_description, instance_description, generator_description, hard_constraint_descriptions, soft_constraint_descriptions = extract_descriptions(problem)

    # Generate an instance template based on instance description (we still provide problem description for the repair prompt)
    instance_template = get_partial_program(
        system_prompt_path='system_prompts/instance.txt',
        prompt=instance_description,
        system_prompt_variables={
            'problem_description': problem_description
        },
        pipe=pipe,
        k=k,
        printer=printer,
        temperature=temperature,
        top_p=top_p,
        seed=seed,
        max_new_tokens=max_new_tokens
    )
    print('Instance Template:\n' + instance_template) if printer else None
    
    # Generate a generator based on generator description and instance template (we still provide problem description for the repair prompt)
    generator = get_partial_program(
        system_prompt_path='system_prompts/generator.txt',
        prompt=generator_description,
        system_prompt_variables={
            'instance_template': instance_template,
            'problem_description': problem_description
        },
        pipe=pipe,
        k=k,
        printer=printer,
        temperature=temperature,
        top_p=top_p,
        seed=seed,
        max_new_tokens=max_new_tokens
    )
    print('\n\nGenerator\n' + generator) if printer else None

    # Generate hard constraints based on hard constraint descriptions, problem description, instance template and generator
    hard_constraints = get_hard_constraints(hard_constraint_descriptions, problem_description, instance_template, generator, pipe=pipe, printer=printer, k=k)

    # Generate soft constraints based on soft constraint descriptions, problem description, instance template and generator
    soft_constraints = get_soft_constraints(soft_constraint_descriptions, problem_description, instance_template, generator, pipe=pipe, printer=printer, k=k)

    # Create a string that contains all hard and soft constraints with descriptions as comments
    hard_constraints_str = extract_constraints(hard_constraint_descriptions, hard_constraints)
    soft_constraints_str = extract_constraints(soft_constraint_descriptions, soft_constraints)
    
    # Combine everything into a full ASP program
    full_program = f'''
{instance_template}

% Generator

{generator}\n

% Hard Constraints

{hard_constraints_str}

% Soft Constraints

{soft_constraints_str}

% Objective function
#minimize {{ Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }}.
'''

    return full_program