
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
1 {{ event(Event) :- event(Event) }} 1.
1 {{ assign(Event, Timeslot, Room) : room(Room), timeslot(Timeslot) }} 1 :- event(Event).


% Hard Constraints

% Students must not have overlapping events.
1 {{ assign(Event, Timeslot, Room) : room(Room), timeslot(Timeslot) }} 1 :- student(Student, Event).
:- assign(Event1, Timeslot1, Room1), assign(Event2, Timeslot2, Room2), student(Student), Event1!= Event2, Timeslot1 = Timeslot2, Room1 = Room2.


% The amount of students in a room at the same time should not exceed the capacity of the room
:- room(Room, Capacity), event(Event), #count{{Student: student(Student, Event)} : assign(Event, Timeslot, Room), timeslot(Timeslot)} > Capacity.


% Rooms must have the required features for the event.
:- assign(Event, Timeslot, Room), room_feature(FEATURE, Room), \+ feature_requirement(FEATURE, Event).


% There must be no more than one event in a room at a time.
1 {{ assign(Event1, Timeslot, Room) : room(Room), timeslot(Timeslot) }} 1 :-
assign(Event2, Timeslot, Room), Event1!= Event2.


% Events may only be scheduled in designated timeslots.
1 {{ assign(Event, Timeslot, Room) : timeslot(Timeslot) }} 1 :- event(Event).


% Some events must be scheduled in a specific order.
1 {{ precedence_constraint(EVENT1, EVENT2) : event(EVENT1), event(EVENT2) }} 1 :- precedence_constraint(EVENT1, EVENT2).




% Soft Constraints

% Students should not have events scheduled in the last timeslot of the day
penalty("LastTimeslotConstraint",student(Student,Event),1) :- student(Student,Event), timeslot(Day,Hour), assign(Event,Timeslot,Room), Timeslot = { Day,8 }, N = { student(Student,Event) }, N > 0.


% Students should not have events scheduled in three or more consecutive timeslots
penalty("ConsecutiveTimeslots",student(Student,Event),1) :-
event(Event),
student(Student,Event),
timeslot(Day,Hour),
timeslot(Day,Hour+1),
timeslot(Day,Hour+2),
not assign(Event,Timeslot,Room) :-
assign(Event,(Day,Hour),Room),
assign(Event,(Day,Hour+1),Room),
assign(Event,(Day,Hour+2),Room).


% Students should not have exactly one event in a day
1 {{ assign(Event, Timeslot, Room) : student(Student), event(Event), timeslot(Day, Timeslot), room(Room) }} 1 :- student(Student), event(Event), timeslot(Day, Timeslot), room(Room).
penalty("SingleEventPerDay", single_event_per_day(Student, Day), 1) :-
#count{E: assign(E, T, R), student(Student), event(E), timeslot(Day, T)} = 1, student(Student), timeslot(Day, T).
single_event_per_day(Student, Day) :- student(Student), timeslot(Day, _).




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
