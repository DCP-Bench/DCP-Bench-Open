% Infeasible model: 9 pigeons, 8 holes, no two pigeons share a hole.
% In ECLiPSe a failed search means "no solution": the goal fails, it raises nothing.
:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.

pigeons(Pigeons) :-
    length(Pigeons, 9),
    Pigeons :: 1..8,
    alldifferent(Pigeons),
    labeling(Pigeons).

main :-
    ( pigeons(Ps) ->
        printf("feasible: %w%n", [Ps])
    ;
        printf("infeasible: no assignment exists%n", [])
    ).
