:- lib(gfd).
:- lib(branch_and_bound).

p6 :-
    Xs = [A,B,C], Xs :: 1..3,
    gfd:alldifferent(Xs),
    labeling(Xs),
    printf("gfd alldifferent ok %w%n", [Xs]),
    Ys = [P,Q], Ys :: 1..3, P #< Q, labeling(Ys),
    printf("gfd labeling ok %w%n", [Ys]),
    bb_min(labeling([A,B,C]), -(A+B+C), bb_options{strategy:restart}),
    printf("bb_min ok %w%n", [A+B+C]),
    printf("done p6%n", []).

:- p6, halt.
:- halt.
