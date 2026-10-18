:- lib(ic).
:- lib(ic_global).
:- lib(ic_edge_finder).
:- lib(listut).

p7 :-
    ( current_module_predicate(exported, P)@ic_constraints, writeq(P), write(' '), fail ; nl ).

:- p7, halt.
:- halt.
