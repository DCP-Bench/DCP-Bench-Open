:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [sol-Sol]) :-
    K = Instance.k,
    Length is 2 * K,
    Last is Length - 1,
    % Position holds the two 0-based places of each value: the first copies
    % first, then the second copies.
    length(Position, Length),
    Position ins 0..Last,
    length(Sol, Length),
    Sol ins 1..K,
    all_distinct(Position),
    numlist(1, K, Values),
    maplist({Position, Sol, K}/[I]>>places(I, K, Position, Sol), Values),
    append(Position, Sol, Vars).

places(I, K, Position, Sol) :-
    nth1(I, Position, First),
    Second is I + K,
    nth1(Second, Position, Next),
    Next #= First + I + 1,
    % element/3 is 1-based, the reference's positions are 0-based.
    FirstCell #= First + 1,
    NextCell #= Next + 1,
    element(FirstCell, Sol, I),
    element(NextCell, Sol, I).
