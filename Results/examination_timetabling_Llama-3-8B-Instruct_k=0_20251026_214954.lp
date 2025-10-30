
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
1 {{ assigned(Exam, Period, Room) : period(Period), room(Room) }} 1 :- exam(Exam,_,_).


% Hard Constraints

% No student sits more than one examination at the same time.
:- assigned(Exam1, Period, Room), assigned(Exam2, Period, Room), student(Student, Exam1), student(Student, Exam2).


% The number of students taking exams in a room at the same time should not exceed the capacity of the room.
:- room(Room, Capacity, _), #count{{Student : student(Student, Exam), assigned(Exam, _, Room)}} > Capacity.


% Period Lengths are not violated.
:- assigned(Exam, Period, Room), period(Date, Time, Duration, _, _), Duration!= period_length(Period).


% Some exams must be before other exams.
:- assigned(Exam1, Period1, Room), assigned(Exam2, Period2, Room), order_constraint(Exam1, Exam2), Period1 > Period2.


% Some exams must be at the same time as other exams.
:- same_time_constraint(Exam1, Exam2), assigned(Exam1, Period, Room), assigned(Exam2, Period, Room), Exam1!= Exam2.


% Some exams must be at a differen time than other exams.
:- assigned(Exam1, Period1, Room), assigned(Exam2, Period2, Room), Exam1!= Exam2, Period1 == Period2.


% Some exams must take place in a room with no other exams.
:- assigned(Exam1, Period, Room), assigned(Exam2, Period, Room), Exam1!= Exam2.




% Soft Constraints

% Students should not have more than one exam in the same day
penalty("SameDayExams",same_day_exams(Student,Day),7) :- student(Student,Exam), exam(Exam,_,_), assigned(Exam,Period,Room), period(Date,_,_,_,_) = {{ Date }}, student(Student,Exam2), exam(Exam2,_,_), assigned(Exam2,Period2,Room2), period(Date,_,_,_,_) = {{ Date }}, Period = {{ Period2 - 1; Period2 + 1 }}.

penalty("SameDayExams",same_day_exams(Student,Day),5) :- student(Student,Exam), exam(Exam,_,_), assigned(Exam,Period,Room), period(Date,_,_,_,_) = {{ Date }}, student(Student,Exam2), exam(Exam2,_,_), assigned(Exam2,Period2,Room2), period(Date,_,_,_,_) = {{ Date }}, Period \= {{ Period2 - 1; Period2 + 1 }}.


% Exams of different lengths should not be scheduled in the same room in the same period
penalty("ExamLength",exam_length_mismatch(Room,Period),10) :- assigned(Exam,Period,Room), exam(Exam,Duration1), exam(Exam2,Duration2), Duration1!= Duration2, Exam!= Exam2.


% Some periods have associated penalties
penalty("PeriodPenalty",assigned(Exam,Period,Room),(P*1)) :- exam(Exam,_,_), period(Period,_,_,_,P), assigned(Exam,Period,Room).


% Some rooms have associated penalties
penalty("RoomPenalty",assigned(Exam,Period,Room),(P*1)) :- exam(Exam,_,_), period(Period,_,_,_,_), room(Room,Cap,P), assigned(Exam,Period,Room), P > 0.


% Students should not have more than one exam within a spread of 7 periods.
penalty("ExamSpread",has_two_exams(Student,Exam1,Exam2),3) :- student(Student,Exam1), student(Student,Exam2), exam(Exam1,_,_), exam(Exam2,_,_), period(Period1,_,_,_,_), period(Period2,_,_,_,_), Period1 = {{ period(P) : period(P,_,_,_,_) }}, Period2 = {{ period(P) : period(P,_,_,_,_) }}, abs(P1-P2) <= 7, P1 < P2.


% An exam that is large should not be scheduled in a period that is late.
penalty("LargeExamsLate",exam(Exam,_,Is_large),(Is_large*1)*5) :- exam(Exam,_,Is_large), assigned(Exam,Period,_), period(Date,Time,_,Is_late, Penalty), Is_late, Is_large.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
