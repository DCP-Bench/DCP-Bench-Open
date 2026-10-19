:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.
:- lib(timeout).

magic(Mode, N, Flat, Sel, Val) :-
    NN is N*N, S is N*(NN+1)//2,
    dim(M, [N,N]), M[1..N,1..N] :: 1..NN,
    flatten_array(M, Flat),
    ( Mode = alld -> alldifferent(Flat)
    ; ( fromto(Flat, [X|Rest], Rest, []) do ( foreach(Y, Rest), param(X) do X #\= Y ) ) ),
    ( for(I, 1, N), param(M, N, S) do
        collection_to_list(M[I,1..N], Row), collection_to_list(M[1..N,I], Col),
        sum(Row) #= S, sum(Col) #= S ),
    ( for(I, 1, N), foreach(X1, D1), foreach(Y1, D2), param(M, N) do X1 is M[I,I], J is N+1-I, Y1 is M[I,J] ),
    sum(D1) #= S, sum(D2) #= S,
    search(Flat, 0, Sel, Val, complete, []).

first(Mode, N, Sel, Val) :-
    cputime(T0),
    ( timeout(( magic(Mode, N, _, Sel, Val), true ), 60, fail) -> R = ok ; R = timeout_or_fail ),
    cputime(T1), T is T1 - T0,
    printf("ic %w N=%d magic first %w %w: %w in %.2f s cpu%n", [Mode, N, Sel, Val, R, T]).
