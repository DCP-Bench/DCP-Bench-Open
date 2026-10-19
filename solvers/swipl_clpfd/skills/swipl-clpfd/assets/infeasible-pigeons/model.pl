% Four pigeons in three holes with at most one pigeon per hole: no placement exists.
% Shows: an infeasible model, where the failure can happen while posting a
% constraint as well as while labelling, and how to report "no solution".
:- use_module(library(clpfd)).
:- initialization(main, main).

% Fails when the constraints cannot hold, either while being posted or while labelled.
place(Holes) :-
    length(Holes, 4),
    Holes ins 1..3,
    all_distinct(Holes),
    once(labeling([], Holes)).

main :-
    (   place(Holes)
    ->  format("Placement: ~w~n", [Holes])
    ;   writeln("No placement exists")
    ).
