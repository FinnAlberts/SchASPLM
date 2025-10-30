
% Instance Template
team(Team).

venue(Venue).

availability(Venue, Date).

% Generator

% 1
1 { assigned(Team1, Team2, Venue, Gameday) : team(Team1), team(Team2), venue(Venue), gameday(Gameday) }.


% Hard Constraints

% No team plays each other more than once at different gamedays.
:- assigned(Team1, Team2, _, Gameday1), assigned(Team1, Team2, _, Gameday2), Gameday1!= Gameday2.


% Every team plays every other team at least once.
:- team(Team1), team(Team2), Team1!= Team2, not assigned(Team1, Team2, _, _).


% No team plays itself.
:- assigned(Team, Team, _, _).




% Soft Constraints

% Teams should play at the same venue as little as possible.
Corrected code:
penalty("VenueStability", T1_Venue) :- team(Team1), assigned(Team1,Team2,T1_Venue,Gameday), team(Team2), not using_venue(Team2,T2_Venue), T1_Venue \= T2_Venue.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
