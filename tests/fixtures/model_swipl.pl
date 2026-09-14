:- use_module(library(clpfd)).

model(Instance, [X, Y], [x-X, y-Y], Objective) :-
    N = Instance.n,
    [X, Y] ins 0..N,
    (   Instance.optimize == true
    ->  X + Y #>= N,
        Objective = min(X + Y)
    ;   X + Y #= N,
        Objective = none
    ).
