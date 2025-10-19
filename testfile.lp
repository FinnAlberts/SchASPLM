% Intentionally BROKEN ASP (do not run)

p(a).
q(b            % ← missing closing parenthesis and period

r(X) :- s(X), notnot t(X).      % ← 'notnot' is not a thing
s(1..3).

t(Y) :- u(Y,Z), Z > 2).         % ← extra closing parenthesis

u(1,2)
u(2,3). u(3,4)                  % ← missing period on first, two rules on one line

:- v(X), not s(X.               % ← missing closing parenthesis

#show p/1.
#show r/1x.                     % ← invalid #show arity format

w(X) :- X = 1..3.               % ← '=' with a range is invalid here
{ v(X) : X = 1..3 }.            % ← same issue with '='

:- X > 2, not defined(X).       % ← 'defined/1' never declared (not a syntax error per se, but meh)

a :- b :- c.                    % ← chained ':-' not allowed


t(Y) :- u(Y,Z),                 % This should be syntactically correct code,
Z > 2.                          % even though it's split over 2 lines with comments on each line.

a. b. c.                        % multiple statements on one line should syntactically be correct.