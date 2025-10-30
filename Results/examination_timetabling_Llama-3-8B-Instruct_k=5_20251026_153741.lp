
% Instance Template
exam(Exam, Duration, Is_large).

student(Student, Exam).

period(Date, Time, Duration, Is_late, Penalty).

room(Room, Capacity, Penalty).

order_constraint(Exam1, Exam2).

same_time_constraint(Exam1, Exam2).

different_time_constraint(Exam1, Exam2).

own_room_constraint(Exam).

% Generator

% 1
assigned(Exam, Period, Room) :- exam(Exam,_,_), period(Period), room(Room).


% Hard Constraints

% No student sits more than one examination at the same time.
:- assigned(Exam1, Period, Room), assigned(Exam2, Period, Room), student(Student, Exam1), student(Student, Exam2).


% The number of students taking exams in a room at the same time should not exceed the capacity of the room.
:- room(Room, Capacity, _), #count{ Student : student(Student, Exam), assigned(Exam, _, Room) } > Capacity.


% Period Lengths are not violated.
:- assigned(Exam, Period1, Room), assigned(Exam, Period2, Room), period(Period1, _, Duration, _, _), period(Period2, _, Duration, _, _), Period1!= Period2.


% Some exams must be before other exams.
:- assigned(Exam1, Period1, Room), assigned(Exam2, Period2, Room), order_constraint(Exam1, Exam2), Period1 > Period2.


% Some exams must be at the same time as other exams.
:- same_time_constraint(Exam1, Exam2), assigned(Exam1, Period, Room), assigned(Exam2, Period, Room), Exam1!= Exam2.


% Some exams must be at a differen time than other exams.
:- assigned(Exam1, Period1, _), assigned(Exam1, Period2, _), Period1!= Period2.


% Some exams must take place in a room with no other exams.
:- assigned(Exam1, Period, Room), assigned(Exam2, Period, Room), Exam1!= Exam2.




% Soft Constraints

% Students should not have more than one exam in the same day
penalty("SameDayExams", same_day_exams(Student, Day), 7) :- student(Student, Exam), exam(Exam, _, _), period(Period, _, _, _, _), student(Student, Exam2), exam(Exam2, _, _), period(Period2, _, _, _, _), Period = Period2 - 1; Period = Period2 + 1, Day = Period.

penalty("SameDayExams", same_day_exams(Student, Day), 5) :- student(Student, Exam), exam(Exam, _, _), period(Period, _, _, _, _), student(Student, Exam2), exam(Exam2, _, _), period(Period2, _, _, _, _), Period = Period2, Day = Period.


% Exams of different lengths should not be scheduled in the same room in the same period
Corrected Code:
penalty("ExamLength",exam_length_mismatch(Exam1,Exam2),10) :- 
    assigned(Exam1,Period,Room), 
    assigned(Exam2,Period,Room), 
    exam(Exam1,Duration1), 
    exam(Exam2,Duration2), 
    Duration1 \= Duration2.


% Some periods have associated penalties
penalty("PeriodPenalty", assigned(Exam, Period, Room), Penalty) :- exam(Exam, _, _), period(Period, _, _, _, Penalty), assigned(Exam, Period, Room).


% Some rooms have associated penalties
penalty("RoomPenalty", assigned(Exam, Period, Room), Penalty) :- exam(Exam, _, _), period(Period, _, _, _, _), room(Room, _, Penalty), assigned(Exam, Period, Room).


% Students should not have more than one exam within a spread of 7 periods.
penalty("ExamSpread",has_two_exams(Student,Exam1,Exam2),3) :- student(Student,Exam1), student(Student,Exam2), exam(Exam1,_,_), exam(Exam2,_,_), period(Period1,_,_,_,_), period(Period2,_,_,_,_), abs(Period1-Period2) <= 7.


% An exam that is large should not be scheduled in a period that is late.
penalty("LargeExamsLate",exam(Exam,_,Is_large),5*Is_large) :- exam(Exam,_,Is_large), period(Date,Time,_,Is_late, Penalty), Is_large = 1, Is_late = 1.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
