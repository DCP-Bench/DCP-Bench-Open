% Heterosquare of order n (the instance field n): an n*n square x of distinct
% integers from 1 to n^2 such that the sums of the rows, the columns and the
% two diagonals are all different from each other.

:- lib(ic).
:- lib(listut).

model(Instance, Cells, [x-Rows]) :-
    memberchk(n-N, Instance),
    NN is N*N,
    ( for(_, 1, N), foreach(Row, Rows) do length(Row, N) ),
    flatten(Rows, Cells),

    % The elements are distinct integers from 1 to n^2.
    Cells :: 1..NN,
    all_different_pairs(Cells),

    % The sums of the rows, columns and diagonals are all different.
    column_lists(Rows, N, Cols),
    diagonal_lists(Rows, N, Diag1, Diag2),
    append(Rows, Cols, RowsCols),
    append(RowsCols, [Diag1, Diag2], Lines),
    sums_of(Lines, Sums),
    Sums :: 1..N*NN,
    all_different_pairs(Sums).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

all_different_pairs([]).
all_different_pairs([X|Xs]) :-
    ( foreach(Y, Xs) do X #\= Y ),
    all_different_pairs(Xs).

sums_of(Lines, Sums) :-
    ( foreach(L, Lines), foreach(S, Sums) do sum(L) #= S ).

column_lists(Rows, N, Cols) :-
    ( for(J, 1, N), foreach(C, Cols) do
        ( foreach(R, Rows), foreach(X, C) do nth1(J, R, X) )
    ).

diagonal_lists(Rows, N, Diag1, Diag2) :-
    ( for(I, 1, N), foreach(X, Diag1), foreach(Y, Diag2), param(Rows, N) do
        nth1(I, Rows, R1),
        nth1(I, R1, X),
        J is N + 1 - I,
        nth1(J, R1, Y)
    ).
