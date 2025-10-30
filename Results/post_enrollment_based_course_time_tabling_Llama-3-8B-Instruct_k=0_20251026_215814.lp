
% Instance Template
event(Event).

room(Room, Capacity).

timeslot(Day, Hour).

student(Event).

feature(Event, Feature).

room_feature(Room, Feature).

precedence_event(Event1, Event2).

timeslot_event(Event, Timeslot).

% Generator

% 1
1 {{ assigned(Event, Timeslot, Room) : room(Room,_) }} 1 :- event(Event), timeslot(Timeslot).


% Hard Constraints

% Students must not have overlapping events.
:- assigned(Event1, Timeslot1, Room), assigned(Event2, Timeslot1, Room), Event1!= Event2.


% The amount of students in a room at the same time should not exceed the capacity of the room
:- room(Room, Capacity), #count{{Student : student(Student, Event), assigned(Event, Timeslot, Room), timeslot_event(Event, Timeslot)}} > Capacity.


% Rooms must have the required features for the event.
:- assigned(Event, Timeslot, Room), feature(Event, Feature), not room_feature(Room, Feature).


% There must be no more than one event in a room at a time.
:- assigned(Event1, Timeslot, Room), assigned(Event2, Timeslot, Room), Event1!= Event2.


% Events may only be scheduled in designated timeslots.
:- assigned(Event, Timeslot, Room), ~timeslot_event(Event, Timeslot).


% Some events must be scheduled in a specific order.
:- precedence_event(Event1, Event2), timeslot_event(Event1, Timeslot1), timeslot_event(Event2, Timeslot2), Timeslot1!= Timeslot2.




% Soft Constraints

% Students should not have events scheduled in the last timeslot of the day
penalty("LastTimeslot",student(Event),1) :- event(Event), timeslot_event(Event,Timeslot), last_timeslot(Day,Timeslot), student(Event), timeslot(Day,Day).


% Students should not have events scheduled in three or more consecutive timeslots
penalty("ConsecutiveTimeslots",has_consecutive_timeslots(Student),1) :- student(Student), has_event(Student,Timeslot), has_event(Student,Timeslot-1), has_event(Student,Timeslot-2).


% Students should not have exactly one event in a day
student_event_count(Count, Student, Day) :- event(Event), student(Event), #count{{Event : timeslot_event(Event, Timeslot), timeslot(Timeslot, Day)}} = Count.
penalty("SingleEvent", student_event_count(Count, Student, Day), (1-Count)*1) :- student_event_count(Count, Student, Day), Count = 1.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
