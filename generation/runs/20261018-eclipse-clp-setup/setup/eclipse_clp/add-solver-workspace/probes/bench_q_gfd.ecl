:- lib(gfd).
:- lib(timeout).

queens(dec, N, Qs, Sel, Val) :-
    length(Qs, N), Qs #:: 1..N,
    ( fromto(Qs, [Q|Rest], Rest, []) do
        ( foreach(Q2, Rest), count(D, 1, _), param(Q) do Q #\= Q2, Q #\= Q2 + D, Q #\= Q2 - D ) ),
    search(Qs, 0, Sel, Val, complete, []).
queens(alld, N, Qs, Sel, Val) :-
    length(Qs, N), Qs #:: 1..N,
    ( for(I, 1, N), foreach(Q, Qs), foreach(P, Ps), foreach(M, Ms) do P #= Q + I, M #= Q - I ),
    alldifferent(Qs), alldifferent(Ps), alldifferent(Ms),
    search(Qs, 0, Sel, Val, complete, []).

first(Mode, N, Sel, Val) :-
    cputime(T0),
    ( timeout(( queens(Mode, N, _, Sel, Val), true ), 60, fail) -> R = ok ; R = timeout_or_fail ),
    cputime(T1), T is T1 - T0,
    printf("gfd %w N=%d first %w %w: %w in %.2f s cpu%n", [Mode, N, Sel, Val, R, T]).

allsol(Mode, N, Sel, Val) :-
    cputime(T0),
    ( timeout(( findall(x, queens(Mode, N, _, Sel, Val), L), length(L, C) ), 120, (C = timeout)) -> true ; C = failed ),
    cputime(T1), T is T1 - T0,
    printf("gfd %w N=%d all %w %w: %w solutions in %.2f s cpu%n", [Mode, N, Sel, Val, C, T]).
