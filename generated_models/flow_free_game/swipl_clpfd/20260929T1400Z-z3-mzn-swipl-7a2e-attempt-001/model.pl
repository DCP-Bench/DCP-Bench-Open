:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Flow Free: colour every cell of the board so that each colour forms one pipe
% joining its two given end cells, the pipes do not cross or overlap, and the
% whole board is covered. A pipe is a chain of orthogonally adjacent cells of
% one colour.
model(Instance, Vars, ['B'-Rows]) :-
    Board = Instance.board,    % colour of each end cell, 0 for a cell to fill
    length(Board, NRows),
    Board = [FirstRow|_],
    length(FirstRow, NCols),
    append(Board, AllColours),
    max_list(AllColours, NColours),   % colours are numbered 1..NColours

    % Rows[i][j] = colour of cell (i, j)
    length(Rows, NRows),
    maplist({NCols, NColours}/[Row]>>(length(Row, NCols), Row ins 1..NColours), Rows),

    % the end cells with their colours (0 marks a cell to fill), as ground data
    findall(R-C-Colour, (nth1(R, Board, BoardRow), nth1(C, BoardRow, Colour)), Cells),
    maplist({Rows, NRows, NCols}/[R-C-Colour]>>(
                nth1(R, Rows, Row), nth1(C, Row, Cell),
                findall(A-B, (member(DA-DB, [-1-0, 1-0, 0-(-1), 0-1]), A is R + DA, B is C + DB,
                              A >= 1, A =< NRows, B >= 1, B =< NCols), Around),
                maplist({Rows, Cell}/[A-B, Same]>>(nth1(A, Rows, RowA), nth1(B, RowA, Other), Same #<==> (Cell #= Other)),
                        Around, Sames),
                ( Colour =\= 0
                ->  % an end cell has its given colour and joins exactly one neighbour of that colour
                    Cell #= Colour,
                    sum(Sames, #=, 1)
                ;   % a cell in the middle of a pipe joins exactly two neighbours of its colour
                    sum(Sames, #=, 2)
                )), Cells),
    append(Rows, Vars).
