% QG3.m quasigroup existence (CSPLib 003).
% An order m quasigroup is a Latin square of size m: an m x m table in which
% each element occurs once in every row and column. QG3.m: (a*b)*(b*a) = a
% for all a, b. Values are 0..m-1. Output: the quasigroup as a list of rows.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [quasigroup-Rows]) :-
    memberchk(m-M, Instance),

    % An order m quasigroup is a Latin square of size m: an m x m table in
    % which each element occurs once in every row and column.
    length(Rows, M),
    ( foreach(Row, Rows), param(M) do
        length(Row, M)
    ),
    flatten(Rows, Flat),
    Flat :: 0..M-1,
    ( foreach(Row, Rows) do
        alldifferent(Row)
    ),
    ( for(J, 1, M), param(Rows) do
        ( foreach(Row, Rows), foreach(V, Col), param(J) do
            nth1(J, Row, V)
        ),
        alldifferent(Col)
    ),

    % QG3.m problems are order m quasigroups for which (a*b)*(b*a) = a.
    % The product a*b is Rows[a][b]; the element index into Flat is row*m+col+1.
    ( for(A, 0, M-1), param(Rows, Flat, M) do
        ( for(B, 0, M-1), param(Rows, Flat, M, A) do
            nth0(A, Rows, RowA),
            nth0(B, RowA, C),
            nth0(B, Rows, RowB),
            nth0(A, RowB, D),
            Idx #= C*M + D + 1,
            element(Idx, Flat, A)
        )
    ),

    Vars = Flat.
