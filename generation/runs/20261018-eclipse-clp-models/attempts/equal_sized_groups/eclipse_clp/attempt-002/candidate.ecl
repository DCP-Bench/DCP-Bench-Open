% Equal-sized groups: divide a sorted list of N elements into K groups by
% choosing K-1 split points between elements. Equal values must stay in the
% same group. Minimise the total error, where each group's size is compared
% with round(N/K).

:- lib(ic).
:- lib(lists).

model(Instance, Xs, [x-Xs], min(sum(Errs))) :-
    memberchk(a-A, Instance),
    memberchk(k-K, Instance),
    length(A, N),
    round_div(N, K, Target),
    % a split point p means the groups end after element p (1-based);
    % it is only allowed between two different values
    valid_splits(A, 1, Valid),
    KM1 is K - 1,
    length(Xs, KM1),
    % the split points are the boundaries of the groups
    ( foreach(X, Xs), param(Valid) do X :: Valid ),
    % K-1 split points, strictly increasing, so every group is non-empty
    strictly_increasing(Xs),
    % group boundaries 0, x_1, ..., x_{K-1}, N
    append([0], Xs, Starts0),
    append(Starts0, [N], Bounds),
    group_sizes(Bounds, Sizes),
    % each group's error against round(N/K)
    ( foreach(S, Sizes), param(Target), foreach(E, Errs) do E #= abs(S - Target) ).

% Search: smallest domain first, values from the bottom up.
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% The split point after element p is allowed when element p and p+1 differ.
valid_splits([X, Y | T], P, [P | Ps]) :-
    X =\= Y,
    !,
    P1 is P + 1,
    valid_splits([Y | T], P1, Ps).
valid_splits([_, Y | T], P, Ps) :-
    P1 is P + 1,
    valid_splits([Y | T], P1, Ps).
valid_splits([_], _, []).

% Split points are strictly increasing.
strictly_increasing([]).
strictly_increasing([_]).
strictly_increasing([X, Y | T]) :-
    X #< Y,
    strictly_increasing([Y | T]).

% Size of each group from consecutive boundaries.
group_sizes([_], []).
group_sizes([B1, B2 | T], [S | Ss]) :-
    S #= B2 - B1,
    group_sizes([B2 | T], Ss).

% round(N/K) as Python's round: halves go to the even integer.
round_div(N, K, T) :-
    Q is N // K,
    R is N mod K,
    D is 2 * R - K,
    (   D < 0 -> T = Q
    ;   D > 0 -> T is Q + 1
    ;   Q mod 2 =:= 0 -> T = Q
    ;   T is Q + 1
    ).
