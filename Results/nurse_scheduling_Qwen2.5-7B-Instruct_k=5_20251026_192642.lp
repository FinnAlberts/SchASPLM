
% Instance Template
nurse(Nurse).

day(Day).

shift_type(Shift_type, Duration).

nurse_requirement(Shift, Min, Max).

work_requirement(Nurse, Min, Max).

shift_requirement(Shift_type, Min, Max, Preferred).

% Generator

% Instance Template
nurse(Nurse).

day(Day).

shift_type(Shift_type, Duration).

nurse_requirement(Shift, Min, Max).

work_requirement(Nurse, Min, Max).

shift_requirement(Shift_type, Min, Max, Preferred).

% Generator
1 { assigned(Nurse, Shift_type, Day) : day(Day), shift_type(Shift_type,_) } 1 :- nurse(Nurse).


% Hard Constraints

% Every day, the number of nurses assigned to each shift must be between the specified minimum and maximum
:- shift_type(Shift_type, _), day(Day), #count{Nurse : assigned(Nurse, Shift_type, Day)} < nurse_requirement(Shift_type, Min, _).
:- shift_type(Shift_type, _), day(Day), #count{Nurse : assigned(Nurse, Shift_type, Day)} > nurse_requirement(Shift_type, Max, _).


% Each nurse must work at least the specified minimum and at most the specified maximum number of hours
:- nurse(Nurse), #sum{Duration, Shift_type : assigned(Nurse, Shift_type, Day), shift_type(Shift_type, Duration)} < work_requirement(Nurse, Min, Max).
:- nurse(Nurse), #sum{Duration, Shift_type : assigned(Nurse, Shift_type, Day), shift_type(Shift_type, Duration)} > work_requirement(Nurse, Min, Max).


% Nurses must have exactly 30 days of vacation.
:- nurse(Nurse), #count{Day : assigned(Nurse, vacation, Day)}!= 30.


% If a nurse works a night shift, they can not work a morning or afternoon shift the next day
:- assigned(Nurse, night, Day), assigned(Nurse, morning, Day+1).
:- assigned(Nurse, night, Day), assigned(Nurse, afternoon, Day+1).


% If a nurse works an afternoon shift, they cannot work a morning shift the next day.
:- assigned(Nurse, morning, Day), assigned(Nurse, afternoon, Day+1).


% Each nurse has at least two ordinary rest days for every window of fourteen days
:- nurse(N), 
   #count{D : day(D), assigned(N, rest, D), \+ assigned(N, morning, D), \+ assigned(N, afternoon, D), \+ assigned(N, night, D)} < 2, 
   #count{D : day(D), #between(D, 1, 14)} = 14.


% Nurses working on two consecutive nights deserve one special_rest day in addition to the ordinary rest days
:- assigned(Nurse, night, Day1), assigned(Nurse, night, Day2), Day2 = Day1 + 1, #count{X: assigned(Nurse, special_rest, X)} < 1.


% The total number of hours worked by each nurse must be between the specified minimum and maximum
:- nurse(Nurse), #sum{ Hours : assigned(Nurse, Shift_type, Hours), shift_type(Shift_type, Hours) } < work_requirement(Nurse, Min, _).
:- nurse(Nurse), #sum{ Hours : assigned(Nurse, Shift_type, Hours), shift_type(Shift_type, Hours) } > work_requirement(Nurse, _, Max).




% Soft Constraints

% Nurses work the preferred number of shifts for each shift type
shift_type(Shift_type, Duration).

shift_requirement(Shift_type, Min, Max, Preferred).

penalty("ShiftPreference", shift_count(Count, Shift_type, Day), (Count-Preferred)*1) :-
shift_type(Shift_type, _), day(Day),
#count{Nurse : assigned(Nurse, Shift_type, Day)} = Count,
shift_requirement(Shift_type, _, _, Preferred),
Count < Preferred.

penalty("ShiftPreference", shift_count(Count, Shift_type, Day), (Preferred-Count)*1) :-
shift_type(Shift_type, _), day(Day),
#count{Nurse : assigned(Nurse, Shift_type, Day)} = Count,
shift_requirement(Shift_type, _, _, Preferred),
Count > Preferred.

shift_count(Count, Shift_type, Day) :-
shift_type(Shift_type, _), day(Day),
#count{Nurse : assigned(Nurse, Shift_type, Day)} = Count.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
