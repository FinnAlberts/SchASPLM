
# Problems from ITC-2007
# https://www.eeecs.qub.ac.uk/itc2007/index_files/competitiontracks.htm

# Examination Timetabling 
# https://www.eeecs.qub.ac.uk/itc2007/examtrack/report/Exam_Track_TechReportv4.0.pdf 

# Examination Timetabling (ET) is a problem that involves assigning a set of exams to a set of timeslots, while satisfying a set of constraints. The problem is defined by the following parameters:

et_consecutive_penalty = 7
et_not_consecutive_penalty = 5
et_different_length_penalty = 10
frontload_penalty = 5
period_spread = 7
period_spread_penalty = 3

et_problem_description = '''
Your problem (Examination Timetabling) is a problem that involves making a schedule for a set of exams.
Each exam needs to be scheduled during a specific period in a specific room. 
It is possible to schedule multiple exams in one room at the same time.
Furthermore, each exam is being taken by a set of students.
'''

et_generator = '''Goal:
An assignment of exams to periods and rooms.
    - Variables: period, room
'''

et_instance = '''
Instance Variables:
- Exams: A set of exams that need to be scheduled.
    - Variables: duration, is_large
- Students: A set of students that are taking a set of exams.
    - Variables: exam
- Periods: A set of periods in which the exams can be scheduled.
    - Variables: date, time, duration, is_late, penalty
- Rooms: A set of rooms in which the exams can be scheduled.
    - Variables: capacity, penalty
- Order_Constrains: A set of constraints that specify the order in which some exams must be scheduled.
    - Variables: exam1, exam2
- Same_Time_Constraints: A set of constraints that specify the exams that must be scheduled at the same time.
    - Variables: exam1, exam2
- Different_Time_Constraints: A set of constraints that specify the exams that must not be scheduled at the same time.
    - Variables: exam1, exam2
- Own_Room_Constraints: A set of constraints that specify the exams that must not be scheduled in a room on their own.
    - Variables: exam
'''

et_hard_constraints = '''- No student sits more than one examination at the same time.
- The number of students taking exams in a room at the same time should not exceed the capacity of the room.
    type: count
- Period Lengths are not violated.
- Some exams must be before other exams.
- Some exams must be at the same time as other exams.
- Some exams must be at a differen time than other exams.
- Some exams must take place in a room with no other exams.
'''

et_soft_constraints = f'''- Students should not have more than one exam in the same day
    Penalty: {et_consecutive_penalty} for two exams in the same day that are in consecutive periods.
    Penalty: {et_not_consecutive_penalty} for two exams in the same day that are not in consecutive periods.
- Exams of different lengths should not be scheduled in the same room in the same period
    Penalty: {et_different_length_penalty} for each exam of different length scheduled in the same room in the same period.
- Some periods have associated penalties
    Penalty: 1 for each time an exam is scheduled in a period with an associated penalty. Weighted by the penalty value of the period.
- Some rooms have associated penalties
    Penalty: 1 for each time an exam is scheduled in a room with an associated penalty. Weighted by the penalty value of the room.
- Students should not have more than one exam within a spread of {period_spread} periods.
    Penalty: {period_spread_penalty} for each time a student has two exams within a spread of periods.
- An exam that is large should not be scheduled in a period that is late.
    Penalty: {frontload_penalty} for each large exam scheduled in a period that is late.
'''


et_problem = {
    'problem_description': et_problem_description,
    'generator_description': et_generator,
    'instance_description': et_instance,
    'hard_constraint_descriptions': et_hard_constraints,
    'soft_constraint_descriptions': et_soft_constraints
}


# Post Enrolment Based Course Timetabling
# https://www.eeecs.qub.ac.uk/itc2007/postenrolcourse/report/Post%20Enrolment%20based%20CourseTimetabling.pdf
# Post Enrolment Based Course Timetabling (PE-CTT) is a problem that involves assigning a set of courses to a set of timeslots and rooms, while satisfying a set of constraints. The problem is defined by the following parameters:

