% Calvin puzzle on an n by n grid (n from the instance).
% Fill the n^2 squares with the numbers 1..n^2, each used once.
% Type I: the next number is placed horizontally or vertically, exactly three
%         squares away from the previous number (two squares gap).
% Type II: the next number is placed diagonally, exactly two squares away
%          from the previous number (one square gap).
% Output x: the completed grid as a list of rows.

:- lib(ic).

model(Instance, Vars, [x-Grid]) :-
    memberchk(n-N, Instance),
    NN is N * N,

    % To take an n by n grid, representing n^2 squares, and completely fill
    % every square with the numbers 1..n^2, each used once.
    % The grid, row-major: cell (R,C) is Cells[(R-1)*N + C].
    length(Cells, NN),
    Cells :: 1..NN,
    alldifferent(Cells),

    % Number V sits in row Rs[V], column Cs[V], flat index Ps[V].
    length(Rs, NN),
    length(Cs, NN),
    length(Ps, NN),
    Rs :: 1..N,
    Cs :: 1..N,
    Ps :: 1..NN,
    alldifferent(Ps),
    ( foreach(P, Ps), foreach(R, Rs), foreach(C, Cs), param(N) do
        P #= (R - 1) * N + C
    ),
    ( foreach(P, Ps), count(V, 1, _), param(Cells) do
        element(P, Cells, V)
    ),

    % If the next number in the sequence is going to be placed vertically or
    % horizontally, it must be placed exactly three squares away from the
    % previous number. If it is placed diagonally, it must be placed exactly
    % two squares away from the previous number.
    moves(Rs, Cs),

    % Search follows the numbers in order: row and column of 1, 2, 3, ...
    interleave(Rs, Cs, Vars),

    chunks(Cells, N, Grid).

moves([_], [_]).
moves([R1, R2 | Rs], [C1, C2 | Cs]) :-
    move(R1, C1, R2, C2),
    moves([R2 | Rs], [C2 | Cs]).

move(R1, C1, R2, C2) :-
    (   (abs(R1 - R2) #= 3 and C1 #= C2)
    or  (R1 #= R2 and abs(C1 - C2) #= 3)
    or  (abs(R1 - R2) #= 2 and abs(C1 - C2) #= 2)
    ).

interleave([], [], []).
interleave([R | Rs], [C | Cs], [R, C | Vs]) :-
    interleave(Rs, Cs, Vs).

% Split the flat list into rows of length N.
chunks([], _, []).
chunks(L, N, [R | Rs]) :-
    length(R, N),
    append(R, Rest, L),
    chunks(Rest, N, Rs).

search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).
