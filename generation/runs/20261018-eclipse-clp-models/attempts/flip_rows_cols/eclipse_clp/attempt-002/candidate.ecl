% Problem: flip_rows_cols
% Given an array of positive and negative numbers, flip the sign of entire rows and
% columns, as many of them as you like. The goal is to make each one of all the rows
% and columns sum to positive numbers (or zero), and then to find the solution that
% has the smallest overall sum.
% Output: row_signs and col_signs, lists of -1/1 for the selected sign of each
% row/column.
%
% Encoding: Bs(I) = 1 when row I is flipped, Bc(J) = 1 when column J is flipped,
% and the sign of each row/column is 1 - 2*B.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [row_signs-Rs, col_signs-Cs], min(sum(Flat))) :-
    memberchk(input_matrix-Matrix, Instance),
    length(Matrix, NR),
    Matrix = [FirstRow | _],
    length(FirstRow, NC),

    % Each row and each column is either flipped or not.
    length(Bs, NR), Bs :: 0..1,
    length(Bc, NC), Bc :: 0..1,
    ( foreach(B, Bs), foreach(R, Rs) do R #= 1 - 2*B ),
    ( foreach(B, Bc), foreach(C, Cs) do C #= 1 - 2*B ),

    % Column flips are labelled first: once they are fixed, each row's flip is
    % forced by its row-sum constraint, which keeps the search small.
    append(Bc, Bs, Vars),

    % Each cell of the flipped matrix is the input value A times the row sign and the
    % column sign. With Pij = Bi * Bj as a 0/1 variable, that is linear in the flips:
    % A * (1-2Bi) * (1-2Bj) = A - 2A*Bi - 2A*Bj + 4A*Pij.
    ( foreach(Row, Matrix), foreach(XRow, Xss), foreach(Bi, Bs), param(Bc) do
        ( foreach(A, Row), foreach(Bj, Bc), foreach(X, XRow), param(Bi) do
            P #:: 0..1,
            P #=< Bi,
            P #=< Bj,
            P #>= Bi + Bj - 1,
            X #= A - 2*A*Bi - 2*A*Bj + 4*A*P
        )
    ),
    flatten(Xss, Flat),

    % Each row of the flipped matrix sums to a positive number or zero.
    ( foreach(XRow, Xss) do
        sum(XRow) #>= 0
    ),

    % Each column of the flipped matrix sums to a positive number or zero.
    ( for(J, 1, NC), param(Xss) do
        ( foreach(XRow, Xss), foreach(X, Col), param(J) do
            nth1(J, XRow, X)
        ),
        sum(Col) #>= 0
    ).
