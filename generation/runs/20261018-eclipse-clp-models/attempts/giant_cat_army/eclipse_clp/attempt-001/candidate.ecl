% Giant cat army: start from the list [0] and build a list x of 24 integers.
% Each step adds 5, adds 7, or takes the square root (the result must be an integer).
% The game is complete when 2, 10 and 14 appear on the list in that order, with
% other numbers allowed between them. All elements are distinct, at most 60, and
% integers. The list starts with 0 and ends with 14.

:- lib(ic).

model(_Instance, Vars, [x-X]) :-
    Len = 24,
    Max = 60,
    length(X, Len),
    X :: 0..Max,

    % starting with [0]
    X = [Start | _],
    Start #= 0,

    % ending with 14
    append(_, [Final], X),
    Final #= 14,

    % build this list by using one of three operations: adding 5, adding 7, or taking sqrt
    chain(X, Ops),

    % all the elements are distinct
    alldifferent(X),

    % 2, 10 and 14 appear on the list, in that order, other numbers may lie between them
    P2 :: 1..Len,
    P10 :: 1..Len,
    P14 :: 1..Len,
    element(P2, X, 2),
    element(P10, X, 10),
    element(P14, X, 14),
    P2 #< P10,
    P10 #< P14,

    append(Ops, X, T1),
    append(T1, [P2, P10, P14], Vars).

% each step from X to Y is one of the three operations, chosen by O
% (1 adds 5, 2 adds 7, 3 takes the square root, so X is the square of Y)
chain([_], []).
chain([X, Y | Rest], [O | Ops]) :-
    O :: 1..3,
    (O #= 1) => (Y #= X + 5),
    (O #= 2) => (Y #= X + 7),
    (O #= 3) => (X #= Y * Y),
    chain([Y | Rest], Ops).
