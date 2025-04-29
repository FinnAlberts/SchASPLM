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

# Get Generator
def get_generator(prompt, instance_template, pipe=None):
    system_prompt = f'''You are a bot that is tasked with turning textual goal and generator data into a set of Answer Set Programming (ASP) facts.
Given a target goal, you will make an ASP generator that will 

Here is an example of the input you will receive:

```
Here are some example inputs you will receive:
1. An assignment of courses to rooms, days, and periods such that all lectures of a course are scheduled to distinct periods.
    - Variables: course, room, day, period
    - Cardinality: N_lectures
2. An assignment of players to teams and positions such that each player is assigned to exactly one team and one position.
    - Variables: player, team, position
3. An assignment of tasks to employees and days. Each employee needs needs to be assigned to a task on each day.
```

The corresponding ASP generator would be:

```
% 1
N_lectures {{ assigned(Course, Room, Day, Period) : room(Room,_), day(Day), period(Period) }} N_lectures :- course(Course,_,N_lectures,_,_).

% 2
1 {{ assigned(Player, Team, Position) : team(Team), position(Position) }} 1 :- player(Player).

% 3
1 {{ assigned(Employee, Task, Day) : task(Task) }} 1 :- employee(Employee), day(Day).
```

Below is a template of an instace for your problem, you may use the predicates and variables to construct your generator:
```
{instance_template}
```

Please provide only the generator in the same format as the example and without any further explanation.
'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

# Get Hard Constraints
def get_hard_constraints(hard_constraint_descriptions, problem_description, instance_template, generator, pipe=None, printer=False):
    # If there are no hard constraints
    if hard_constraint_descriptions is None:
        return None
    
    hard_constraints = []
    print('\n\nHard Constraints\n') if printer else None

    # For every hard constraint description
    for constraint_description in hard_constraint_descriptions:

        # Use the correct hard constraint prompt based on the type of constraint
        if 'type: count' in constraint_description.lower():
            hard_constraint =  get_count_hard_constraints(constraint_description, problem_description, instance_template, generator, pipe)
            time.sleep(10)
        elif 'type: sum' in constraint_description.lower():
            hard_constraint =  get_sum_hard_constraints(constraint_description, problem_description, instance_template, generator, pipe)
            time.sleep(10)
        else:
            hard_constraint =  get_regular_hard_constraints(constraint_description, problem_description, instance_template, generator, pipe)
            time.sleep(10)

        hard_constraints.append(hard_constraint)

        print(constraint_description + '\n' + hard_constraints[-1]+ '\n') if printer else None
    
    return hard_constraints

def get_regular_hard_constraints(prompt, problem_description, instance_template, generator, pipe=None):
    system_prompt = f'''You are a bot that is tasked with turning textual hard constraint data into a set of Answer Set Programming (ASP) facts.
Given a set of constraints, you will turn them into ASP facts.

Here are some example inputs you will receive:
1. All lectures for a course must be scheduled to distinct periods.
2. Lectures from the same curriculum or taught by the same teacher must be scheduled to distinct periods.
3. If an exam is scheduled, another exam cannot be scheduled for two days.
4. Lectures can not be booked in a period where the teacher is unavailable.

The corresponding ASP rules would be:
```
% 1
:- assigned(Course, Room1, Day, Period), assigned(Course, Room2, Day, Period), Room1 != Room2.

% 2
:- assigned(Course1, _, Day, Period), assigned(Course2, _, Day, Period), course(Course1, Teacher, _, _, _), course(Course2, Teacher, _, _, _), Course1 != Course2.
:- assigned(Course1, _, Day, Period), assigned(Course2, _, Day, Period), curriculum(Curriculum, Course1), curriculum(Curriculum, Course2), Course1 != Course2.

% 3

:- assigned(exam, _, Day1), assigned(exam, _, Day+1).
:- assigned(exam, _, Day1), assigned(exam, _, Day+2).

% 4
:- assigned(Course,Teacher,Day,Period), unavailability_constraint(Teacher,Day,Period).
```
{problem_description}

Below is a template of an instance for your problem, you may use the predicates and variables to construct your rule:
```
{instance_template}
{generator}
```

Please provide only the ASP rule in the same format as the example and without any further explanation.

'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

