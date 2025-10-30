
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
exam(Exam, _, _) :- exam(Exam, _, _).

assigned(Exam, P, R) :- exam(Exam, _, _), period(P, _, _, _, _, _), room(R, _, _).


% Hard Constraints

% No student sits more than one examination at the same time.
:- student(Student, Exam1), student(Student, Exam2), assigned(Exam1, P, _), assigned(Exam2, P, _), Exam1!= Exam2.


% The number of students taking exams in a room at the same time should not exceed the capacity of the room.
:- assigned(Exam1, P, R), assigned(Exam2, P, R), student(Student, Exam1), student(Student, Exam2), room(R, Capacity, _), #count{S : student(S, Exam1), student(S, Exam2)} > Capacity.


% Period Lengths are not violated.
:- assigned(Exam, P1, R1), assigned(Exam, P2, R2), P1!= P2, period(P1, _, _, Duration1, _, _), period(P2, _, _, Duration2, _, _), Duration1 + Duration2 > 1.


% Some exams must be before other exams.
:- assigned(Exam1, P1, _), assigned(Exam2, P2, _), order_constrain(Exam2, Exam1), P1 > P2.


% Some exams must be at the same time as other exams.
:- assigned(Exam1, P1, R1), assigned(Exam2, P2, R2), same_time_constraint(Exam1, Exam2), P1!= P2.


% Some exams must be at a differen time than other exams.
:- assigned(Exam1, P1, R1), assigned(Exam2, P2, R2), different_time_constraint(Exam1, Exam2), P1 = P2, R1 = R2.


% Some exams must take place in a room with no other exams.
:- assigned(Exam1, P, R), assigned(Exam2, P, R), own_room_constraint(Exam1), own_room_constraint(Exam2), Exam1!= Exam2.




% Soft Constraints

% Students should not have more than one exam in the same day
penalty("ExamOverlapDay", exam_overlap_day(Student, Day), 7) :-
    assigned(Exam1, P1, R1),
    assigned(Exam2, P2, R2),
    student(Student, Exam1),
    student(Student, Exam2),
    P1 \= P2,
    P1 < P2,
    P2 - P1 = 1,
    day(P1, Day),
    day(P2, Day).
penalty("ExamOverlapDay", exam_overlap_day(Student, Day), 5) :-
    assigned(Exam1, P1, R1),
    assigned(Exam2, P2, R2),
    student(Student, Exam1),
    student(Student, Exam2),
    P1 \= P2,
    P1 < P2,
    P2 - P1 > 1,
    day(P1, Day),
    day(P2, Day).


% Exams of different lengths should not be scheduled in the same room in the same period
penalty("SameRoomDifferentLength", assigned(Exam1, P, R), 10) :-
    assigned(Exam1, P, R),
    assigned(Exam2, P, R),
    exam(Exam1, L1, _),
    exam(Exam2, L2, _),
    L1!= L2.


% Some periods have associated penalties
penalty("PeriodPenalty",assigned(Exam,P,R),P_penalty) :- exam(Exam,_,_), period(P,_,_,_,_,P_penalty), assigned(Exam,P,R).


% Some rooms have associated penalties
penalty("RoomPenalty",assigned(Exam,P,R),Penalty) :- exam(Exam,_,_), period(P,_,_,_,_,_), room(R,_,Penalty), has_penalty(R).


% Students should not have more than one exam within a spread of 7 periods.
penalty("ExamSpread",exam_spread(Student,Spread),3) :- student(Student,Exam1), student(Student,Exam2), assigned(Exam1,P1,R), assigned(Exam2,P2,R), period(P1,_,_,_,_,_), period(P2,_,_,_,_,_), P1 < P2, P2 - P1 <= Spread, not exam_spread(Student,Spread-1).


% An exam that is large should not be scheduled in a period that is late.
penalty("LateLargeExam", assigned(LargeExam, P, Room), 5) :-
    exam(LargeExam, _, Is_large),
    period(P, _, _, _, Is_late, _),
    Is_large = true,
    Is_late = true,
    LargeExam = Room.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
