% Dudeney numbers: print a Dudeney number (number) that is larger than 1.
% A Dudeney number is a positive integer that is a perfect cube such that
% the sum of its digits is equal to the cube root of the number.
% The instance field n bounds the number of digits (the number has at most n digits).

:- lib(ic).

model(Instance, [C | Ds], [number-X]) :-
    memberchk(n-N, Instance),
    MaxX is 10^N - 1,
    max_cube_root(MaxX, MaxC),
    length(Ds, N),
    Ds :: 0..9,
    C :: 2..MaxC,
    X :: 8..MaxX,

    % the number is a perfect cube
    % (the cube root of the number is C, the digits of the number are Ds)
    X #= C*C*C,

    % the number has at most n digits, its digits are Ds, read from the lowest digit
    digits_terms(Ds, 1, Terms),
    X #= sum(Terms),

    % the sum of its digits is equal to the cube root of the number
    sum(Ds) #= C.

% digits_terms(+Ds, +Weight, -Terms): Terms is the list of D*Weight over the digit
% list, lowest digit first (weights 1, 10, 100, ...)
digits_terms([], _, []).
digits_terms([D | Ds], W, [D * W | Ts]) :-
    W1 is W * 10,
    digits_terms(Ds, W1, Ts).

% max_cube_root(+M, -C): C is the largest integer with C^3 =< M
max_cube_root(M, C) :-
    find_cube_root(1, M, C).

find_cube_root(C0, M, C) :-
    C1 is C0 + 1,
    (   C1 ^ 3 =< M
    ->  find_cube_root(C1, M, C)
    ;   C = C0
    ).
