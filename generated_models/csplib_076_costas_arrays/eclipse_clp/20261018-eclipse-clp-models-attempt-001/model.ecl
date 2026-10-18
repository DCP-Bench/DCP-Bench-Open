% CSPLib 076, Costas arrays: place n marks on an n x n grid, one mark per row and per column,
% so that the n(n-1)/2 vectors between the marks are all different.
% Output costas: the list of n column positions (1-based), one per row.

:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.
:- lib(listut).

model(Instance, Xs, [costas-Xs]) :-
    % the instance field n gives the grid size and the number of marks
    memberchk(n-N, Instance),
    length(Xs, N),
    Xs :: 1..N,

    % the marks form a permutation: one mark per row and per column
    alldifferent(Xs),

    % difference triangle: for each length l in 1..n-1 the n-l differences
    % X_i - X_{i+l} are the vectors of length l; each line must not contain a value twice
    ( for(L, 1, N-1), param(Xs, N) do
        Len is N - L,
        ( for(I, 1, Len), foreach(D, Ds), param(Xs, L) do
            J is I + L,
            nth1(I, Xs, XI),
            nth1(J, Xs, XJ),
            D #= XI - XJ
        ),
        alldifferent(Ds)
    ).
