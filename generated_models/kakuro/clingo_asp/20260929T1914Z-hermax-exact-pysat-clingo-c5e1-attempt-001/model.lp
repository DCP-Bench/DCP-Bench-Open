% Kakuro: put a digit 1..9 in each white cell so that every entry (a run of
% cells across or down) adds up to its clue and no digit repeats within an
% entry. Blank cells hold 0 in the answer.
% problem(K, 0, Clue) is the clue of entry K and problem(K, J, 0, R), problem(K, J, 1, C)
% the row and column (counted from 1) of its J-th cell; blanks(I, 0, R), blanks(I, 1, C)
% are the blank cells.
index(0..N-1) :- n(N).

% x(R, C, V): the digit in cell (R, C), or 0 for a blank cell.
1 { x(R,C,V) : V = 0..9 } 1 :- index(R), index(C).

% Blank cells are 0.
:- blanks(I,0,R), blanks(I,1,C), not x(R-1,C-1,0).

% in_entry(K, R, C): cell (R, C) belongs to entry K (0-based here).
in_entry(K,R-1,C-1) :- problem(K,J,0,R), problem(K,J,1,C).

% The cells of an entry hold real digits, 1 to 9.
:- in_entry(K,R,C), x(R,C,0).
% The digits of the entry add up to its clue.
:- problem(K,0,Clue), Clue != #sum { V,R,C : in_entry(K,R,C), x(R,C,V) }.
% No digit is repeated within an entry.
:- in_entry(K,R1,C1), in_entry(K,R2,C2), (R1,C1) < (R2,C2), x(R1,C1,V), x(R2,C2,V).

#show x/3.
