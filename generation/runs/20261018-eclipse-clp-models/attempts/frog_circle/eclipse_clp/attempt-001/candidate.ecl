% Frog circle: cards numbered 1 to n are arranged in a circle. A frog jumps on
% card 1, then jumps to the card 1 place clockwise around the circle. Then, from
% card k, it jumps directly to the card k places clockwise around the circle, and
% so on forever. Find an arrangement of the cards that lets the frog jump on every
% card starting from card 1. Output x: the arrangement, as n different integers
% from 1 to n (x[P] is the card at position P, positions 1..n clockwise).

:- lib(ic).

model(Instance, Vars, [x-X], none) :-
    memberchk(n-N, Instance),
    length(X, N),
    X :: 1..N,
    alldifferent(X),

    % Succ[P] is the position the frog lands on after a jump from position P,
    % which is x[P] places clockwise. Positions wrap around the circle of N places.
    length(Succ, N),
    Succ :: 1..N,
    ( foreach(Xp, X), foreach(Sp, Succ), count(P, 1, _), param(N) do
        % Wrap is 1 when the jump passes the end of the list of positions.
        Wrap #= (Xp + P #> N),
        Sp #= Xp + P - N * Wrap
    ),

    % The frog's visits, in order: Pos[1] is the position of card 1, and each next
    % visit is the successor of the previous one. The frog reaches every card
    % exactly when the first N visits are all different.
    length(Pos, N),
    Pos :: 1..N,
    alldifferent(Pos),
    Pos = [Pos1 | _],
    element(Pos1, X, 1),
    chain(Pos, Succ),

    append(X, Pos, Vars).

% Each visit is the successor of the one before it.
chain([_], _).
chain([P, Q | T], Succ) :-
    element(P, Succ, Q),
    chain([Q | T], Succ).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_max, complete, []).
