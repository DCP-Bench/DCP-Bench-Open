% Model for divisible_by_1_through_9: find a 10 digit number that uses each of
% the digits 0 to 9 exactly once and where the number formed by the first n
% digits of the number is divisible by n. Output: number (the full 10 digit number).

:- lib(ic).

model(_Instance, Vars, [number-Number]) :-
    % a number that uses each of the digits 0 to 9 exactly once
    length(Digits, 10),
    Digits :: 0..9,
    alldifferent(Digits),
    % a 10 digit number has a nonzero leading digit
    Digits = [First|_],
    First #\= 0,
    % the number formed by the first n digits of the number is divisible by n
    prefix_divisible(Digits, 0, 1, Vars, Number).

% Vars is the digit list with each quotient Q_n placed right after digit n, so
% that labelling fixes the quotient as soon as its prefix is known.
prefix_divisible([], Prefix, _, [], Prefix).
prefix_divisible([D|Ds], Prefix, N, [D, Q|Vs], Number) :-
    P #= Prefix * 10 + D,
    MaxQ is 10000000000 // N,
    Q :: 0..MaxQ,
    P #= N * Q,
    N1 is N + 1,
    prefix_divisible(Ds, P, N1, Vs, Number).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
