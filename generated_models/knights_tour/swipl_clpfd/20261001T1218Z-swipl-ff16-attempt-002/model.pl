:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(pairs)).
:- use_module(library(yall)).

% Knight's tour: number the squares of an n x n board 0..n*n-1 so that
% consecutive numbers are one knight's move apart. The knight visits every
% square once and need not return to the square it started from.
model(Instance, Choices, [x-Rows]) :-
    N = Instance.n,                         % size of the board
    Squares is N * N,
    Dummy is Squares + 1,                   % an extra node, explained below
    Last is Squares - 1,
    numlist(1, Squares, SquareIds),

    % Square (i, j), counted from 0, is node i*N + j + 1. A tour is a path
    % through all squares, which is written as a circuit through the squares
    % and one extra node: the extra node is followed by the first square of
    % the tour and comes after the last one.
    % Successors[v] is the node visited after node v. From a square the knight
    % goes to a square one knight's move away, or to the extra node when the
    % square is the last of the tour; the extra node leads to any square.
    maplist(knight_moves(N), SquareIds, Moves),

    % How the search picks a successor: Choices[v] is a place in the list of
    % nodes that can follow v. The list puts the squares with the fewest
    % knight's moves first (they are the hardest to reach later, so they are
    % best visited early) and the extra node last. Trying small places first
    % follows this rule.
    maplist({Moves, Dummy}/[Targets, Candidates]>>candidates(Moves, Targets, Dummy, Candidates),
            Moves, SquareCandidates),
    numlist(1, Squares, AnySquare),
    candidates(Moves, AnySquare, none, StartCandidates),
    append(SquareCandidates, [StartCandidates], AllCandidates),
    maplist([Candidates, Choice, Next]>>
                (length(Candidates, Count), Choice in 1..Count,
                 element(Choice, Candidates, Next)),
            AllCandidates, Choices, Successors),
    % every node is left once, entered once, and the path closes into a
    % single circuit; this also means every square is visited once
    circuit(Successors),

    % Rows[i][j] is the move number (0 for the first square) of square (i, j).
    length(Rows, N),
    maplist({N}/[Row]>>length(Row, N), Rows),
    append(Rows, Numbers),
    Numbers ins 0..Last,
    % the numbers follow the path: the extra node counts as -1, so the first
    % square gets 0, and every move to a square adds one. The numbers are
    % determined by Successors and are not labelled.
    append(Numbers, [-1], AllNumbers),
    maplist({AllNumbers, Dummy}/[Next, Number]>>number_step(AllNumbers, Dummy, Next, Number),
            Successors, AllNumbers).

% candidates(+Moves, +Targets, +Dummy, -Candidates): the nodes in Targets ordered
% by how few knight's moves they have, fewest first, followed by Dummy (unless
% it is none).
candidates(Moves, Targets, Dummy, Candidates) :-
    maplist({Moves}/[Target, Count-Target]>>(nth1(Target, Moves, Onward), length(Onward, Count)),
            Targets, Counted),
    keysort(Counted, Sorted),
    pairs_values(Sorted, Ordered),
    (   Dummy == none
    ->  Candidates = Ordered
    ;   append(Ordered, [Dummy], Candidates)
    ).

% number_step(+AllNumbers, +Dummy, +Next, +Number): the node Next follows a node
% numbered Number; unless it is the extra node it is numbered one higher.
number_step(AllNumbers, Dummy, Next, Number) :-
    element(Next, AllNumbers, NextNumber),
    (Next #\= Dummy) #==> (NextNumber #= Number + 1).

% knight_moves(+N, +Square, -Targets): the squares of an N x N board a knight
% reaches from Square in one move (two squares along one direction and one
% along the other; these eight moves belong to chess, not to the instance).
knight_moves(N, Square, Targets) :-
    I is (Square - 1) // N,
    J is (Square - 1) mod N,
    findall(Target,
            (   member([DI, DJ],
                       [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]]),
                I2 is I + DI, J2 is J + DJ,
                I2 >= 0, I2 < N, J2 >= 0, J2 < N,
                Target is I2 * N + J2 + 1
            ),
            Targets).
