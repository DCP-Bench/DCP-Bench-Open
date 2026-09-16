:- use_module(library(clpfd)).

% Eighteen hole golf: eighteen holes of length three, four or five that add up
% to a par of seventy-two.
model(_Instance, Holes, [holes-Holes]) :-
    length(Holes, 18),
    Holes ins 3..5,
    sum(Holes, #=, 72).
