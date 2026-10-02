:- use_module(library(clpfd)).

% Hardy's 1729 with squares: find four different numbers a, b, c, d between 1
% and 100 such that a^2 + b^2 = c^2 + d^2. The problem has no instance data;
% the range 1..100 is the one in the statement.
model(_Instance, Vars, [a-A, b-B, c-C, d-D]) :-
    Vars = [A, B, C, D],
    Vars ins 1..100,

    % the sum of the squares of the first two numbers equals the sum of the
    % squares of the other two
    A * A + B * B #= C * C + D * D,

    % the four numbers are different
    all_distinct(Vars).
