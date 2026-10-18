% 4x4 magic square: entries 1..16 all different, every row, column and
% diagonal sums to 34.
:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.   % ic and ic_global both export it

main :-
    N = 4, NN is N*N, S is N*(NN+1)//2,
    dim(M, [N,N]),                         % N x N array of fresh variables
    M[1..N,1..N] :: 1..NN,                 % domain on every cell
    flatten_array(M, Flat),                % collection_to_list/2 would give a list of rows
    % all cells different
    alldifferent(Flat),
    % each row and each column sums to S
    ( for(I, 1, N), param(M, N, S) do
        collection_to_list(M[I,1..N], Row),
        collection_to_list(M[1..N,I], Col),
        sum(Row) #= S,
        sum(Col) #= S
    ),
    % both diagonals sum to S
    ( for(I, 1, N), foreach(X, D1), foreach(Y, D2), param(M, N) do
        X is M[I,I],
        J is N+1-I,
        Y is M[I,J]
    ),
    sum(D1) #= S,
    sum(D2) #= S,
    % search: smallest domain first, smallest value first
    search(Flat, 0, first_fail, indomain_min, complete, []),
    ( for(I, 1, N), param(M, N) do
        collection_to_list(M[I,1..N], Row),
        writeln(Row)
    ).