def get_count_hard_constraints(prompt, problem_description, instance_template, generator, pipe=None):
    # Remove the last line (the one that says "type: count")
    lines = prompt.splitlines()
    prompt = "\n".join(lines[:-1])

    system_prompt = f'''You are a bot that is tasked with turning a textual hard constraint description into an Answer Set Programming (ASP) rule.
More specifically, you are to create rules which use and count aggregates.

Here are some example inputs you will receive:
1. The number of students in each course should be less than 50.
2. The number of students in courses should be between 100 and 200.
3. The number of students attending a school should not exceed the limit of the school.
4. The number of students in a school at a specific time should not exceed the limit of the school.


The corresponding ASP rules would be:
```
% 1
:- course(Course, _, _, _), #count{{Student : student(Student, Course)}} >= 50.

% 2
:- course(Course,_,_,_), #count{{Student : student(Student, Course)}} < 100.
:- course(Course,_,_,_), #count{{Student : student(Student, Course)}} > 200.

% 3
:- course(_, School, _), #count{{Student: student(Student, Course), course(Course, School, _)}} > Limit, school(School,Limit).

% 4
:- course(_, School, Time), #count{{Student: student(Student, Course), course(Course, School, Time)}} > Limit, School(School, Limit).
```
Note: For count aggregates, the variables outside the aggregate function act as a "for all", meaning the variable you are counting should never be out there. Otherwise you always count exactly one.

Your problem:
{problem_description}

Below is a template of an instance for your problem, you may use the predicates and variables to construct your rule:
```
{instance_template}
{generator}
```

Please provide only the ASP rule in the same format as the example and without any further explanation.

'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

def get_sum_hard_constraints(prompt, problem_description, instance_template, generator, pipe=None):
    # Remove the last line (the one that says "type: count")
    lines = prompt.splitlines()
    prompt = "\n".join(lines[:-1])

    system_prompt = f'''You are a bot that is tasked with turning a textual hard constraint description into an Answer Set Programming (ASP) rule.
More specifically, you are to create rules which use and sum aggregates.

Here are some example inputs you will receive:
1. The total duration of all exams for a student should be between the minimum and maximum exam time limit.
2. The doctors working a shift together at the hospital should have at least 150 years of experience between them.
3. The total number of hours worked by an employee should not exceed 40 hours per week.
4. The total amount of money assigned to a project should be exactly the allocated budget for that project.


The corresponding ASP rules would be:
```
% 1
:- student(Student, _), #sum{{Duration, Exam:  student(Student, Exam), exam(Exam, _, Duration)}} > MaxTime, timelimits(_, MaxTime).
:- student(Student, _), #sum{{Duration, Exam:  student(Student, Exam), exam(Exam, _, Duration)}} < MinTime, timelimits(MinTime, _).

% 2
:- shift(Shift), #sum{{Exp, Doctor: assigned(Doctor, Shift, _), doctor(Doctor, _, Exp, _)}} < 150.

% 3
:- employee(Employee), time(Week,_,_) #sum{{Hours, Day: assigned(Employee, Day, Hours), time(Week, Day, _)}} > 40.

% 4
:- project(Project), #sum{{Amount, Task: assigned(Project, Task, Amount) }} != Budget, budget(Project, Budget)
```


{problem_description}

Below is a template of an instance for your problem, you may use the predicates and variables to construct your rule:
```
{instance_template}
{generator}
```

Please provide only the ASP rule in the same format as the example and without any further explanation.

'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

# Get Soft Constraints
def get_soft_constraints(soft_constraint_descriptions, problem_description, instance_template, generator, pipe=None, printer=False):
    # If there are no soft constraints
    if soft_constraint_descriptions is None:
        return None
    
    soft_constraints = []
    print('\nSoft Constraints:\n') if printer else None

    # For every hard constraint description
    for constraint_description in soft_constraint_descriptions:

        
        # Use the correct soft constraint prompt based on the type of constraint
        if 'type: count' in constraint_description.lower():
            soft_constraint =  get_count_soft_constraint(constraint_description, problem_description, instance_template, generator, pipe)
        elif 'type: sum' in constraint_description.lower():
            soft_constraint =  get_sum_soft_constraint(constraint_description, problem_description, instance_template, generator, pipe)
        else:
            soft_constraint =  get_regular_soft_constraint(constraint_description, problem_description, instance_template, generator, pipe)

        soft_constraints.append(soft_constraint)

        print(constraint_description + '\n' + soft_constraints[-1]+ '\n') if printer else None
    
    return soft_constraints

