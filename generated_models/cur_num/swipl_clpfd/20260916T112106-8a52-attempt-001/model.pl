:- use_module(library(clpfd)).

% Curious number: one more than it is a square, and one more than its half is a
% square too - and it is not 48, which is the known example.
model(_Instance, Vars, [peculiar-Peculiar]) :-
    Vars = [Peculiar, A, B, C, D, E],
    Vars ins 1..10000,
    Peculiar #\= 48,
    % Add one and you get a square.
    Peculiar + 1 #= A,
    A #= B * B,
    % Halve it, add one, and you get a square again.
    Peculiar #= 2 * C,
    C + 1 #= D,
    D #= E * E.
