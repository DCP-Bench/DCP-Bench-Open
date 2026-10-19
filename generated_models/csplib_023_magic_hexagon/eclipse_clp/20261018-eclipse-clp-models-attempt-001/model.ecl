% Magic hexagon (CSPLib 023): place the numbers 1..NUM_CELLS on the cells A..S of
% a hexagon with rows of 3, 4, 5, 4 and 3 cells, so that the sum of the numbers
% in each of the 15 lines (rows and diagonals) equals the magic constant MAGIC_SUM.
% Output LD lists the values of A, B, ..., S in that order.

:- lib(ic).

model(Instance, Vars, ['LD'-Vars], none) :-
    memberchk('NUM_CELLS'-Cells, Instance),
    memberchk('MAGIC_SUM'-Magic, Instance),
    Vars = [A,B,C,D,E,F,G,H,I,J,K,L,M,Nn,O,P,Q,R,S],
    length(Vars, Cells),
    Vars :: 1..Cells,

    % all numbers of the hexagon are different
    alldifferent(Vars),

    % the sum of the numbers in each of the 5 horizontal rows is the magic constant
    A + B + C #= Magic,
    D + E + F + G #= Magic,
    H + I + J + K + L #= Magic,
    M + Nn + O + P #= Magic,
    Q + R + S #= Magic,

    % the sum of the numbers in each of the 5 diagonals from upper left to lower right is the magic constant
    A + E + J + O + S #= Magic,
    B + F + K + P #= Magic,
    C + G + L #= Magic,
    D + I + Nn + R #= Magic,
    H + M + Q #= Magic,

    % the sum of the numbers in each of the 5 diagonals from upper right to lower left is the magic constant
    C + F + J + Nn + Q #= Magic,
    B + E + I + M #= Magic,
    A + D + H #= Magic,
    G + K + O + R #= Magic,
    L + P + S #= Magic.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
