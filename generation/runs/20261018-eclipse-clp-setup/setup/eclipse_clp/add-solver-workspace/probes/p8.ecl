:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.

p8 :-
    length(Xs, 4), Xs :: 1..4,
    alldifferent(Xs),
    Xs = [1,2|_],
    labeling(Xs),
    writeln(Xs).

:- p8, halt.
:- halt.
