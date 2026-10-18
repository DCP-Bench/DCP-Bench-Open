% Problem: flip_rows_cols
% Given an array of positive and negative numbers, flip the sign of entire rows and
% columns, as many of them as you like. The goal is to make each one of all the rows
% and columns sum to positive numbers (or zero), and then to find the solution that
% has the smallest overall sum.
% Output: row_signs and col_signs, lists of -1/1 for the selected sign of each
% row/column.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [row_signs-Rs, col_signs-Cs], min(sum(Flat))) :-
    memberchk(input_matrix-Matrix, Instance),
    length(Matrix, NR),
    Matrix = [FirstRow | _],
    length(FirstRow, NC),
    length(Rs, NR), Rs :: [-1, 1],
    length(Cs, NC), Cs :: [-1, 1],
    append(Rs, Cs, Vars),

    % each cell of the flipped matrix is the input value times its row sign and column sign
    ( foreach(Row, Matrix), foreach(XRow, Xss), foreach(Ri, Rs), param(Cs) do
        ( foreach(A, Row), foreach(Cj, Cs), foreach(X, XRow), param(Ri) do
            X #= A * Ri * Cj
        )
    ),
    flatten(Xss, Flat),

    % each row of the flipped matrix sums to a positive number or zero
    ( foreach(XRow, Xss) do
        sum(XRow) #>= 0
    ),

    % each column of the flipped matrix sums to a positive number or zero
    ( for(J, 1, NC), param(Xss) do
        ( foreach(XRow, Xss), foreach(X, Col), param(J) do
            nth1(J, XRow, X)
        ),
        sum(Col) #>= 0
    ).
