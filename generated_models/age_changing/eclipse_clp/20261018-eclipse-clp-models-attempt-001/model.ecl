% Age changing: find my age m and my husband's age h (both in years).
% Start with my age and apply the four operations +2, /8, -3, *7 in some order:
% the final answer is his age h. Start with his age and apply the same four
% operations in a different order: the final answer is my age m.

:- lib(ic).

model(_Instance, Vars, [h-H, m-M]) :-
    % the two ages, whole years
    M :: 0..100000,
    H :: 0..100000,

    % the order of the operations for my age and for his age
    % (codes: 1 is +2, 2 is /8, 3 is -3, 4 is *7); each order uses every operation once
    Oa = [A1, A2, A3, A4],
    Ob = [B1, B2, B3, B4],
    Oa :: 1..4,
    Ob :: 1..4,
    alldifferent(Oa),
    alldifferent(Ob),

    % the second order is a different order from the first
    ( A1 #\= B1 ) or ( A2 #\= B2 ) or ( A3 #\= B3 ) or ( A4 #\= B4 ),

    % intermediate values of the chain from my age to his age
    X1 :: -100000..100000,
    X2 :: -100000..100000,
    X3 :: -100000..100000,

    % intermediate values of the chain from his age to my age
    Y1 :: -100000..100000,
    Y2 :: -100000..100000,
    Y3 :: -100000..100000,

    % start with my age, apply the four operations in the order Oa, the end is h
    step(A1, M, X1),
    step(A2, X1, X2),
    step(A3, X2, X3),
    step(A4, X3, H),

    % start with his age, apply the four operations in the order Ob, the end is m
    step(B1, H, Y1),
    step(B2, Y1, Y2),
    step(B3, Y2, Y3),
    step(B4, Y3, M),

    Vars = [A1, A2, A3, A4, B1, B2, B3, B4, M, H, X1, X2, X3, Y1, Y2, Y3].

% one operation: C selects it (1 +2, 2 /8, 3 -3, 4 *7), Y is X after it
% /8 is exact: X must be 8 times Y, so the division leaves no remainder
step(C, X, Y) :-
    (C #= 1) => (Y #= X + 2),
    (C #= 2) => (X #= 8 * Y),
    (C #= 3) => (Y #= X - 3),
    (C #= 4) => (Y #= 7 * X).
