
% Instance Template
event(Event).

room(Room, Capacity).

timeslot(Day, Hour).

student(Student, Event).

feature_requirement(FEATURE, Event).

room_feature(FEATURE, Room).

precedence_constraint(EVENT1, EVENT2).

timeslot_constraint(EVENT, TIMESLOT).

% Generator

% 1
1 { event(Event) :- event(Event) }.
1 { assign(Event, Timeslot, Room) : room(Room), timeslot(Timeslot) } 1 :- event(Event).


% Hard Constraints

% Students must not have overlapping events.
:- student(Student), event(Event1), event(Event2), precedence_constraint(Event1, Event2), timeslot(Timeslot1), timeslot(Timeslot2), Timeslot1 < Timeslot2, assign(Event1, Timeslot1, _), assign(Event2, Timeslot2, _).


% The amount of students in a room at the same time should not exceed the capacity of the room
:- room(Room, Capacity), event(Event), 
#count{ Student : student(Student, Event), assign(Event, Timeslot, Room), timeslot(Timeslot) } > Capacity.


% Rooms must have the required features for the event.
:- assign(Event, Timeslot, Room), room_feature(FEATURE, Room), \+ feature_requirement(FEATURE, Event).


% There must be no more than one event in a room at a time.
1 { assign(Event, Timeslot, Room) : room(Room), timeslot(Timeslot) } 1 :- room(Room), timeslot(Timeslot).


% Events may only be scheduled in designated timeslots.
:- event(Event), timeslot(Timeslot), not timeslot_constraint(Event, Timeslot).


% Some events must be scheduled in a specific order.
1 { precedence_constraint(EVENT1, EVENT2) : event(EVENT1), event(EVENT2) } 1 :- precedence_constraint(EVENT1, EVENT2).




% Soft Constraints

% Students should not have events scheduled in the last timeslot of the day
penalty("LastTimeslotConstraint",student(Student,Event),1) :- student(Student,Event), timeslot(Day,Hour), assign(Event,Timeslot,Room), Timeslot = Hour-1, Hour = 8.


% Students should not have events scheduled in three or more consecutive timeslots
penalty("ConsecutiveTimeslots", student(Student, Event), 1) :-
    event(Event),
    student(Student, Event),
    { timeslot_constraint(Event, Timeslot) : timeslot(Timeslot) } #= 3,
    consecutive_timeslots(Event, Timeslot, Timeslot2, Timeslot3).


% Students should not have exactly one event in a day
penalty("SingleEventPerDay", single_event_per_day(Student, Day), 1) :-
#count{Timeslot : assign(Event, Timeslot, Room), event(Event), student(Student), timeslot(Timeslot), day_of_timeslot(Day)} = 1,
student(Student),
day(Day).




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
