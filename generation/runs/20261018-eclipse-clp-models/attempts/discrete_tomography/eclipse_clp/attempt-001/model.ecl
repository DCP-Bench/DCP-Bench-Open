% Discrete tomography: a matrix of zeroes and ones is x-rayed vertically and
% horizontally. Given the number of ones in each row and each column, find
% the matrix. Output: the matrix as a list of rows.
:- lib(ic).

model(Instance, Vars, [matrix-Rows], none) :-
    memberchk(row_sums-RowSums, Instance),
    memberchk(col_sums-ColSums, Instance),
    length(RowSums, R),
    length(ColSums, C),
    % one cell per row and column of the matrix, each a zero or a one
    dim(M, [R, C]),
    M[1..R, 1..C] :: 0..1,
    flatten_array(M, Vars),
    % the number of ones in each row is the row's x-ray count
    ( foreach(S, RowSums), count(I, 1, _), param(M, C) do
        collection_to_list(M[I, 1..C], Row),
        sum(Row) #= S
    ),
    % the number of ones in each column is the column's x-ray count
    ( foreach(S, ColSums), count(J, 1, _), param(M, R) do
        collection_to_list(M[1..R, J], Col),
        sum(Col) #= S
    ),
    % the matrix as a list of rows, for output
    ( for(I, 1, R), foreach(Row, Rows), param(M, C) do
        collection_to_list(M[I, 1..C], Row)
    ).
