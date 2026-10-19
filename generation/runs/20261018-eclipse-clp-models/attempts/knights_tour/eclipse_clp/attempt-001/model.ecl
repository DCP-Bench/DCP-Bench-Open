% Knight's tour on an n x n chessboard, n read from the instance.
% A knight's tour is a sequence of knight moves that visits every square exactly once,
% without returning to the starting square. x[i][j] is the move number (0-based) of square (i,j).
%
% Encoding: the path is a circuit over the squares plus one extra node (Dummy) that closes
% the open path into a cycle. Succ[P] is the square visited after square P (1-based index),
% Ord[P] is the move number of square P (0-based).

:- lib(ic).
:- lib(listut).

model(Instance, Succ, [x-Rows], none) :-
    memberchk(n-N, Instance),
    N2 is N * N,
    Dummy is N2 + 1,
    M1 is N2 - 1,
    length(CellSucc, N2),
    append(CellSucc, [DSucc], Succ),
    length(CellOrd, N2),
    OrdD :: 0..N2,
    append(CellOrd, [OrdD], OrdAll),
    Succ :: 1..Dummy,
    CellOrd :: 0..M1,
    DSucc #\= Dummy,

    % the successor of a square is a square a knight move away, or the dummy node
    % (the tour ends there); no square is its own successor
    ( for(P, 0, N2 - 1), param(N, CellSucc, CellOrd, OrdAll) do
        knight_nbrs(N, P, Nbrs),
        nth0(P, CellSucc, S),
        S :: Nbrs,
        S #\= P + 1,
        % the move number increases by one from a square to its successor
        nth0(P, CellOrd, O),
        V #= O + 1,
        element(S, OrdAll, V)
    ),

    % the path visits every square exactly once: the successors form one circuit with the dummy node
    circuit(Succ),

    % the first square of the tour is the successor of the dummy node and has move number 0
    element(DSucc, OrdAll, 0),

    % every square gets a different move number
    alldifferent(CellOrd),

    split_rows(N, CellOrd, Rows).

% the square indices (1-based) a knight move away from square P (0-based), plus the dummy node
knight_nbrs(N, P, Nbrs) :-
    R is P // N,
    C is P mod N,
    N2 is N * N,
    D is N2 + 1,
    findall(Q,
            ( member(d(DR, DC), [d(1,2), d(2,1), d(-1,2), d(-2,1), d(1,-2), d(2,-1), d(-1,-2), d(-2,-1)]),
              R2 is R + DR, C2 is C + DC,
              R2 >= 0, R2 < N, C2 >= 0, C2 < N,
              Q is R2 * N + C2 + 1
            ), Qs),
    append(Qs, [D], Nbrs).

% split a flat list of N*N move numbers into N rows of N
split_rows(N, L, [R|Rs]) :-
    length(R, N),
    append(R, Rest, L),
    split_rows(N, Rest, Rs).
split_rows(_, [], []).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
