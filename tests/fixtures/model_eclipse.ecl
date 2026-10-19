:- lib(ic).

model(Instance, [X, Y], [x-X, y-Y], Objective) :-
    memberchk(n-N, Instance),
    [X, Y] #:: 0..N,
    (   memberchk(optimize-true, Instance)
    ->  X + Y #>= N,
        Objective = min(X + Y)
    ;   X + Y #= N,
        Objective = none
    ).
