:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Flip rows and columns (Einav's puzzle): choose, for every row and column,
% whether to flip its sign so that every row sum and every column sum is
% non-negative, with the smallest possible total of the whole matrix.
model(Instance, Vars, [row_signs-RowSigns, col_signs-ColSigns], min(Total)) :-
    Matrix = Instance.input_matrix,
    length(Matrix, Rows),
    Matrix = [FirstRow|_],
    length(FirstRow, Cols),

    % the signs of the rows and columns: -1 (flipped) or +1, never 0
    length(RowSigns, Rows),
    RowSigns ins -1 \/ 1,
    length(ColSigns, Cols),
    ColSigns ins -1 \/ 1,

    % Signs[i][j] = sign of cell (i, j) after both flips = row sign * column sign
    maplist({ColSigns}/[RowSign, SignRow]>>maplist({RowSign}/[ColSign, Sign]>>(Sign #= RowSign * ColSign),
                                                  ColSigns, SignRow), RowSigns, Signs),

    % every row and column sums to at least 0; the reference's declared
    % domain for a sum is 0..300, which is mirrored here
    maplist([SignRow, MatrixRow]>>(RowSum in 0..300, scalar_product(MatrixRow, SignRow, #=, RowSum)),
            Signs, Matrix),
    transpose(Signs, SignColumns),
    transpose(Matrix, MatrixColumns),
    maplist([SignColumn, MatrixColumn]>>(ColumnSum in 0..300, scalar_product(MatrixColumn, SignColumn, #=, ColumnSum)),
            SignColumns, MatrixColumns),

    % total sum of the flipped matrix, to be minimised (declared range 0..1000)
    append(Signs, FlatSigns),
    append(Matrix, FlatMatrix),
    Total in 0..1000,
    scalar_product(FlatMatrix, FlatSigns, #=, Total),
    append([RowSigns, ColSigns, FlatSigns, [Total]], Vars).

% Branch on the variable that constrains the most others, and try +1 before -1:
% with the default order the search needs far longer to prove the optimum.
labeling_options([ffc, down]).
