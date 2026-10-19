% Sudoku: fill a 9x9 grid with numbers so that each row, column and 3x3 section
% contains all the digits between 1 and 9. The input grid holds some filled cells
% (digits 1 to 9) and some empty cells (0). The solved grid is the output grid.

:- lib(gfd).
:- lib(listut).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

model(Instance, Vars, [grid-Rows], none) :-
    memberchk(input_grid-Clues, Instance),
    % Nine rows of nine cells, each cell a digit between 1 and 9.
    length(Rows, 9),
    ( foreach(R, Rows) do length(R, 9), R :: 1..9 ),
    flatten(Rows, Vars),
    % Each row contains all the digits between 1 and 9.
    ( foreach(R, Rows) do alldifferent(R) ),
    % Each column contains all the digits between 1 and 9.
    ( for(J, 1, 9), param(Rows) do
        column(Rows, J, Col),
        alldifferent(Col)
    ),
    % Each 3x3 section contains all the digits between 1 and 9.
    ( foreach(BI, [0,1,2]), param(Rows) do
        ( foreach(BJ, [0,1,2]), param(Rows, BI) do
            section_cells(Rows, BI, BJ, Cells),
            alldifferent(Cells)
        )
    ),
    % The filled cells of the input grid keep their digits.
    ( foreach(CR, Clues), foreach(R, Rows) do
        ( foreach(C, CR), foreach(X, R) do
            ( C =:= 0 -> true ; X #= C )
        )
    ).

column(Rows, J, Col) :-
    ( foreach(R, Rows), foreach(X, Col), param(J) do
        nth1(J, R, X)
    ).

section_cells(Rows, BI, BJ, Cells) :-
    findall(I-J, (member(DI, [1,2,3]), member(DJ, [1,2,3]),
                  I is 3*BI+DI, J is 3*BJ+DJ), Pos),
    ( foreach(I-J, Pos), foreach(X, Cells), param(Rows) do
        cell(Rows, I, J, X)
    ).

cell(Rows, I, J, X) :-
    nth1(I, Rows, R),
    nth1(J, R, X).
