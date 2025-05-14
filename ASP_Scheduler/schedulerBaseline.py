from LLM_things import bots
import time







# Get instance 
def get_instance(prompt, pipe=None):
    system_prompt = '''You are a bot that is tasked with turning textual instance data into a set of Answer Set Programming (ASP) facts.
You will be given a set of variables and matching constants, and will turn them into ASP facts. 

Here is an example of the input you will receive:

```
Instance Variables:
- Courses: A set of courses that need to be scheduled.
    - Variables: teacher, number of lectures, number of days, number of students
- Rooms: A set of rooms in which the courses can be scheduled.
    - Variables: capacity
- Curricula: A set of curricula, where each curriculum is a set of courses that need to be scheduled in different periods.
    - Variables: courses
- periods: A number of numbered periods in which the courses can be scheduled.
- Days: A set of numbered days in which the courses can be scheduled.
- Unavailabilities: A set of periods on specific days in which a teacher is unavailable.
    - Variables: teachers, days, periods
```

The corresponding ASP facts would be:

```
% Instance Template
course(Course, Teacher, N_lectures, N_days, N_students).

room(Room, Capacity).

curriculum(Curriculum, Course).

period(0 .. N_periods-1).

day(0 .. N_days-1).

unavailability(Teacher, Day, Period).
```

Please provide only the ASP facts in the same format as the example and without any further explanation.
'''

    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response


# Turn bullet points into a list of strings
def extract_bullet_points(text):
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


# Extract all descriptions from a full problem description
def extract_descriptions(problem):

    problem_description = problem['problem_description']
    instance_description = problem['instance_description']
    generator_description = problem['generator_description']
    hard_constraint_descriptions = extract_bullet_points(problem['hard_constraint_descriptions'])
    soft_constraint_descriptions = extract_bullet_points(problem['soft_constraint_descriptions'])
   
    return problem_description, instance_description, generator_description, hard_constraint_descriptions, soft_constraint_descriptions


# Generate a full asp program consisting of and instance template, solution generator, hard constraints, and soft constraints
def full_ASP_program(problem, printer=False, pipe=None):

    problem_description, instance_description, generator_description, hard_constraint_descriptions, soft_constraint_descriptions = extract_descriptions(problem)


    system_prompt = f'''You are a bot that is tasked with writing an answer set program (ASP).
    The problem you need to write an ASP for is the following:
    
    {problem_description}

    Below is a template of an instace for your problem, you may use the predicates and variables to construct your program rules:
    {instance_description}

    The generator is described as follows:
    {generator_description}

    The problem has the following hard constrainst:
    {hard_constraint_descriptions}

    The problem has the following soft constraints:
    {soft_constraint_descriptions}

    Please provide only the ASP rules  without any further explanation.
    '''

    bot = bots.load_bot(" ", pipe)
    response = bot.prompt(system_prompt)
    return response