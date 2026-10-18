% Magic square of size n (n != 2): an n x n grid whose cells hold the
% integers 1..n^2, each used once, such that every row, column and diagonal
% sums to n(n^2+1)/2. The size n comes from the instance.
:- lib(ic).

model(Instance, Vars, [square-Rows]) :-
    memberchk(n-N, Instance),
    NN is N*N,
    S is N*(NN+1)//2,
    dim(M, [N,N]),
    M[1..N,1..N] :: 1..NN,
    flatten_array(M, Vars),

    % each cell contains a different integer from 1 to n^2
    alldifferent(Vars),

    % the sum of the integers in each row and each column is equal to n(n^2+1)/2
    ( for(I, 1, N), param(M, N, S) do
        collection_to_list(M[I,1..N], Row),
        collection_to_list(M[1..N,I], Col),
        sum(Row) #= S,
        sum(Col) #= S
    ),

    % the sum of the integers on each diagonal is equal to n(n^2+1)/2
    ( for(I, 1, N), foreach(X, D1), foreach(Y, D2), param(M, N) do
        X is M[I,I],
        J is N+1-I,
        Y is M[I,J]
    ),
    sum(D1) #= S,
    sum(D2) #= S,

    % the square as a list of rows
    ( for(I, 1, N), foreach(R, Rows), param(M, N) do
        collection_to_list(M[I,1..N], R)
    ).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
