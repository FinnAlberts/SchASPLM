
% Instance Template
nurse(Nurse).

day(0.. N_days-1).

shift_type(Shift_type, Duration).

nurse_requirement(Shift_type, Min, Max).

work_requirement(Min, Max).

shift_requirement(Shift_type, Min, Max, Preferred).

% Generator

% 1
nurse(Nurse) :- 1 = #count{ Day : day(Day) }.


% Hard Constraints

% Every day, the number of nurses assigned to each shift must be between the specified minimum and maximum
:- shift_type(Shift_type, _), #count{Day : day(Day), Nurse : nurse(Nurse), shift(Nurse, Day, Shift_type)} < nurse_requirement(Shift_type, Min, Max).
:- shift_type(Shift_type, _), #count{Day : day(Day), Nurse : nurse(Nurse), shift(Nurse, Day, Shift_type)} > Max, nurse_requirement(Shift_type, Min, Max).


% Each nurse must work at least the specified minimum and at most the specified maximum number of hours
Corrected code:
:- nurse(Nurse), S = #sum{ Hours : work(Nurse, Day, Hours) | day(Day) }, S < Min, work_requirement(Min, _).
Corrected code:
:- nurse(Nurse), S = #sum{ Hours : work(Nurse, Day, Hours) | day(Day) }, S >= Max, work_requirement(_, Max1), Max = Max1.


% Nurses must have exactly 30 days of vacation.
:- nurse(Nurse), #count{Day : day(Day), nurse(Nurse), shift_type(_, 'vacation'), work_requirement(30, 30)} = 30.


% If a nurse works a night shift, they can not work a morning or afternoon shift the next day
Corrected code:
:- shift_type(Shift_type, _), shift_type('night', _), assigned(Nurse, Shift_type, Day, _), Day1 is Day+1, assigned(Nurse, Shift_type2, Day1), shift_type('morning', _), Shift_type \='morning', Shift_type2 \='morning'.
Corrected code:
:- shift_type(Shift_type, _), shift_type('night', _), assigned(Nurse, Shift_type, Day, _), Day1 is Day+1, assigned(Nurse, Shift_type2, Day1), not(shift_type('morning', _)), not(shift_type('afternoon', _)), Shift_type2 \='morning', Shift_type2 \= 'afternoon'.


% If a nurse works an afternoon shift, they cannot work a morning shift the next day.
:- assigned(Nurse, afternoon, Day), assigned(Nurse, morning, Day+1).


% Each nurse has at least two ordinary rest days for every window of fourteen days
:- nurse(Nurse), C > 2, C1 < 2, C = #count{Day : day(Day), nurse_shift(Nurse, Day, Shift_type), shift_type(Shift_type, Duration) = rest}, C1 = #count{Day : day(Day), nurse_shift(Nurse, Day, Shift_type)}.


% Nurses working on two consecutive nights deserve one special_rest day in addition to the ordinary rest days
Corrected code:
nurse_requirement(night, 2, 2) :- assigned(N, night, D1), assigned(N, night, D2), D2 - D1 = 1, D2 = D1 + 1, assigned(N, special_rest, D2).


% The total number of hours worked by each nurse must be between the specified minimum and maximum
Corrected code:
:- nurse(Nurse), S = #sum{ Hours : assigned(Nurse, Day, Hours) | day(Day) }, S > Max, work_requirement(_, Max).
Corrected code:
:- nurse(Nurse), S = #sum{ Hours : assigned(Nurse, Day, Hours) | day(Day) }, S =< Min, work_requirement(_, Max), S >= Max.




% Soft Constraints

% Nurses work the preferred number of shifts for each shift type
Corrected code:
shift_count(Count, Shift_type, Nurse, Day) :- nurse(Nurse), day(Day), Count = #count{Shift : assigned(Shift, Day, Nurse), shift_type(Shift, Duration), shift_type(Shift_type, Duration)}.
penalty("ShiftCount", shift_count(Count, Shift_type, Nurse, Day), (abs(Preferred-Count))*1) :- shift_count(Count, Shift_type, Nurse, Day), shift_requirement(Shift_type, _, _, Preferred).




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
