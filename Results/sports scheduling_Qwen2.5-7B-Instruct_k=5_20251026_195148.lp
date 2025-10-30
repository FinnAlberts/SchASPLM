
team(Team).

venue(Venue).

availability(Venue, Date).

% Generator

1 {{ game(Team1, Team2, Venue, GameDay) : venue(Venue), gameday(GameDay) }}, 1 :- team(Team1), team(Team2).


% Hard Constraints

% No team plays each other more than once at different gamedays.
:- game(Team1, Team2, Venue, GameDay1), game(Team1, Team2, _, GameDay2), GameDay1!= GameDay2, team(Team1), team(Team2).


% Every team plays every other team at least once.
:- team(Team1), team(Team2), Team1!= Team2, 1 { game(Team1, Team2, _, _) : gameday(_) } = 0.


% No team plays itself.
:- game(Team, Team, _, _).




% Soft Constraints

% Teams should play at the same venue as little as possible.
penalty("VenueStability",game(Team1,Team2,Venue,GameDay),(N-1)*1) :- game(Team1,Team2,Venue,GameDay), N = { game(Team1,Team2,Venue,_) }, N > 1.




% Objective function
#minimize { Penalty,Reason,SoftConstraint : penalty(SoftConstraint,Reason,Penalty) }.
