:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Bus scheduling: the day is cut into equal time slots and a bus works two
% consecutive slots. Choose how many buses start in each slot so that every
% slot's demand is met with as few buses as possible.
model(Instance, [Total|X], [x-X], min(Total)) :-
    Demands = Instance.demands,      % buses needed in each slot
    length(Demands, Slots),
    sum_list(Demands, AllDemand),

    % X[i] = number of buses that start working in slot i
    length(X, Slots),
    X ins 0..AllDemand,

    % a bus covers its starting slot and the next one (the day wraps around),
    % so slot i+1 is served by the buses starting in slots i and i+1
    Last is Slots - 1,
    numlist(0, Last, Slot),
    maplist({X, Demands, Slots}/[I]>>(J is (I + 1) mod Slots,
                                      nth0(I, X, Xi), nth0(J, X, Xj), nth0(J, Demands, Dj),
                                      Xi + Xj #>= Dj), Slot),

    % use as few buses as possible
    Bound is AllDemand * Slots,
    Total in 0..Bound,
    sum(X, #=, Total).
