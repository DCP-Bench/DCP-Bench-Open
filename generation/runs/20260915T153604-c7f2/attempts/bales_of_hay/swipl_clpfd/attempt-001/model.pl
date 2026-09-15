:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Bales of hay: every pair of bales was weighed, the pair weights arrived in
% sorted order with no record of which pair produced which weight.  Recover the
% individual bale weights.
model(Instance, Vars, [bales-Bales]) :-
    N = Instance.n,
    Weights = Instance.weights,
    length(Bales, N),
    % Bale weight domain 0..50 is fixed by the problem statement, not by the
    % instance; the reference declares the same bound.
    Bales ins 0..50,
    maplist({Bales, N}/[W, Pick]>>pair_weight(Bales, N, W, Pick),
            Weights, Picks),
    append(Picks, PickVars),
    append(Bales, PickVars, Vars).

% Each recorded weight is the sum of some pair i < j of distinct bales; the
% positions are decision variables, so element/3 does the lookup.
pair_weight(Bales, N, W, [I, J]) :-
    I in 1..N,
    J in 1..N,
    I #< J,
    element(I, Bales, Here),
    element(J, Bales, There),
    Here + There #= W.
