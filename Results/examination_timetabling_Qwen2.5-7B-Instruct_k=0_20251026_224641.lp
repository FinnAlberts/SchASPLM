
% Instance Template
exam(Exam, Duration, Is_large).

student(Student, Exam).

period(P, Date, Time, Duration, Is_late, Penalty).

room(R, Capacity, Penalty).

order_constrain(Exam1, Exam2).

same_time_constraint(Exam1, Exam2).

different_time_constraint(Exam1, Exam2).

own_room_constraint(Exam).

% Generator

% 1
{{ exam(Exam, _, _) : exam(Exam, _, _) }} 1 :-
period(P, _, _, _, _, _),
room(R, _, _).

{{ assigned(Exam, P, R) : exam(Exam, _, _) }} 1 :-
period(P, _, _, _, _, _),
room(R, _, _).


% Hard Constraints

% No student sits more than one examination at the same time.
{{ assigned(Exam, P, R) : student(Student, Exam) }} 1 :-
period(P, _, _, _, _, _),
room(R, _, _),
student(Student, Exam).


% The number of students taking exams in a room at the same time should not exceed the capacity of the room.
:- room(R, Capacity, _), assigned(Exam1, P, R), assigned(Exam2, P, R), student(Student, Exam1), student(Student, Exam2), Exam1!= Exam2, #count{{Student : student(Student, Exam1), student(Student, Exam2)}} > Capacity.


% Period Lengths are not violated.
{{ assigned(Exam, P, R) : exam(Exam, _, _) }} 1 :-
period(P, _, _, Duration, _, _),
P = period(_, _, _, Duration_, _, _),
Duration = Duration_.


% Some exams must be before other exams.
{{ assigned(Exam1, P1, _) : order_constrain(Exam1, Exam2), assigned(Exam2, P2, _) }} 1 :-
P1 < P2.


% Some exams must be at the same time as other exams.
{{ assigned(Exam1, P, R) : same_time_constraint(Exam1, Exam2) }}, {{ assigned(Exam2, P, R) : same_time_constraint(Exam1, Exam2) }} 1 :-
same_time_constraint(Exam1, Exam2).


% Some exams must be at a differen time than other exams.
:- assigned(Exam1, P1, R1), assigned(Exam2, P2, R2), different_time_constraint(Exam1, Exam2), P1 = P2, R1 = R2.


% Some exams must take place in a room with no other exams.
:- assigned(Exam1, P, R), assigned(Exam2, P, R), own_room_constraint(Exam1), own_room_constraint(Exam2), Exam1!= Exam2.




% Soft Constraints

% Students should not have more than one exam in the same day
penalty("ConsecutiveExams",consecutive_exams(Student,Day,P1,P2),7) :- assigned(Exam1,Day,P1,R), assigned(Exam2,Day,P2,R), student(Student,Exam1), student(Student,Exam2), P1+1 = P2, P1 < P2.
penalty("NonConsecutiveExams",non_consecutive_exams(Student,Day,P1,P2),5) :- assigned(Exam1,Day,P1,R), assigned(Exam2,Day,P2,R), student(Student,Exam1), student(Student,Exam2), abs(P1-P2) > 1.


% Exams of different lengths should not be scheduled in the same room in the same period
penalty("DifferentLengthExams",same_room_same_period_diff_length(Exam1, Exam2, P, R),10) :-
assigned(Exam1, P, R),
assigned(Exam2, P, R),
exam(Exam1, D1, _),
exam(Exam2, D2, _),
D1 \= D2.


% Some periods have associated penalties
penalty("PeriodPenalty",assigned(Exam,P,R),Penalty) :- period(P,_,_,_,1,_), assigned(Exam,P,R).
penalty("PeriodPenalty",assigned(Exam,P,R),Penalty) :- period(P,_,_,_,Penalty,_), assigned(Exam,P,R), Penalty > 1.


% Some rooms have associated penalties
penalty("RoomPenalty",assigned(Exam,P,R),Penalty) :- exam(Exam,_,_), period(P,_,_,_,_,_), room(R,_,Penalty), has_penalty(R).


% Students should not have more than one exam within a spread of 7 periods.
penalty("ExamSpread",exam_spread(Student, Spread),3) :-
{ { assigned(Exam1, P1, R1) : student(Student, Exam1) } = N1 },
{ { assigned(Exam2, P2, R2) : student(Student, Exam2) } = N2 },
N1 > 0, N2 > 0,
abs(P1 - P2) <= 7,
Spread = P2 - P1.


% An exam that is large should not be scheduled in a period that is late.
penalty("LateLargeExam",assigned(Exam,P,R),(N*5)) :- exam(Exam,_,Is_large), period(P,_,_,_,Is_late,_), Is_large=1, Is_late=1.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
