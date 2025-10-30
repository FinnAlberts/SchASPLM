
% Instance Template
nurse(Nurse).

day(0.. N_days-1).

shift_type(Shift_type, Duration).

nurse_requirement(Shift_type, Min, Max).

work_requirement(Min, Max).

shift_requirement(Shift_type, Min, Max, Preferred).

% Generator

% 1
1 {{ assigned(Nurse, Shift, Day) : day(Day) }} 1 :- nurse(Nurse).


% Hard Constraints

% Every day, the number of nurses assigned to each shift must be between the specified minimum and maximum
:- shift_type(Shift_type, _), #count{{ assigned(Nurse, Shift_type, Day) : day(Day), nurse(Nurse) }} < Min, shift_type(Shift_type, _), #count{{ assigned(Nurse, Shift_type, Day) : day(Day), nurse(Nurse) }} > Max.


% Each nurse must work at least the specified minimum and at most the specified maximum number of hours
:- nurse(Nurse), #sum{{Hours, Day: assigned(Nurse, _, Day), shift_type(_, Duration), work_requirement(Min, Max) : assigned(Nurse, _, Day), shift_type(_, Duration), work_requirement(Min, Max)}} < Min, work_requirement(Min, Max).
:- nurse(Nurse), #sum{{Hours, Day: assigned(Nurse, _, Day), shift_type(_, Duration), work_requirement(Min, Max) : assigned(Nurse, _, Day), shift_type(_, Duration), work_requirement(Min, Max)}} > Max, work_requirement(Min, Max).


% Nurses must have exactly 30 days of vacation.
:- #count{{Day: day(Day), assigned(_, _, Day)}} = 30.


% If a nurse works a night shift, they can not work a morning or afternoon shift the next day
:- assigned(Nurse, shift_type(morning, _), Day), assigned(Nurse, shift_type(night, _), Day+1).
:- assigned(Nurse, shift_type(afternoon, _), Day), assigned(Nurse, shift_type(night, _), Day+1).


% If a nurse works an afternoon shift, they cannot work a morning shift the next day.
:- assigned(Nurse, afternoon, Day), assigned(Nurse, morning, Day+1).


% Each nurse has at least two ordinary rest days for every window of fourteen days
:- #count{{Day: day(Day), assigned(_, _, Day)}} >= 2, #count{{Day: day(Day), assigned(_, Shift, Day), shift_type(Shift, Duration), Duration = 1}} >= 14.


% Nurses working on two consecutive nights deserve one special_rest day in addition to the ordinary rest days
:- assigned(Nurse, night, Day1), assigned(Nurse, night, Day2), Day2 = Day1 + 1,!, assigned(Nurse, special_rest, Day2).


% The total number of hours worked by each nurse must be between the specified minimum and maximum
:- nurse(Nurse), #sum{{Hours, Day: assigned(Nurse, _, Day), shift_type(_, Duration), day(Day), time(Day, _, Hours) }} > Max, work_requirement(_, Max).
:- nurse(Nurse), #sum{{Hours, Day: assigned(Nurse, _, Day), shift_type(_, Duration), day(Day), time(Day, _, Hours) }} < Min, work_requirement(Min, _).




% Soft Constraints

% Nurses work the preferred number of shifts for each shift type
shift_count(Count, Shift_type, Day) :- day(Day), #count{{assigned(Nurse, Shift, Day) : nurse(Nurse), shift_type(Shift_type, _), Shift = Shift_type}} = Count.
penalty("ShiftPreference",shift_count(Count, Shift_type, Day),(abs(Preferred-Count))*1) :- shift_count(Count, Shift_type, Day), shift_requirement(Shift_type, _, _, Preferred), Count < Preferred; Count > Preferred.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
