:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Climbing stairs: split n steps into moves of m1..m2 steps each.  Unused
% moves are zero, and once a move is zero every later one is zero too.
model(Instance, Steps, [steps-Steps]) :-
    N = Instance.n,
    M1 = Instance.m1,
    M2 = Instance.m2,
    length(Steps, N),
    Steps ins 0..M2,
    sum(Steps, #=, N),
    % A move is either skipped or a stride of at least m1 and at most m2.
    maplist({M1, M2}/[S]>>(S #>= M1 #\/ S #= 0), Steps),
    trailing_zeros(Steps).

% Once a move is zero, every later move is zero as well.
trailing_zeros([]).
trailing_zeros([S|Rest]) :-
    maplist({S}/[Later]>>(S #= 0 #==> Later #= 0), Rest),
    trailing_zeros(Rest).
