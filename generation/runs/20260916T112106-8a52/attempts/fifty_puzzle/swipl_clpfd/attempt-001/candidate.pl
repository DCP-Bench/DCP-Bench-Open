:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Fifty puzzle: knock over a set of dummies whose numbers total exactly the
% target sum.
model(Instance, Dummies, [dummies-Dummies]) :-
    Values = Instance.values,
    Target = Instance.target_sum,
    length(Values, N),
    length(Dummies, N),
    Dummies ins 0..1,
    scalar_product(Values, Dummies, #=, Target).
