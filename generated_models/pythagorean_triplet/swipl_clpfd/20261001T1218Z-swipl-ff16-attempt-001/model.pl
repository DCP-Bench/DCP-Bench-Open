:- use_module(library(clpfd)).

% Pythagorean triplet (Project Euler 9): find natural numbers a, b, c with
% a^2 + b^2 = c^2 and a + b + c = 1000. The problem has no instance data; the
% sum 1000 and the bound 500 on each number are the ones the reference fixes
% (every side of a triangle with perimeter 1000 is below 500). As in the
% reference, a, b and c are not required to be in increasing order.
model(_Instance, Vars, [a-A, b-B, c-C]) :-
    Perimeter = 1000,
    Vars = [A, B, C],
    Vars ins 1..500,

    % the three numbers add up to 1000
    A + B + C #= Perimeter,

    % a^2 + b^2 = c^2
    A * A + B * B #= C * C.
