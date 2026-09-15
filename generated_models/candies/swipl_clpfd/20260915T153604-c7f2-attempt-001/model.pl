:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Candies: every child gets at least one candy, and between neighbours the
% higher-rated child gets strictly more.  Minimize the total handed out.
model(Instance, Vars, [z-Total, x-Xs], min(Total)) :-
    Ratings = Instance.ratings,
    length(Ratings, N),
    length(Xs, N),
    % Bounds follow the reference: at least one and at most n candies each.
    Xs ins 1..N,
    Limit is N * N,
    Total in 1..Limit,
    Vars = [Total|Xs],
    sum(Xs, #=, Total),
    Total #>= N,
    neighbours(Ratings, Xs).

% Between adjacent children the one rated higher gets strictly more candies;
% equal ratings are left unconstrained.
neighbours([_], [_]).
neighbours([R1, R2|Rs], [X1, X2|Xs]) :-
    compare_pair(R1, R2, X1, X2),
    neighbours([R2|Rs], [X2|Xs]).

compare_pair(R1, R2, X1, X2) :- R1 > R2, !, X1 #> X2.
compare_pair(R1, R2, X1, X2) :- R1 < R2, !, X1 #< X2.
compare_pair(_, _, _, _).