# 
def get_regular_soft_constraint(prompt, problem_description, instance_template, generator, pipe=None):
    system_prompt = f'''You are a bot that is tasked with turning textual hard constraint data into a set of Answer Set Programming (ASP) facts.
Given a set of constraints, you will turn them into ASP facts.

Here are some example inputs you will receive:
1 Number of students in a course should be less than or equal to the capacity of the room.
    Penalty: 1 for each student over the capacity.
2 Lectures of a course should be scheduled over a minimum number of days
    Penalty: 5 for each day under the minimum.
3 Lectures in a curriculum should be in adjacent periods.
    Penalty: 2 for each isolated lecture in a curriculum.
4 All lectures of a course should be held in the same room.
    Penalty: 1 for each additional room used beyond the first.

The corresponding ASP rules would be:
```
% 1
penalty("RoomCapacity",assigned(Course,Room,Day,Period),(N_students-Cap)*1) :- assigned(Course,Room,Day,Period), course(Course,_,_,_,N_students), room(Room,Cap), N_students > Cap.

% 2
working_day(Course,Day) :- assigned(Course,_,Day,Period).
penalty("MinWorkingDays",course(Course,N_days,N),(N_days-N)*5) :- course(Course,_,_,N_days,_), N = {{ working_day(Course,Day) }}, N < N_days.

% 3
scheduled_curricula(Curriculum,Day,Period) :- assigned(Course,_,Day,Period), curriculum(Curriculum,Course).
penalty("IsolatedLectures",isolated_lectures(Curriculum,Day,Period),2) :- scheduled_curricula(Curriculum,Day,Period), not scheduled_curricula(Curriculum,Day,Period-1), not scheduled_curricula(Curriculum,Day,Period+1).

% 4
using_room(Course,Room) :- assigned(Course,Room,Day,Period).
penalty("RoomStability",using_room(Course,N),(N-1)*1) :- course(Course,_,_,_,_), N = {{ using_room(Course,R) }}, N > 1.
```

{problem_description}

Below is a template of an instance for your problem, you may use the predicates and variables to construct your rule:
```
{instance_template}
{generator}
```

Please provide only the ASP rule in the same format as the example and without any further explanation.

'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

def get_count_soft_constraint(prompt, problem_description, instance_template, generator, pipe=None):
    system_prompt = f'''You are a bot that is tasked with turning textual hard constraint data into a set of Answer Set Programming (ASP) facts.
Given a set of constraints, you will turn them into ASP facts.

Here are some arbitrary example inputs from different problems:
1 Number of students in a course should be less than or equal to the capacity of the room.
    Penalty: 1 for each student over the capacity.
2 The number of students in a school at a specific time should not exceed the limit of the school.
    Penalty: 1 for each student over the limit.
3 At any given time, there should be exactly as many exams as rooms.
    Penalty: 10 for each exam over the number of rooms.
    Penalty: 5 for each exam under the number of rooms.
4 Surgeons should perform two surgeries per day
    Penalty: 2 for each time a surgeon does not have two surgeries scheduled in a day


The corresponding ASP rules would be:
```
% 1
student_count(Count, Course, Room) :- course(Course, _, _, _, _), room(Room, _), #count{{Student : student(Student, Course), assigned(Course,Room,_,_)}} = Count.
penalty("RoomCapacity",student_count(Count,Course,Room),(Count-Cap)*1) :- student_count(Count,_,Room), room(Room,Cap), Count > Cap.

% 2
student_count(Count, School, Time) :- school(School), course(_, _, Time), #count{{Student:, student(Student, Course), course(Course, Room, Time), room(Room, School)}} = Count.
penalty("SchoolLimit",student_count(Count, School, Time, Limit),(Count-Limit)*1) :- count(Count,School,Time), school(School, Limit), Count > Limit.

% 3
% Note: Please use this solution when we have an interval. Do not use an absolute value function.
exam_count(Count, Time) :- period(Time), #count{{Exam : assigned(Exam,_,_,Time)}} = Count.
room_count(Count, Time) :- period(Time), #count{{Room : assigned(_,_,Room,Time)}} = Count.
penalty("RoomStability",exam_count(ExamCount, Time),(ExamCount-RoomCount)*10) :- exam_count(ExamCount, Time), room_count(RoomCount, Time), ExamCount > RoomCount.
penalty("RoomStability",exam_count(ExamCount, Time),(RoomCount-ExamCount)*5) :- exam_count(ExamCount, Time), room_count(RoomCount, Time), ExamCount < RoomCount.

% 4 
surgery_count(Count, Surgeon, Day) :- surgeon(Surgeon), timeslots(_, _, Day), #count{{surgery: assigned(Surgery, Time, _), timeslots(_, Time, Day), surgery(Surgery, _, Surgeon)}} = Count.
penalty("SameTimeSurgery",surgery_count(Count, Hospital, Time),2) :- surgery_count(Count, Hospital, Time), Count != 2.

```


