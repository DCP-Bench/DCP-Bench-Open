:- lib(gfd).
:- lib(branch_and_bound).
:- lib(timeout).

p5 :-
    Xs = [A,B,C], Xs :: 1..3,
    ( alldistinct(Xs), labeling(Xs), printf("gfd alldistinct ok %w%n", [Xs]) ; true ),
    ( element(2, [10,20,30], E), E #= 20 -> printf("gfd element ok%n", []) ; printf("gfd element FAIL%n", []) ),
    ( #<=>(A, B, _) -> true ; true ),
    ( bb_min(labeling([A,B,C]), -(A+B+C), bb_options{strategy:restart}) -> printf("bb_min ok %w%n", [A+B+C]) ; printf("bb_min FAIL%n", []) ),
    printf("done p5%n", []).

:- p5, halt.
:- halt.
