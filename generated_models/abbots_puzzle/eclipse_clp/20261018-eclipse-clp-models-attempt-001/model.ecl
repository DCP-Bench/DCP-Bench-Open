% Abbot's puzzle: 100 bushels of corn are distributed among 100 people
% such that each man receives three bushels, each woman two, and each child half a bushel.
% There are five times as many women as men. Find the number of men, women and children.
:- lib(ic).

model(_Instance, [Men, Women, Children], [men-Men, women-Women, children-Children]) :-
    [Men, Women, Children] #:: 0..100,

    % there are five times as many women as men
    Women #= 5 * Men,

    % 100 people among men, women and children
    Men + Women + Children #= 100,

    % 100 bushels: each man three, each woman two, each child half a bushel
    % (multiplied by 2 to keep integer coefficients)
    6 * Men + 4 * Women + Children #= 200.
