:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Guards and apples: at each gate the boy hands over half his apples plus one,
% and walks away from the last gate with exactly one apple left.
model(Instance, Apples, [apples-Apples]) :-
    NumGates = Instance.num_gates,
    Length is NumGates + 1,
    length(Apples, Length),
    % Apple count domain 0..100 is the reference's declared bound.
    Apples ins 0..100,
    last(Apples, AfterLastGate),
    AfterLastGate #= 1,
    gates(Apples).

% Before a gate he carries twice what he has after it, plus the two he loses.
gates([_]).
gates([Before, After|Rest]) :-
    Before #= 2 * (After + 1),
    gates([After|Rest]).
