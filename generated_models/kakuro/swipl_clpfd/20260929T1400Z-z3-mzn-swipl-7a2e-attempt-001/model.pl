:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
% cells across or down) adds up to its clue and no digit repeats within an
% entry. Blank cells hold 0 in the answer.
model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,                 % side of the grid
    Entries = Instance.problem,     % [Clue, [Row, Col], [Row, Col], ...] with cells counted from 1
    Blanks = Instance.blanks,       % [Row, Col] of the cells that are blank

    % Rows[r][c] = digit in cell (r, c), or 0 for a blank cell
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..9), Rows),

    % blank cells are 0
    maplist({Rows}/[[R, C]]>>(nth1(R, Rows, Row), nth1(C, Row, 0)), Blanks),

    maplist({Rows}/[[Clue|Cells]]>>(
                maplist({Rows}/[[R, C], Cell]>>(nth1(R, Rows, Row), nth1(C, Row, Cell)), Cells, Run),
                % the cells of an entry hold real digits, 1 to 9
                Run ins 1..9,
                % the digits of the entry add up to its clue
                sum(Run, #=, Clue),
                % no digit is repeated within an entry
                all_distinct(Run)), Entries),
    append(Rows, Vars).