Your problem:
{problem_description}

Below is a template of an instance for your problem, you may use the predicates and variables to construct your rule:
```
{instance_template}
{generator}
```

Please provide only the ASP rule in the same format as the example and without any further explanation.

'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

def get_sum_soft_constraint(prompt, problem_description, instance_template, generator, pipe=None):
    system_prompt = f'''You are a bot that is tasked with turning textual hard constraint data into a set of Answer Set Programming (ASP) facts.
Given a set of constraints, you will turn them into ASP facts.

Here are some arbitrary example inputs from different scheduling problems:
1 The total duration of all exams for a student should be less than the specified exam time limit.
    Penalty: 1 for each minute that the total is too long.
2 The doctors working a shift together at the hospital should have at least 150 years of experience between them.
    Penalty: 2 for each year of experience too little
3 The total number of hours worked by an employee should not exceed 40 hours per week.
    Penalty: 3 for each hour over the limit.
4 The total amount of money assigned to a project should be exactly 100,000.
    Penalty: 1 for each unit over the budget.
    Penalty: 1 for each unit under the budget.

The corresponding ASP rules would be:
```
% 1 
timesum(TimeSum, Student) :- student(Student, _), #sum{{Duration, Exam: student(Student, Exam), exam(Exam, _, Duration)}} = TimeSum.
penalty("ExamTime", timesum(TimeSum, Student), (TimeSum - Timelimit)*1) :- timesum(TimeSum, Student), timelimit(TimeLimit), TimeSum > TimeLimit.

% 2 
expsum(ExpSum, Shift) :- shift(Shift, _, _), #sum{{Exp, Doctor: assigned(Doctor, Shift, _), doctor(Doctor, _, Exp, _)}} = ExpSum.
penalty("LackOfExperience", expsum(ExpSum, Shift), (150 - ExpSum)*2) :- expsum(ExpSum, Shift), ExpSum < 150.

% 3 
hoursum(HoursSum, Week, Employee) :- employee(Employee, _, _), time(Week,_,_) #sum{{Hours, Day: assigned(Employee, Day, Hours), time(Week, Day, _)}} = HoursSum.
penalty("ExcessHours", hoursum(HoursSum, Week, Employee), (HoursSum - 40)*3) :- hoursum(HoursSum, Group), HoursSum > 40.

% 4 
budgets(BudgetSum, Project) :- project(Project), #sum{{Amount, Task: assigned(Project, Task, Amount) }} = BudgetSum.
penalty("OverBudgetLimit", budgets(BudgetSum, Project), (BudgetSum - 100000) * 1) :- budgets(BudgetSum, Project), BudgetSum > 100000.
penalty("UnderBudgetLimit", budgets(BudgetSum, Project), (100000 - BudgetSum) * 1) :- budgets(BudgetSum, Project), BudgetSum < 100000.
```

{problem_description}

Below is a template of an instance for your problem, you may use the predicates and variables to construct your rule:
```
{instance_template}
{generator}
```

Please provide only the ASP rule in the same format as the example and without any further explanation.

'''
    bot = bots.load_bot(system_prompt, pipe)
    response = bot.prompt(prompt)
    return response

def extract_constraints(descriptions, constraints):
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
        
        program += f'''% {description}
{asp}\n\n'''
    
    return program


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

    # Generate an instance template based on problem description
    instance_template = get_instance(instance_description, pipe=pipe)
    print('Instance Template:\n' + instance_template) if printer else None
    
    # Use problem description and instance template to create a generator for the solution
    generator = get_generator(generator_description, instance_template, pipe=pipe)
    print('\n\nGenerator\n' + generator) if printer else None

    # Use instance and generator to create hard constraints
    hard_constraints = get_hard_constraints(hard_constraint_descriptions, problem_description, instance_template, generator, pipe=pipe, printer=printer)
    
    # Use instance and generator to create soft constraints
    soft_constraints = get_soft_constraints(soft_constraint_descriptions, problem_description, instance_template, generator, pipe=pipe, printer=printer)
    
    hard_constraints_str = extract_constraints(hard_constraint_descriptions, hard_constraints)
    soft_constraints_str = extract_constraints(soft_constraint_descriptions, soft_constraints)
    

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