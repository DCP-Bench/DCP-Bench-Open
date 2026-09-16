:- use_module(library(clpfd)).

% Five brigands: 200 doubloons shared so that the reweighted shares also come to
% 200.  The reweighting is 12A + 3B + C + D/2 + E/3; multiplying through by six
% clears both fractions, which is what the reference does.
model(_Instance, Vars, ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E]) :-
    Vars = [A, B, C, D, E],
    Vars ins 1..200,
    A + B + C + D + E #= 200,
    6 * (A * 12 + B * 3 + C) + 3 * D + 2 * E #= 6 * 200.