pebctt_problem_description = '''Your problem (Post Enrolment Based Course Timetabling) is a problem that involves making a schedule for a set of events.
In this case, a set of events needs to be schedules into a set of timeslots and a set of rooms.
There are a total of 45 timeslots (9 per day for 5 days).

'''

pebctt_generator = '''
An assignment of events to timeslots and rooms.
    - Variables: timeslot, room
'''

pebctt_instance = '''
- Events: A set of N events.
    - Variables: none
- Rooms: A set of rooms in which the events can be scheduled.
    - Variables: capacity
- Timeslots: A set of timeslots in which the events can be scheduled.
    - Variables: day, hour
- Students: A set of students that are attending a set of events.
    - Variables: event
- Feature Requirements: A set of features which events may have.
    - Variables: feature, event
- Room Features: A set of features which rooms may have.
    - Variables: feature, room
- Precedence Constraints: A set of constraints that specify if some events must be scheduled before other events.
    - Variables: event1, event2
- Timeslot Constraints: A set of constraints for each event that specify the timeslots in which the event can be scheduled.
    - Variables: event, timeslot
'''

pebctt_hard_constraint = '''- Students must not have overlapping events.
- The amount of students in a room at the same time should not exceed the capacity of the room
    type: count
- Rooms must have the required features for the event.
- There must be no more than one event in a room at a time.
- Events may only be scheduled in designated timeslots.
- Some events must be scheduled in a specific order.
'''

pebctt_soft_constraint = '''- Students should not have events scheduled in the last timeslot of the day
    Penalty: 1 for each student with an event in the last timeslot of the day.
- Students should not have events scheduled in three or more consecutive timeslots
    Penalty: 1 for each student with an event in three or more consecutive timeslots.
- Students should not have exactly one event in a day
    Penalty: 1 for each time a student has exactly one event in a day.
    type: count
'''

pebctt_problem = {
    'problem_description': pebctt_problem_description,
    'generator_description': pebctt_generator,
    'instance_description': pebctt_instance,
    'hard_constraint_descriptions': pebctt_hard_constraint,
    'soft_constraint_descriptions': pebctt_soft_constraint
}



# Nurse Rostering Problem Description
# https://sci-hub.se/10.3233/IA-170030


ns_problem_description = '''
In the nurse scheduling problem, a set of nurses is assigned to shifts in a hospital.
Shift types are: morning, afternoon, night, rest, special_rest, and vacation.
All shift types occur once every day.
'''

ns_generator = '''Goal:
An assignment of nurses to shifts_types and days. There must be one assignment for each nurse and each day.
    - Variables: nurse, shift, day
'''

ns_instance = '''
Instance Variables:
- Nurses: A set of numbered nurses.
    - Variables: none
- Days: A set of numbered days.
    - Variables: none
- Shift_types: A set of shifts types that the nurses can be assigned to.
    - Variables: shift_type, duration
- nurse_requirements: Min and max number of nurses required for each shift type.
    - Variables: shift, min, max
- work_requirements: Min and max number of hours each nurse must work.
    - Variables: min, max
- shift_requirements: For each shift type, there is a minimum and maximum number of times a nurse must work this shift. There is also a preferred number of each shift type.
    - Variables: shift_type, min, max, preferred
'''

ns_hard_constraints = '''- Every day, the number of nurses assigned to each shift must be between the specified minimum and maximum
    type: count
- Each nurse must work at least the specified minimum and at most the specified maximum number of hours
    type: sum
- Nurses must have exactly 30 days of vacation.
    type: count
- If a nurse works a night shift, they can not work a morning or afternoon shift the next day
- If a nurse works an afternoon shift, they cannot work a morning shift the next day.
- Each nurse has at least two ordinary rest days for every window of fourteen days
    type: count
- Nurses working on two consecutive nights deserve one special_rest day in addition to the ordinary rest days
- The total number of hours worked by each nurse must be between the specified minimum and maximum
    type: sum
'''

