:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Curious set of integers: 1, 3, 8 and 120 have the property that the product of
% any two of them is one less than a perfect square. Find a fifth number, at
% least 0, that can be added to the set without destroying this property.
model(Instance, Vars, [number-Number]) :-
    N = Instance.n,                         % size of the set
    MaxVal = Instance.max_val,              % no number is larger than this

    % Set[i] is the i-th number of the set. The first four are the numbers the
    % problem starts with (they belong to the problem, not to the instance);
    % the last one is the number to find.
    length(Set, N),
    Set ins 0..MaxVal,
    Set = [1, 3, 8, 120|_],
    last(Set, Number),
    % the numbers of the set are different
    all_distinct(Set),

    % the product of any two numbers plus one is a perfect square: Roots holds
    % one root for each pair (the product of a pair is the same in both orders)
    roots(Set, MaxVal, Roots),
    append(Set, Roots, Vars).

% roots(+Set, +MaxVal, -Roots): for every two numbers X and Y of Set, a root R
% with R * R = X * Y + 1.
roots([], _, []).
roots([X|Xs], MaxVal, Roots) :-
    pair_roots(Xs, X, MaxVal, Here),
    roots(Xs, MaxVal, There),
    append(Here, There, Roots).

pair_roots([], _, _, []).
pair_roots([Y|Ys], X, MaxVal, [Root|Roots]) :-
    Root in 0..MaxVal,
    Root * Root #= X * Y + 1,
    pair_roots(Ys, X, MaxVal, Roots).
