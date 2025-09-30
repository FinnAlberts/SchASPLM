from sched import scheduler
from LLM_things import bots
import time
import os

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

def get_hard_constraints(hard_constraint_descriptions, problem_description, instance_template, generator, pipe=None, printer=False):
    ''' Get hard constraints based on their descriptions. Uses different prompts based on the type of constraint.

    Args:
        hard_constraint_descriptions (list): A list of descriptions for each hard constraint.
        problem_description (str): The overall problem description.
        instance_template (str): The instance template generated from the instance description.
        generator (str): The generator generated from the generator description.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.
        printer (bool, optional): Whether to print intermediate results. Defaults to False.

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
                pipe=pipe
            )
            time.sleep(10)
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
                pipe=pipe
            )
            time.sleep(10)
        else:
            hard_constraint = get_partial_program(
                system_prompt_path='system_prompts/regular_hard_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe
            )
            time.sleep(10)
        
        # Append the generated hard constraint to the list
        hard_constraints.append(hard_constraint)

        print(constraint_description + '\n' + hard_constraints[-1]+ '\n') if printer else None
    
    return hard_constraints

# Get Soft Constraints
def get_soft_constraints(soft_constraint_descriptions, problem_description, instance_template, generator, pipe=None, printer=False):
    ''' Get soft constraints based on their descriptions. Uses different prompts based on the type of constraint.

    Args:
        soft_constraint_descriptions (list): A list of descriptions for each soft constraint.
        problem_description (str): The overall problem description.
        instance_template (str): The instance template generated from the instance description.
        generator (str): The generator generated from the generator description.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.
        printer (bool, optional): Whether to print intermediate results. Defaults to False.

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
                pipe=pipe
            )
            time.sleep(10)
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
                pipe=pipe
            )
            time.sleep(10)
        else:
            soft_constraint = get_partial_program(
                system_prompt_path='system_prompts/regular_soft_constraints.txt',
                prompt=constraint_description,
                system_prompt_variables={
                    'problem_description': problem_description,
                    'instance_template': instance_template,
                    'generator': generator
                },
                pipe=pipe
            )
            time.sleep(10)

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

def get_partial_program(system_prompt_path, prompt, system_prompt_variables={}, pipe=None):
    ''' Generate a partial ASP program based on a system prompt and variables.

    Args:
        system_prompt_path (str): The path to the system prompt file.
        system_prompt_variables (dict): A dictionary containing variables to replace in the system prompt.
        prompt (str): The user prompt to send to the LLM for the specific partial program.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.

    Returns:
        str: The generated partial ASP program as a string.
    '''

    # Read the system prompt and replace variables
    system_prompt = read_system_prompt(system_prompt_path)
    
    for key, value in system_prompt_variables.items():
        system_prompt = system_prompt.replace(f'<<{key}>>', value)

    # Load the bot and get the response
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

def full_ASP_program(problem, printer=False, pipe=None):
    ''' Generate a full ASP program based on the problem description.

    Args:
        problem (dict): A dictionary containing the problem descriptions.
        printer (bool, optional): Whether to print intermediate results. Defaults to False.
        pipe (optional): The pipeline to use for the LLM. Defaults to None.

    Returns:
        str: The full ASP program as a string.
    '''

    problem_description, instance_description, generator_description, hard_constraint_descriptions, soft_constraint_descriptions = extract_descriptions(problem)

    # Generate an instance template based on instance description
    instance_template = get_partial_program(
        system_prompt_path='system_prompts/instance.txt',
        prompt=instance_description,
        pipe=pipe
    )
    print('Instance Template:\n' + instance_template) if printer else None
    
    # Generate a generator based on generator description and instance template
    generator = get_partial_program(
        system_prompt_path='system_prompts/generator.txt',
        prompt=generator_description,
        system_prompt_variables={
            'instance_template': instance_template
        },
        pipe=pipe
    )
    print('\n\nGenerator\n' + generator) if printer else None

    # Generate hard constraints based on hard constraint descriptions, problem description, instance template and generator
    hard_constraints = get_hard_constraints(hard_constraint_descriptions, problem_description, instance_template, generator, pipe=pipe, printer=printer)

    # Generate soft constraints based on soft constraint descriptions, problem description, instance template and generator
    soft_constraints = get_soft_constraints(soft_constraint_descriptions, problem_description, instance_template, generator, pipe=pipe, printer=printer)
    
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