ns_hard_constraints_extra = '''
- For each nurse, the starting time of a shift must be at least 24 hours later than the starting time of their previous shift.
'''
ns_soft_constraints = '''- Nurses work the preferred number of shifts for each shift type
    Penalty: 1 for each shift below the preferred number
    Penalty: 1 for each shift above the preferred number
    type: count
'''


ns_problem = {
    'problem_description': ns_problem_description,
    'generator_description': ns_generator,
    'instance_description': ns_instance,
    'hard_constraint_descriptions': ns_hard_constraints,
    'soft_constraint_descriptions': ns_soft_constraints
}



# Sports Scheduling

sps_problem_description = '''
Sport scheduling is a problem that involves assigning games in a sport leagues between two teams, satisfying a set of constraints. The problem is defined by the following parameters:'''

sps_generator = '''
An assignment of games to pairs of teams, venues and game days.
    - Variables: team1, team2, venue, gameday'''


sps_instance = '''
- Teams: a set of teams that plays in the league
    - Variables: team
- Venues: a set of venues that is available
    - Variables: venues
- Availabilities: A set of dates at which a given venue is available 
    - Variables: venues, dates
    '''

sps_hard_constraints = '''- No team plays each other more than once at different gamedays.
- Every team plays every other team at least once.
- No team plays itself.
'''

sps_soft_constraints='''-Teams should play at the same venue as little as possible.'''



sps_problem= {
    'problem_description': sps_problem_description,
    'generator_description': sps_generator,
    'instance_description': sps_instance,
    'hard_constraint_descriptions': sps_hard_constraints,
    'soft_constraint_descriptions':sps_soft_constraints
    }


all_problems = {
    'examination_timetabling': et_problem,
    'post_enrollment_based_course_time_tabling': pebctt_problem,
    'nurse_scheduling': ns_problem,
    'sports scheduling': sps_problem
}










# original example
# Curriculum Based Course Timetabling 
# https://www.eeecs.qub.ac.uk/itc2007/curriculmcourse/report/curriculumtechreport.pdf
cbctt = '''
Curriculum Based Course Timetabling (CB-CTT) is a problem that involves assigning a set of courses to a set of periods and rooms, while satisfying a set of constraints. The problem is defined by the following parameters:

Goal:
An assignment of courses to rooms, days, and periods such that all lectures of a course are scheduled to distinct periods.
    - Variables: course, room, day, period
    - Amount: N_lectures


Instance Variables:
- Courses: A set of courses that need to be scheduled.
    - Variables: teacher, number of lectures, number of days, number of students
- Rooms: A set of rooms in which the courses can be scheduled.
    - Variables: capacity
- Curricula: A set of curricula, where each curriculum is a set of courses that need to be scheduled in different periods.
    - Variables: courses
- periods: A number of periods in which the courses can be scheduled.
- Days: A set of days in which the courses can be scheduled.
- Unavailabilities: A set of periods on specific days in which a teacher is unavailable.
    - Variables: teachers, days, periods


Hard Constraints:
1. All lectures for a course must be scheduled to distinct periods.
2. Lectures from the same curriculum or taught by the same teacher must be scheduled to distinct periods.
3. Only one lecture can be scheduled in a room at a time.
4. Lectures can not be booked in a period where the teacher is unavailable.

Soft Constraints:
1 Number of students in a course should be less than or equal to the capacity of the room.
    - Penalty: 1 for each student over the capacity.
2 Lectures of a course should be scheduled over a minimum number of days
    - Penalty: 5 for each day under the minimum.
3 Lectures in a curriculum should be in adjacent periods.
    - Penalty: 2 for each isolated lecture in a curriculum.
4 All lectures of a course should be held in the same room.
    - Penalty: 1 for each additional room used beyond the first.
'''



