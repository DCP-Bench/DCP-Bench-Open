% N-queens (csplib 054): place n queens on an n x n chessboard so that no two
% queens attack each other, i.e. no two share a row, column or diagonal.
% queens[i] is the column (1..n) of the queen in row i.

:- lib(ic).

model(Instance, Queens, [queens-Queens], none) :-
    memberchk(n-N, Instance),
    length(Queens, N),
    Queens :: 1..N,
    safe_placement(Queens).

search_goal(Queens) :-
    search(Queens, 0, first_fail, indomain_min, complete, []).

% no two queens on the same column, and no two queens on the same diagonal
% (the queens sit on different rows by construction, one per array position)
safe_placement([]).
safe_placement([Q|Qs]) :-
    safe_from(Q, Qs, 1),
    safe_placement(Qs).

% the queen in row i and the queen in row i+D: different columns, and the
% column distance differs from the row distance D
safe_from(_, [], _).
safe_from(Q, [R|Rs], D) :-
    Q #\= R,
    Q #\= R + D,
    Q #\= R - D,
    D1 is D + 1,
    safe_from(Q, Rs, D1).
