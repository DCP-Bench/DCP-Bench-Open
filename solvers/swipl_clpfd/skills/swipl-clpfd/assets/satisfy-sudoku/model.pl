% 4x4 Sudoku: find one grid that satisfies the rules.
% Shows: a matrix of finite-domain variables, all_distinct/1 on rows, columns and
% boxes, givens posted as constraints, and labelling of one solution.
:- use_module(library(clpfd)).
:- initialization(main, main).

% 0 marks an empty cell.
puzzle([[1,0,0,0],
        [0,0,3,0],
        [0,4,0,0],
        [0,0,0,2]]).

sudoku(Rows) :-
    puzzle(Puzzle),
    length(Puzzle, N),
    length(Rows, N),
    maplist({N}/[Row]>>length(Row, N), Rows),
    append(Rows, Cells),
    Cells ins 1..N,
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    boxes(Rows, Boxes),
    maplist(all_distinct, Boxes),
    maplist(maplist(given), Puzzle, Rows).

% A given cell is fixed to its digit; an empty cell stays free.
given(0, _) :- !.
given(Digit, Cell) :- Cell #= Digit.

% The four 2x2 boxes of a 4x4 grid.
boxes([[A1,A2,A3,A4],[B1,B2,B3,B4],[C1,C2,C3,C4],[D1,D2,D3,D4]],
      [[A1,A2,B1,B2],[A3,A4,B3,B4],[C1,C2,D1,D2],[C3,C4,D3,D4]]).

main :-
    sudoku(Rows),
    append(Rows, Cells),
    once(labeling([ff], Cells)),
    maplist(print_row, Rows).

print_row(Row) :-
    atomic_list_concat(Row, ' ', Line),
    writeln(Line).
